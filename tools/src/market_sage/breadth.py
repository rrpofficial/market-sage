"""
ms-breadth [--index NIFTY500] [--pretty]

Indian market breadth tool — computes the go/no-go signal that gates all
momentum entry decisions.

Breadth metrics (all computed from live yfinance data, never from training memory):
  % of index stocks above 200 DMA → market regime (Bullish / Neutral / Bearish)
  % of index stocks above 50 DMA
  New 52W highs vs lows (stocks within 2% of 52W boundary)
  Advance/Decline ratio for the most recent session
  Nifty 50 index vs its own 200 DMA

  --index   NSE index to scan (NIFTY500, NIFTY50, NIFTY100, NIFTYMIDCAP150). Default: NIFTY500.
  --pretty  Render coloured Rich output instead of raw JSON.

Runtime: NIFTY50 ≈ 3-10 seconds; NIFTY500 ≈ 30-90 seconds.
Live data only — no training-knowledge values are ever used.
"""

from __future__ import annotations

import json
from datetime import date

import sys

import typer
import yfinance as yf
from rich import box
from rich.console import Console
from rich.table import Table

from market_sage._utils import _batch_download, _get_universe

app = typer.Typer(add_completion=False)
console = Console()
_err = Console(stderr=True)  # status/progress messages go to stderr, not stdout


# ── Pure-math helpers ────────────────────────────────────────────────────────

def _compute_200dma(closes: list[float]) -> float | None:
    """200-bar simple arithmetic mean. Returns None when fewer than 200 bars available."""
    if len(closes) < 200:
        return None
    return sum(closes[-200:]) / 200


def _compute_50dma(closes: list[float]) -> float | None:
    """50-bar simple arithmetic mean. Returns None when fewer than 50 bars available."""
    if len(closes) < 50:
        return None
    return sum(closes[-50:]) / 50


# ── Core breadth computation ─────────────────────────────────────────────────

def _compute_breadth(tickers: list[str]) -> dict:
    """Compute market breadth for a list of NSE symbols.

    Single yf.download() batch call via _batch_download (from _utils).
    All arithmetic is pure Python — no numpy / scipy.
    """
    all_closes = _batch_download(tickers, period="14mo")  # 14mo guarantees >= 252 bars

    if not all_closes:
        return {
            "error": "batch_download_failed",
            "total_stocks": 0,
            "above_200dma": 0,
            "pct_above_200dma": 0.0,
            "above_50dma": 0,
            "pct_above_50dma": 0.0,
            "new_52w_highs": 0,
            "new_52w_lows": 0,
            "ad_ratio_today": 1.0,
            "market_regime": "Unknown",
            "momentum_go": False,
        }

    above_200 = 0
    above_50  = 0
    new_highs = 0
    new_lows  = 0
    advances  = 0
    declines  = 0

    for _sym, closes in all_closes.items():
        if len(closes) < 200:
            continue

        dma_200 = sum(closes[-200:]) / 200
        dma_50  = sum(closes[-50:]) / 50 if len(closes) >= 50 else None

        w52_high = max(closes[-252:]) if len(closes) >= 252 else max(closes)
        w52_low  = min(closes[-252:]) if len(closes) >= 252 else min(closes)

        if closes[-1] > dma_200:
            above_200 += 1
        if dma_50 is not None and closes[-1] > dma_50:
            above_50 += 1
        # "New high" = within 2% of 52W high; "new low" = within 2% of 52W low
        if closes[-1] >= w52_high * 0.98:
            new_highs += 1
        if closes[-1] <= w52_low * 1.02:
            new_lows += 1

        # Single-session A/D: compare last close vs previous close
        if len(closes) >= 2:
            if closes[-1] > closes[-2]:
                advances += 1
            elif closes[-1] < closes[-2]:
                declines += 1

    total = len(all_closes)
    pct_200 = round(above_200 / total * 100, 1) if total else 0.0
    pct_50  = round(above_50  / total * 100, 1) if total else 0.0
    ad_ratio = round(advances / declines, 2) if declines else (999.0 if advances else 1.0)

    if pct_200 > 60:
        regime = "Bullish"
    elif pct_200 < 40:
        regime = "Bearish"
    else:
        regime = "Neutral"

    return {
        "total_stocks": total,
        "above_200dma": above_200,
        "pct_above_200dma": pct_200,
        "above_50dma": above_50,
        "pct_above_50dma": pct_50,
        "new_52w_highs": new_highs,
        "new_52w_lows": new_lows,
        "ad_ratio_today": ad_ratio,
        "market_regime": regime,
        "momentum_go": pct_200 >= 50,
    }


# ── Public interface ─────────────────────────────────────────────────────────

def analyze(index: str = "NIFTY500") -> dict:
    """Compute full market breadth for the named NSE index.

    Additionally fetches the Nifty 50 index benchmark (^NSEI) to check whether
    the market-wide trend is itself intact (price above its own 200 DMA).
    """
    tickers = _get_universe(index)
    _err.print(
        f"[dim]Fetching {len(tickers)} tickers ({index}) from yfinance — "
        f"may take {'3-10s' if len(tickers) <= 60 else '30-90s'}...[/dim]",
        highlight=False,
    )

    breadth = _compute_breadth(tickers)
    breadth["index"] = index.upper()

    # Nifty 50 benchmark vs its own 200 DMA
    nifty50_vs_200: str | None = None
    try:
        nifty_hist = yf.Ticker("^NSEI").history(period="14mo")
        if nifty_hist is not None and not nifty_hist.empty:
            nifty_closes = nifty_hist["Close"].dropna().tolist()
            if len(nifty_closes) >= 200:
                dma_200 = sum(nifty_closes[-200:]) / 200
                nifty50_vs_200 = "above" if nifty_closes[-1] > dma_200 else "below"
    except Exception:
        pass

    breadth["nifty50_vs_200dma"] = nifty50_vs_200
    breadth["source_date"] = date.today().isoformat()
    return breadth


# ── Pretty renderer ──────────────────────────────────────────────────────────

def _render_pretty(data: dict) -> None:
    regime = data.get("market_regime", "Unknown")
    regime_colour = {"Bullish": "green", "Neutral": "yellow", "Bearish": "red"}.get(regime, "white")
    index_name = data.get("index", "")
    total = data.get("total_stocks", 0)

    console.print()
    console.print(
        f"[bold {regime_colour}]MARKET REGIME: {regime.upper()}[/bold {regime_colour}]  "
        f"[dim]({index_name} — {total} stocks scanned)[/dim]"
    )

    tbl = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan", pad_edge=False)
    tbl.add_column("Metric",            style="bold", width=28)
    tbl.add_column("Value",             justify="right", width=10)
    tbl.add_column("Signal",            width=30)

    pct_200  = data.get("pct_above_200dma", 0.0)
    pct_50   = data.get("pct_above_50dma",  0.0)
    highs    = data.get("new_52w_highs",    0)
    lows     = data.get("new_52w_lows",     0)
    ad       = data.get("ad_ratio_today",   1.0)
    nifty_vs = data.get("nifty50_vs_200dma") or "unknown"

    def _pct_signal(pct: float, bull: float, bear: float) -> str:
        if pct > bull:
            return f"[green]Bullish (> {bull:.0f}%)[/green]"
        if pct < bear:
            return f"[red]Bearish (< {bear:.0f}%)[/red]"
        return "[yellow]Neutral[/yellow]"

    tbl.add_row("% Above 200 DMA", f"{pct_200:.1f}%", _pct_signal(pct_200, 60, 40))
    tbl.add_row("% Above 50 DMA",  f"{pct_50:.1f}%",  _pct_signal(pct_50,  55, 35))
    hl_signal = (
        "[green]Highs dominating[/green]" if highs > lows
        else ("[red]Lows dominating[/red]" if lows > highs else "[yellow]Even[/yellow]")
    )
    tbl.add_row("New 52W Highs",      str(highs), hl_signal)
    tbl.add_row("New 52W Lows",       str(lows), "")
    ad_signal = (
        "[green]Broad advance[/green]" if ad > 1.2
        else ("[red]Broad decline[/red]" if ad < 0.8 else "[yellow]Mixed[/yellow]")
    )
    tbl.add_row("A/D Ratio (today)", f"{ad:.2f}", ad_signal)
    nv_colour = "green" if nifty_vs == "above" else ("red" if nifty_vs == "below" else "dim")
    tbl.add_row("Nifty 50 vs 200 DMA", nifty_vs.upper(), f"[{nv_colour}]{nifty_vs}[/{nv_colour}]")

    console.print(tbl)

    # Recommendation
    if data.get("momentum_go") and regime == "Bullish":
        console.print("[green]✓ Market conditions support momentum entries[/green]")
    elif regime == "Neutral":
        console.print("[yellow]⚠ Proceed selectively — market is mixed[/yellow]")
    else:
        console.print("[red]✗ Avoid new momentum entries — breadth is deteriorating[/red]")

    console.print(f"[dim]Source: yfinance | Date: {data.get('source_date', '?')}[/dim]")


# ── CLI ───────────────────────────────────────────────────────────────────────

@app.command()
def main(
    index: str = typer.Option(
        "NIFTY500",
        "--index",
        help="Index to scan: NIFTY500, NIFTY50, NIFTY100, NIFTYMIDCAP150",
    ),
    pretty: bool = typer.Option(False, "--pretty", help="Render coloured Rich output"),
) -> None:
    """Indian market breadth — go/no-go signal for momentum entries.

    NIFTY50 scan takes 3-10 seconds. NIFTY500 scan takes 30-90 seconds.
    """
    data = analyze(index=index)
    if pretty:
        _render_pretty(data)
    else:
        console.print(json.dumps(data, indent=2))
