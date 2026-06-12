"""
ms-momentum-score SYMBOL [SYMBOL ...] [--exclude-last 21] [--pretty]

Computes raw and volatility-adjusted price momentum for NSE/BSE symbols over
standard Dual Momentum lookback windows (1M / 3M / 6M / 12M / 12-1M).

  --exclude-last  Bars to exclude from the 12-month tail (default 21 = 1 month).
                  The 12-1M formulation skips the most recent month to avoid the
                  short-term reversal effect (Jegadeesh & Titman, 1993).
  --pretty        Render a Rich table instead of raw JSON.

Live data only — no training-knowledge values are ever used.
"""

from __future__ import annotations

import json
import time
from datetime import date
from typing import Optional

import typer
import yfinance as yf
from rich.console import Console
from rich.table import Table

from market_sage._utils import _nse, _period_return

app = typer.Typer(add_completion=False)
console = Console()


# ── Pure-math helpers ────────────────────────────────────────────────────────

def _daily_returns(closes: list[float]) -> list[float]:
    """Single-pass daily log-price returns as decimals."""
    if len(closes) < 2:
        return []
    return [(closes[i] / closes[i - 1]) - 1.0 for i in range(1, len(closes))]


def _annualized_vol(daily_returns: list[float]) -> float:
    """Population standard deviation of daily returns, annualised by sqrt(252).

    Uses population std (divide by N) consistent with academic momentum literature.
    """
    n = len(daily_returns)
    if n < 2:
        return 0.0
    mean = sum(daily_returns) / n
    variance = sum((r - mean) ** 2 for r in daily_returns) / n
    return round((variance ** 0.5) * (252 ** 0.5), 4)


# ── Core compute ─────────────────────────────────────────────────────────────

def _momentum_score(symbol: str, exclude_last: int = 21) -> dict:
    """Fetch 14 months of daily OHLCV and compute momentum metrics.

    Returns a structured dict. On failure, returns {"symbol": ..., "error": ...}.
    The 12-1M calculation skips `exclude_last` bars from the tail so it measures
    the 11-month period ending one month ago — the canonical academic signal.
    """
    ticker = _nse(symbol)
    t = yf.Ticker(ticker)

    try:
        hist = t.history(period="14mo")
    except Exception as exc:
        return {"symbol": symbol.upper(), "ticker": ticker, "error": f"fetch_failed: {exc}"}

    if hist is None or hist.empty:
        return {"symbol": symbol.upper(), "ticker": ticker, "error": "no_data"}

    hist = hist.dropna(subset=["Close"])
    if hist.empty:
        return {"symbol": symbol.upper(), "ticker": ticker, "error": "no_data_after_dropna"}

    closes = hist["Close"].tolist()

    if len(closes) < 252:
        return {
            "symbol": symbol.upper(),
            "ticker": ticker,
            "error": "insufficient_data",
            "bars_available": len(closes),
            "bars_required": 252,
        }

    # Standard lookbacks in trading days
    ret_1m  = _period_return(closes, 21)
    ret_3m  = _period_return(closes, 63)
    ret_6m  = _period_return(closes, 126)
    ret_12m = _period_return(closes, 252)

    # 12-1M: exclude the last `exclude_last` bars (avoids short-term reversal)
    # Need closes[:-exclude_last] and at least 252-exclude_last bars in the trimmed series
    trimmed = closes[:-exclude_last] if exclude_last > 0 else closes
    ret_12_1m = _period_return(trimmed, 252 - exclude_last) if len(trimmed) >= 252 else None

    daily_rets = _daily_returns(closes[-252:])
    ann_vol = _annualized_vol(daily_rets)
    vol_adj = round(ret_12_1m / ann_vol, 3) if (ret_12_1m is not None and ann_vol > 0) else None

    return {
        "symbol": symbol.upper(),
        "ticker": ticker,
        "returns": {
            "1m":    ret_1m,
            "3m":    ret_3m,
            "6m":    ret_6m,
            "12m":   ret_12m,
            "12_1m": ret_12_1m,
        },
        "annualized_vol": ann_vol,
        "vol_adjusted_momentum": vol_adj,
        # Populated by ms-momentum-screen orchestrator when ranking within a universe
        "momentum_rank_pct": None,
        "source_date": date.today().isoformat(),
    }


def analyze(symbols: list[str], exclude_last: int = 21) -> list[dict]:
    """Compute momentum scores for multiple symbols with rate-limit sleep between calls."""
    results: list[dict] = []
    for i, sym in enumerate(symbols):
        if i > 0:
            time.sleep(1.5)
        results.append(_momentum_score(sym, exclude_last=exclude_last))
    return results


# ── Pretty renderer ──────────────────────────────────────────────────────────

def _pct(v: float | None) -> str:
    if v is None:
        return "—"
    colour = "green" if v >= 0 else "red"
    return f"[{colour}]{v * 100:+.1f}%[/{colour}]"


def _flt(v: float | None) -> str:
    return f"{v:.2f}" if v is not None else "—"


def _render_pretty(results: list[dict]) -> None:
    tbl = Table(title="Momentum Score", show_header=True, header_style="bold cyan")
    tbl.add_column("Symbol", style="bold")
    tbl.add_column("1M%", justify="right")
    tbl.add_column("3M%", justify="right")
    tbl.add_column("6M%", justify="right")
    tbl.add_column("12M%", justify="right")
    tbl.add_column("12-1M%", justify="right")
    tbl.add_column("Ann.Vol", justify="right")
    tbl.add_column("Vol-Adj Score", justify="right")

    for r in results:
        if "error" in r:
            tbl.add_row(
                r.get("symbol", "?"),
                f"[red]ERR: {r['error']}[/red]", "", "", "", "", "", "",
            )
            continue

        ret = r.get("returns", {})
        vol_adj = r.get("vol_adjusted_momentum")
        va_str = (
            f"[green]{vol_adj:.2f}[/green]" if vol_adj is not None and vol_adj >= 0
            else (f"[red]{vol_adj:.2f}[/red]" if vol_adj is not None else "—")
        )

        tbl.add_row(
            r.get("symbol", "?"),
            _pct(ret.get("1m")),
            _pct(ret.get("3m")),
            _pct(ret.get("6m")),
            _pct(ret.get("12m")),
            _pct(ret.get("12_1m")),
            _flt(r.get("annualized_vol")),
            va_str,
        )

    console.print(tbl)
    console.print(f"[dim]Source: yfinance | Date: {date.today().isoformat()}[/dim]")


# ── CLI ───────────────────────────────────────────────────────────────────────

@app.command()
def main(
    symbols: list[str] = typer.Argument(..., help="One or more NSE symbols (e.g. KAYNES HDFCBANK)"),
    exclude_last: int = typer.Option(21, "--exclude-last", help="Bars to skip from 12M tail for 12-1M calculation"),
    pretty: bool = typer.Option(False, "--pretty", help="Render a Rich table"),
) -> None:
    """Compute raw and volatility-adjusted price momentum."""
    results = analyze(symbols, exclude_last=exclude_last)
    if pretty:
        _render_pretty(results)
    else:
        console.print(json.dumps(results if len(results) > 1 else results[0], indent=2))
