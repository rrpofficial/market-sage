"""
ms-rs-rank SYMBOL [SYMBOL ...] [--vs NIFTY500] [--pretty]

Computes IBD-style Relative Strength (RS) Rating (1–99 scale) and Mansfield RS
for NSE/BSE symbols vs a reference index universe.

RS Rating (IBD-style):
  Weighted quarterly return score, percentile-ranked within the universe.
  Formula: 0.40×Q1 + 0.20×Q2 + 0.20×Q3 + 0.20×Q4 where each Q is a 3-month
  return measured from oldest to most recent.
  Score of 85 means the stock outperformed 85% of the universe over the last year.

Mansfield RS:
  Relative return of the stock vs Nifty 50 over 12 months.
  Positive = outperforming; negative = underperforming.

  --vs    Reference universe (NIFTY500, NIFTY100, NIFTY50, NIFTYMIDCAP150). Default: NIFTY500.
  --pretty  Render a Rich table with colour-coded ratings.

Live data only — universe is downloaded fresh via yfinance.
Fetching NIFTY500 (500 tickers) takes 15–25 seconds; NIFTY50 takes 3–5 seconds.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from typing import Optional

import typer
import yfinance as yf
from rich.console import Console
from rich.table import Table

from market_sage._utils import _batch_download, _get_universe, _nse, _period_return

app = typer.Typer(add_completion=False)
console = Console()


# ── Pure-math helpers ────────────────────────────────────────────────────────

def _ibdrs_score(closes: list[float]) -> float | None:
    """IBD-style composite return score.

    Weights the four most-recent 3-month quarters:
      Q1 (most recent, 0–3M ago): 0.40
      Q2 (3–6M ago):              0.20
      Q3 (6–9M ago):              0.20
      Q4 (9–12M ago):             0.20

    Requires at least 252 daily bars.
    """
    if len(closes) < 252:
        return None
    # Quarter returns: (price_at_end / price_at_start) - 1
    q1 = (closes[-1]   / closes[-63])  - 1   # 0–3M, weight 0.40
    q2 = (closes[-63]  / closes[-126]) - 1   # 3–6M, weight 0.20
    q3 = (closes[-126] / closes[-189]) - 1   # 6–9M, weight 0.20
    q4 = (closes[-189] / closes[-252]) - 1   # 9–12M, weight 0.20
    return 0.40 * q1 + 0.20 * q2 + 0.20 * q3 + 0.20 * q4


def _percentile_rank(score: float, universe: list[float]) -> int:
    """Rank `score` within `universe` on a 1–99 integer scale.

    A score of 85 means the symbol outperformed 85% of the universe.
    """
    if not universe:
        return 50
    pct = sum(1 for s in universe if s < score) / len(universe) * 99
    return max(1, min(99, round(pct) + 1))


def _mansfield_rs(stock_closes: list[float], index_closes: list[float]) -> float | None:
    """Mansfield Relative Strength: stock's 12M return relative to index's 12M return.

    Returns the decimal excess return. E.g. 0.25 means the stock outperformed
    the index by 25 percentage points over 12 months.
    Requires at least 252 bars in both series.
    """
    if len(stock_closes) < 252 or len(index_closes) < 252:
        return None
    stock_ret = (stock_closes[-1] / stock_closes[-252]) - 1
    index_ret = (index_closes[-1] / index_closes[-252]) - 1
    # Relative return: (1 + stock) / (1 + index) - 1
    return round((1 + stock_ret) / (1 + index_ret) - 1, 4)


# ── Universe fetch & scoring ─────────────────────────────────────────────────

def _download_with_status(tickers: list[str], label: str, period: str = "14mo") -> dict[str, list[float]]:
    """Wrap _batch_download with a console status message."""
    console.print(
        f"[dim]Fetching {len(tickers)} tickers ({label}) from yfinance — may take "
        f"{'15-25s' if len(tickers) >= 400 else '3-10s'}...[/dim]",
        highlight=False,
    )
    return _batch_download(tickers, period=period)


def fetch_rs(symbol: str, vs: str = "NIFTY500") -> dict:
    """Compute IBD RS Rating and Mansfield RS for one symbol vs the chosen universe.

    Returns a structured dict; on error returns {"symbol": ..., "error": ...}.
    """
    sym_upper = symbol.upper().strip()

    universe_syms = _get_universe(vs)
    # Add target symbol to the batch download so we get its data in the same call
    all_syms = list(dict.fromkeys(universe_syms + [sym_upper]))  # dedup, preserving order
    # Use 14mo to guarantee >= 252 trading bars (period="1y" gives ~250 due to holidays)
    all_closes = _download_with_status(all_syms, label=vs, period="14mo")

    if not all_closes:
        return {"symbol": sym_upper, "error": "batch_download_failed"}

    sym_closes = all_closes.get(sym_upper)
    if not sym_closes:
        return {"symbol": sym_upper, "error": "no_data_for_symbol"}

    sym_score = _ibdrs_score(sym_closes)
    if sym_score is None:
        return {
            "symbol": sym_upper,
            "error": "insufficient_history",
            "bars_available": len(sym_closes),
            "bars_required": 252,
        }

    # Universe scores (only symbols with >= 252 bars)
    universe_scores: list[float] = []
    for us in universe_syms:
        cl = all_closes.get(us)
        if cl:
            sc = _ibdrs_score(cl)
            if sc is not None:
                universe_scores.append(sc)

    if not universe_scores:
        return {"symbol": sym_upper, "error": "empty_universe_scores"}

    rs_rating = _percentile_rank(sym_score, universe_scores)

    # Mansfield RS vs Nifty 50 index (^NSEI)
    mansfield: float | None = None
    try:
        nifty_hist = yf.Ticker("^NSEI").history(period="14mo")
        if nifty_hist is not None and not nifty_hist.empty:
            nifty_closes = nifty_hist["Close"].dropna().tolist()
            mansfield = _mansfield_rs(sym_closes, nifty_closes)
    except Exception:
        pass

    if rs_rating >= 80:
        rs_label = "Leader — top 20%"
    elif rs_rating >= 70:
        rs_label = "Strong — top 30%"
    elif rs_rating >= 50:
        rs_label = "Average"
    else:
        rs_label = "Laggard — bottom 50%"

    return {
        "symbol": sym_upper,
        "vs_universe": vs,
        "rs_rating": rs_rating,
        "rs_label": rs_label,
        "ibdrs_score": round(sym_score, 4),
        "mansfield_rs": mansfield,
        "mansfield_signal": (
            "Outperforming" if (mansfield is not None and mansfield > 0)
            else ("Underperforming" if mansfield is not None else "unknown")
        ),
        "universe_size": len(universe_scores),
        "source_date": date.today().isoformat(),
    }


def analyze(symbols: list[str], vs: str = "NIFTY500") -> list[dict]:
    """Score multiple symbols against the same universe (shared batch download)."""
    sym_list = [s.upper().strip() for s in symbols]
    universe_syms = _get_universe(vs)
    all_syms = list(dict.fromkeys(universe_syms + sym_list))
    # Use 14mo to guarantee >= 252 trading bars (period="1y" gives ~250 due to holidays)
    all_closes = _download_with_status(all_syms, label=vs, period="14mo")

    if not all_closes:
        return [{"symbol": s, "error": "batch_download_failed"} for s in sym_list]

    # Pre-compute universe scores once
    universe_scores: list[float] = []
    for us in universe_syms:
        cl = all_closes.get(us)
        if cl:
            sc = _ibdrs_score(cl)
            if sc is not None:
                universe_scores.append(sc)

    # Nifty 50 index closes for Mansfield RS (14mo ensures >= 252 bars)
    nifty_closes: list[float] = []
    try:
        nifty_hist = yf.Ticker("^NSEI").history(period="14mo")
        if nifty_hist is not None and not nifty_hist.empty:
            nifty_closes = nifty_hist["Close"].dropna().tolist()
    except Exception:
        pass

    results: list[dict] = []
    for sym in sym_list:
        sym_closes = all_closes.get(sym)
        if not sym_closes:
            results.append({"symbol": sym, "error": "no_data_for_symbol"})
            continue

        sym_score = _ibdrs_score(sym_closes)
        if sym_score is None:
            results.append({"symbol": sym, "error": "insufficient_history", "bars": len(sym_closes)})
            continue

        rs_rating = _percentile_rank(sym_score, universe_scores) if universe_scores else 50
        mansfield = _mansfield_rs(sym_closes, nifty_closes) if len(nifty_closes) >= 252 else None

        if rs_rating >= 80:
            rs_label = "Leader — top 20%"
        elif rs_rating >= 70:
            rs_label = "Strong — top 30%"
        elif rs_rating >= 50:
            rs_label = "Average"
        else:
            rs_label = "Laggard — bottom 50%"

        results.append({
            "symbol": sym,
            "vs_universe": vs,
            "rs_rating": rs_rating,
            "rs_label": rs_label,
            "ibdrs_score": round(sym_score, 4),
            "mansfield_rs": mansfield,
            "mansfield_signal": (
                "Outperforming" if (mansfield is not None and mansfield > 0)
                else ("Underperforming" if mansfield is not None else "unknown")
            ),
            "universe_size": len(universe_scores),
            "source_date": date.today().isoformat(),
        })

    return results


# ── Pretty renderer ──────────────────────────────────────────────────────────

def _rs_colour(rating: int) -> str:
    if rating >= 80:
        return "green"
    if rating >= 70:
        return "yellow"
    return "red"


def _render_pretty(results: list[dict]) -> None:
    tbl = Table(title="IBD-Style RS Rating", show_header=True, header_style="bold cyan")
    tbl.add_column("Symbol", style="bold")
    tbl.add_column("RS Rating", justify="right")
    tbl.add_column("RS Label")
    tbl.add_column("Mansfield RS", justify="right")
    tbl.add_column("Signal")
    tbl.add_column("Universe")
    tbl.add_column("Univ. Size", justify="right")

    for r in results:
        if "error" in r:
            tbl.add_row(r.get("symbol", "?"), f"[red]ERR: {r['error']}[/red]", "", "", "", "", "")
            continue

        rs = r.get("rs_rating", 0)
        colour = _rs_colour(rs)
        mansfield = r.get("mansfield_rs")
        mf_str = f"{mansfield:+.3f}" if mansfield is not None else "—"
        mf_colour = "green" if mansfield and mansfield > 0 else "red"

        tbl.add_row(
            r.get("symbol", "?"),
            f"[{colour}]{rs}[/{colour}]",
            r.get("rs_label", ""),
            f"[{mf_colour}]{mf_str}[/{mf_colour}]",
            r.get("mansfield_signal", ""),
            r.get("vs_universe", ""),
            str(r.get("universe_size", "")),
        )

    console.print(tbl)
    console.print(f"[dim]Source: yfinance | Date: {date.today().isoformat()}[/dim]")
    console.print(
        "[dim]RS Rating: 80+ = top 20% Leader | 70-79 = Strong | < 70 = Average/Laggard[/dim]"
    )
    console.print(
        "[dim]Mansfield RS: positive = outperforming Nifty 50 over 12M | negative = underperforming[/dim]"
    )


# ── CLI ───────────────────────────────────────────────────────────────────────

@app.command()
def main(
    symbols: list[str] = typer.Argument(..., help="One or more NSE symbols (e.g. KAYNES CDSL)"),
    vs: str = typer.Option("NIFTY500", "--vs", help="Reference universe: NIFTY500, NIFTY100, NIFTY50, NIFTYMIDCAP150"),
    pretty: bool = typer.Option(False, "--pretty", help="Render a Rich table"),
) -> None:
    """Compute IBD-style RS Rating and Mansfield RS vs a reference universe."""
    results = analyze(symbols, vs=vs)
    if pretty:
        _render_pretty(results)
    else:
        output = results if len(results) > 1 else results[0]
        console.print(json.dumps(output, indent=2))
