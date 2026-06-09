"""
ms-dcf [OPTIONS]

Intrinsic value calculator: DCF, Graham Number, PE-based, and Reverse DCF.
All inputs must be explicitly provided — this tool never recalls data from
training memory. Feed it numbers fetched from Screener.in or ms-screener.

Usage examples:
  ms-dcf --symbol CDSL --fcf 560 --growth 20 --price 1212
  ms-dcf --symbol KAYNES --eps 54 --book 707 --pe-fair 40 --price 3072 --fcf 200 --growth 18
  ms-dcf --symbol ANY --price 1003 --fcf 1200 --growth 30 --reverse-only
"""

from __future__ import annotations

import json
import math
from datetime import date
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(add_completion=False)
console = Console()


def dcf_value(
    fcf: float,
    growth_rate: float,
    discount_rate: float,
    terminal_growth: float,
    years: int,
    shares: Optional[float] = None,
) -> dict:
    """Standard two-stage DCF. Returns total intrinsic value (and per-share if shares given)."""
    r = discount_rate / 100
    g = growth_rate / 100
    tg = terminal_growth / 100

    pv_fcfs = 0.0
    cf = fcf
    for t in range(1, years + 1):
        cf *= 1 + g
        pv_fcfs += cf / (1 + r) ** t

    terminal_cf = cf * (1 + tg)
    terminal_value = terminal_cf / (r - tg) if r > tg else 0.0
    pv_terminal = terminal_value / (1 + r) ** years
    total_iv = pv_fcfs + pv_terminal

    result = {
        "method": "DCF",
        "inputs": {
            "fcf_cr": fcf,
            "growth_rate_pct": growth_rate,
            "discount_rate_pct": discount_rate,
            "terminal_growth_pct": terminal_growth,
            "years": years,
        },
        "pv_free_cash_flows_cr": round(pv_fcfs, 2),
        "pv_terminal_value_cr": round(pv_terminal, 2),
        "total_intrinsic_value_cr": round(total_iv, 2),
    }
    if shares:
        result["intrinsic_value_per_share"] = round(total_iv * 1e7 / shares, 2)
    return result


def graham_number(eps: float, book_value_per_share: float) -> dict:
    """Graham Number = sqrt(22.5 × EPS × BV/share). Best for stable asset-heavy businesses."""
    if eps <= 0 or book_value_per_share <= 0:
        return {"method": "Graham Number", "error": "EPS and book value must be positive"}
    gn = math.sqrt(22.5 * eps * book_value_per_share)
    return {
        "method": "Graham Number",
        "inputs": {"eps": eps, "book_value_per_share": book_value_per_share},
        "intrinsic_value_per_share": round(gn, 2),
        "note": "Most reliable for stable, asset-heavy businesses. Less meaningful for capital-light high-growth cos.",
    }


def pe_based_value(eps: float, fair_pe: float) -> dict:
    """Normalised EPS × fair P/E = intrinsic value."""
    iv = eps * fair_pe
    return {
        "method": "PE-Based",
        "inputs": {"eps": eps, "fair_pe": fair_pe},
        "intrinsic_value_per_share": round(iv, 2),
    }


def reverse_dcf(
    current_price: float,
    fcf_base: float,
    discount_rate: float,
    terminal_growth: float,
    years: int,
    shares: float,
) -> dict:
    """
    Finds the growth rate implied by the current market price.
    Binary search over growth_rate until DCF ≈ market cap.
    """
    market_cap_cr = current_price * shares / 1e7

    def total_iv(g_pct: float) -> float:
        r = discount_rate / 100
        g = g_pct / 100
        tg = terminal_growth / 100
        pv = 0.0
        cf = fcf_base
        for t in range(1, years + 1):
            cf *= 1 + g
            pv += cf / (1 + r) ** t
        term_cf = cf * (1 + tg)
        pv_term = (term_cf / (r - tg)) / (1 + r) ** years if r > tg else 0.0
        return pv + pv_term

    lo, hi = 0.0, 60.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if total_iv(mid) < market_cap_cr:
            lo = mid
        else:
            hi = mid

    implied_growth = round((lo + hi) / 2, 1)
    return {
        "method": "Reverse DCF",
        "inputs": {
            "current_price": current_price,
            "shares_cr": shares / 1e7,
            "fcf_base_cr": fcf_base,
            "discount_rate_pct": discount_rate,
            "terminal_growth_pct": terminal_growth,
            "years": years,
        },
        "market_cap_cr": round(market_cap_cr, 2),
        "implied_annual_growth_rate_pct": implied_growth,
        "assessment": _assess_implied_growth(implied_growth),
    }


def _assess_implied_growth(g: float) -> str:
    if g > 25:
        return f"STRETCHED — market pricing in {g}% annual growth for the projection period. Very high bar to clear."
    if g > 18:
        return f"AMBITIOUS — {g}% priced in. Achievable only if strong execution continues consistently."
    if g > 12:
        return f"REASONABLE — {g}% aligns with historical growth trajectories for quality mid-caps."
    return f"CONSERVATIVE — only {g}% growth priced in. Low bar; stock likely undervalued if thesis holds."


def _margin_of_safety(iv: float, price: float) -> dict:
    mos = (iv - price) / iv * 100
    if mos >= 25:
        verdict = "BUY zone (>25% margin of safety)"
    elif mos >= 0:
        verdict = "HOLD / accumulate on dips (0–25% margin)"
    else:
        verdict = "AVOID new entry (overvalued)"
    return {"margin_of_safety_pct": round(mos, 1), "verdict": verdict}


@app.command()
def main(
    symbol: str = typer.Option(..., "--symbol", "-s", help="Stock symbol (for labelling only)"),
    price: float = typer.Option(..., "--price", "-p", help="Current market price (₹/share)"),
    fcf: Optional[float] = typer.Option(None, "--fcf", help="Latest annual Free Cash Flow (₹ Cr)"),
    growth: Optional[float] = typer.Option(None, "--growth", "-g", help="Expected FCF/EPS growth rate % p.a."),
    discount: float = typer.Option(13.0, "--discount", help="Discount rate % (WACC, default 13 for India)"),
    terminal: float = typer.Option(5.0, "--terminal", help="Terminal growth rate % (default 5)"),
    years: int = typer.Option(10, "--years", help="DCF projection years (default 10)"),
    shares: Optional[float] = typer.Option(None, "--shares", help="Shares outstanding (Cr units)"),
    eps: Optional[float] = typer.Option(None, "--eps", help="Normalised EPS (₹/share)"),
    book: Optional[float] = typer.Option(None, "--book", help="Book value per share (₹)"),
    pe_fair: Optional[float] = typer.Option(None, "--pe-fair", help="Fair P/E multiple for PE-based valuation"),
    reverse_only: bool = typer.Option(False, "--reverse-only", help="Only compute reverse DCF (what growth is priced in?)"),
    pretty: bool = typer.Option(False, "--pretty", help="Render Rich table instead of JSON"),
) -> None:
    results: list[dict] = []

    if fcf and growth and not reverse_only:
        results.append(dcf_value(fcf, growth, discount, terminal, years, shares=(shares * 1e7 if shares else None)))

    if eps and book:
        results.append(graham_number(eps, book))

    if eps and pe_fair:
        results.append(pe_based_value(eps, pe_fair))

    if fcf and shares and price:
        results.append(reverse_dcf(price, fcf, discount, terminal, years, shares * 1e7))
    elif fcf and growth and not results:
        results.append({"note": "Provide --shares for per-share DCF and reverse DCF."})

    if not results:
        console.print("[red]Provide at least: --fcf --growth or --eps --book or --eps --pe-fair[/red]")
        raise typer.Exit(1)

    # Margin of safety for each method that produces a per-share IV
    for r in results:
        iv = r.get("intrinsic_value_per_share")
        if iv:
            r["margin_of_safety"] = _margin_of_safety(iv, price)

    output = {
        "symbol": symbol.upper(),
        "current_price": price,
        "source_date": date.today().isoformat(),
        "valuations": results,
        "note": "All inputs manually provided. No LLM training knowledge used.",
    }

    if pretty:
        _render_pretty(output)
    else:
        print(json.dumps(output, indent=2, ensure_ascii=False))


def _render_pretty(output: dict) -> None:
    console.rule(f"[bold cyan]DCF & Valuation — {output['symbol']}[/bold cyan]")
    console.print(f"Current Price: ₹{output['current_price']:,.2f}  |  Date: {output['source_date']}\n")
    for v in output["valuations"]:
        method = v.get("method", "")
        iv = v.get("intrinsic_value_per_share")
        mos = v.get("margin_of_safety", {})
        if method and iv:
            mos_str = f"MoS: {mos.get('margin_of_safety_pct', '—')}%  →  {mos.get('verdict', '')}"
            console.print(f"[bold]{method}[/bold]: ₹{iv:,.2f}  |  {mos_str}")
        elif method == "Reverse DCF":
            ig = v.get("implied_annual_growth_rate_pct")
            assessment = v.get("assessment", "")
            console.print(f"[bold]{method}[/bold]: Implied growth = {ig}%  →  {assessment}")
        elif "error" in v:
            console.print(f"[yellow]{method}: {v['error']}[/yellow]")
        elif "note" in v:
            console.print(f"[dim]{v['note']}[/dim]")


if __name__ == "__main__":
    app()
