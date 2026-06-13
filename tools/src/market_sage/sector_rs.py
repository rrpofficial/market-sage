"""
ms-sector-rs [--period 63] [--pretty]

Ranks NSE sectoral indices by relative strength vs Nifty 50 and classifies
them into Relative Rotation Graph (RRG) quadrants:
  Leading   — strong RS + improving momentum  → offensive allocation
  Weakening — strong RS + declining momentum  → rotate out
  Improving — weak RS   + improving momentum  → early rotation buy
  Lagging   — weak RS   + declining momentum  → avoid

  --period  Lookback in trading days for RS comparison (default 63 = ~3 months).
  --pretty  Render a Rich table sorted by RS, quadrant colour-coded.

Runtime: ~10-20 seconds (13 tickers to download).
Live data only — no training-knowledge values are ever used.
"""

from __future__ import annotations

import json
from datetime import date
from typing import Optional

import typer
import yfinance as yf
from rich import box
from rich.console import Console
from rich.table import Table

app = typer.Typer(add_completion=False)
console = Console()
_err = Console(stderr=True)  # status/progress messages go to stderr, not stdout

# ── Sector index registry ────────────────────────────────────────────────────
# yfinance tickers validated against live data (June 2026).
# Any ticker that fails to return data is silently skipped; the tool degrades
# gracefully rather than crashing. Substitutions are noted inline.
SECTORS: dict[str, str] = {
    "Bank":             "^NSEBANK",
    "IT":               "^CNXIT",
    "Pharma":           "^CNXPHARMA",
    "Auto":             "^CNXAUTO",
    "FMCG":             "^CNXFMCG",
    "Metal":            "^CNXMETAL",
    "Energy":           "^CNXENERGY",
    "Realty":           "^CNXREALTY",
    "Infra":            "^CNXINFRA",
    "Consumer Durables":"^CNXCONSUM",
    "Media":            "^CNXMEDIA",
    "Defence":          "^CNXDEFENCE",   # may be absent in older yfinance; skipped if no data
}

NIFTY50_TICKER = "^NSEI"


# ── Data fetch ───────────────────────────────────────────────────────────────

def _download_indices(tickers: list[str], period: str = "6mo") -> dict[str, list[float]]:
    """Download daily close prices for index tickers (no .NS suffix).

    Uses individual Ticker.history() calls because sector indices use ^ prefix
    and are not in the NSE equity universe handled by _batch_download.
    Returns dict mapping ticker → list[float] of close prices (oldest → newest).
    Silently skips tickers that return no data.
    """
    result: dict[str, list[float]] = {}
    for ticker in tickers:
        try:
            hist = yf.Ticker(ticker).history(period=period)
            if hist is None or hist.empty:
                continue
            closes = hist["Close"].dropna().tolist()
            if len(closes) >= 20:  # minimum viable series
                result[ticker] = closes
        except Exception:
            continue
    return result


# ── Pure-math helpers ────────────────────────────────────────────────────────

def _sector_rs(
    sector_closes: list[float],
    nifty_closes: list[float],
    period: int,
) -> float | None:
    """Relative return of sector vs Nifty 50 over `period` bars.

    Returns decimal excess return (e.g. 0.15 = sector outperformed by 15 pp).
    Returns None when either series has fewer than `period` bars.
    """
    if len(sector_closes) < period or len(nifty_closes) < period:
        return None
    sector_ret = (sector_closes[-1] / sector_closes[-period]) - 1
    nifty_ret  = (nifty_closes[-1]  / nifty_closes[-period])  - 1
    return round(sector_ret - nifty_ret, 4)


def _rrg_quadrant(rs_now: float, rs_4w_ago: float | None) -> str:
    """Classify a sector into one of four RRG quadrants.

    rs_now     : current RS vs Nifty (positive = outperforming)
    rs_4w_ago  : RS vs Nifty 4 weeks (≈20 bars) ago; used to compute RS momentum.
    None for rs_4w_ago → classify by rs_now direction only.
    """
    if rs_4w_ago is None:
        return "Leading" if rs_now > 0 else "Lagging"
    rs_momentum = rs_now - rs_4w_ago
    if rs_now > 0 and rs_momentum > 0:
        return "Leading"
    if rs_now > 0 and rs_momentum <= 0:
        return "Weakening"
    if rs_now <= 0 and rs_momentum > 0:
        return "Improving"
    return "Lagging"


# ── Core analysis ─────────────────────────────────────────────────────────────

def analyze(primary_period: int = 63, lookback_period: int = 21) -> dict:
    """Rank all NSE sectoral indices by RS vs Nifty 50 and classify RRG quadrants.

    primary_period:  bars for current RS (default 63 = ~3 months)
    lookback_period: additional bars for RS-4-weeks-ago (to compute RS momentum)
    """
    all_tickers = [NIFTY50_TICKER] + list(SECTORS.values())

    # We need primary_period + lookback_period bars to compute RS momentum.
    # Download enough history: use "14mo" to guarantee sufficient bars.
    total_bars_needed = primary_period + lookback_period + 10  # small buffer
    # Map bars → approximate yfinance period string
    if total_bars_needed <= 63:
        dl_period = "6mo"
    elif total_bars_needed <= 126:
        dl_period = "6mo"
    else:
        dl_period = "14mo"

    _err.print(
        f"[dim]Fetching {len(all_tickers)} sector indices from yfinance — ~10-20s...[/dim]",
        highlight=False,
    )
    all_closes = _download_indices(all_tickers, period=dl_period)

    nifty_closes = all_closes.get(NIFTY50_TICKER)
    if not nifty_closes:
        return {"error": "nifty50_data_unavailable", "sectors": []}

    sectors_list: list[dict] = []
    for sector_name, ticker in SECTORS.items():
        sect_closes = all_closes.get(ticker)
        if not sect_closes:
            sectors_list.append({
                "sector": sector_name,
                "index": ticker,
                "rs_vs_nifty": None,
                "rs_vs_nifty_4w": None,
                "quadrant": "Unknown",
                "rank": None,
                "error": "no_data",
            })
            continue

        rs_now   = _sector_rs(sect_closes, nifty_closes, primary_period)
        rs_4w    = _sector_rs(sect_closes, nifty_closes, primary_period + lookback_period)

        quadrant = _rrg_quadrant(rs_now if rs_now is not None else 0.0, rs_4w)

        sectors_list.append({
            "sector": sector_name,
            "index": ticker,
            "rs_vs_nifty": round(rs_now * 100, 2) if rs_now is not None else None,
            "rs_vs_nifty_4w": round(rs_4w * 100, 2) if rs_4w is not None else None,
            "quadrant": quadrant,
        })

    # Sort by rs_vs_nifty descending (None values at the bottom)
    sectors_list.sort(
        key=lambda s: s["rs_vs_nifty"] if s["rs_vs_nifty"] is not None else float("-inf"),
        reverse=True,
    )
    for i, s in enumerate(sectors_list, 1):
        s["rank"] = i

    leading    = [s["sector"] for s in sectors_list if s["quadrant"] == "Leading"]
    improving  = [s["sector"] for s in sectors_list if s["quadrant"] == "Improving"]
    weakening  = [s["sector"] for s in sectors_list if s["quadrant"] == "Weakening"]
    lagging    = [s["sector"] for s in sectors_list if s["quadrant"] == "Lagging"]

    top_3     = [s["sector"] for s in sectors_list if s.get("rs_vs_nifty") is not None][:3]
    avoid_3   = [s["sector"] for s in reversed(sectors_list) if s.get("rs_vs_nifty") is not None][:3]

    return {
        "period_days": primary_period,
        "sectors": sectors_list,
        "leading_sectors":   leading,
        "improving_sectors": improving,
        "weakening_sectors": weakening,
        "lagging_sectors":   lagging,
        "top_3_sectors":     top_3,
        "avoid_sectors":     avoid_3,
        "source_date": date.today().isoformat(),
    }


# ── Pretty renderer ──────────────────────────────────────────────────────────

_QUADRANT_COLOUR = {
    "Leading":   "green",
    "Improving": "cyan",
    "Weakening": "yellow",
    "Lagging":   "red",
    "Unknown":   "dim",
}


def _render_pretty(data: dict) -> None:
    period = data.get("period_days", 63)

    tbl = Table(
        title=f"Sector Relative Strength vs Nifty 50 ({period}D)",
        box=box.SIMPLE,
        show_header=True,
        header_style="bold cyan",
        pad_edge=False,
    )
    tbl.add_column("Rank",     justify="right", width=5)
    tbl.add_column("Sector",   width=20)
    tbl.add_column("Ticker",   width=14, style="dim")
    tbl.add_column("RS vs Nifty", justify="right", width=14)
    tbl.add_column("Quadrant", width=12)

    for s in data.get("sectors", []):
        rs = s.get("rs_vs_nifty")
        rs_str = f"{rs:+.2f}%" if rs is not None else "—"
        rs_colour = "green" if rs and rs > 0 else "red"
        q = s.get("quadrant", "Unknown")
        q_colour = _QUADRANT_COLOUR.get(q, "white")
        err = s.get("error")

        tbl.add_row(
            str(s.get("rank", "?")),
            s["sector"],
            s["index"],
            f"[{rs_colour}]{rs_str}[/{rs_colour}]" if err is None else "[dim]no data[/dim]",
            f"[{q_colour}]{q}[/{q_colour}]",
        )

    console.print(tbl)

    # Summary
    console.print(f"\n[bold green]Top Sectors (Leading/Improving):[/bold green]")
    for s in data.get("leading_sectors", []):
        console.print(f"  [green]✓ {s}[/green]")
    for s in data.get("improving_sectors", []):
        console.print(f"  [cyan]↑ {s} (improving)[/cyan]")

    console.print(f"\n[bold red]Avoid (Lagging):[/bold red]")
    for s in data.get("lagging_sectors", []):
        console.print(f"  [red]✗ {s}[/red]")

    console.print(
        f"\n[dim]RRG Quadrants: "
        "[green]Leading[/green]=Strong RS+momentum | "
        "[cyan]Improving[/cyan]=Weak RS+rising momentum | "
        "[yellow]Weakening[/yellow]=Strong RS+falling momentum | "
        "[red]Lagging[/red]=Avoid"
        f" | Source: yfinance | Date: {data.get('source_date', '?')}[/dim]"
    )


# ── CLI ───────────────────────────────────────────────────────────────────────

@app.command()
def main(
    period: int = typer.Option(63, "--period", help="Lookback in trading days (63=3M, 126=6M)"),
    pretty: bool = typer.Option(False, "--pretty", help="Render Rich table"),
) -> None:
    """Rank NSE sector indices by relative strength vs Nifty 50.

    Classifies sectors into RRG quadrants (Leading/Improving/Weakening/Lagging).
    Completes in ~10-20 seconds.
    """
    data = analyze(primary_period=period)
    if pretty:
        _render_pretty(data)
    else:
        console.print(json.dumps(data, indent=2))
