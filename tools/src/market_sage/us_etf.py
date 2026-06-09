"""
ms-us-etf TICKER [TICKER ...] [--pretty]

Fetches US ETF and mutual fund data via Yahoo Finance:
  AUM ($B), expense ratio, NAV, dividend yield, YTD / 1Y / 3Y / 5Y returns,
  Morningstar category, fund family, top holdings count, and a quality checklist.

Use this for: SPY, QQQ, VTI, VXUS, BND, ARKK, sector ETFs, Vanguard/Fidelity funds.
For US stock analysis use ms-us-quotes instead.

Outputs JSON by default; --pretty renders a Rich table.
"""

from __future__ import annotations

import json
from datetime import date
from typing import Optional

import typer
import yfinance as yf
from rich.console import Console
from rich.table import Table

app = typer.Typer(add_completion=False)
console = Console()


def fetch_etf(ticker: str) -> dict:
    t = yf.Ticker(ticker.upper().strip())
    try:
        hist = t.history(period="1y")
        info = t.info or {}

        if hist.empty:
            return {"ticker": ticker.upper(), "error": "no_data"}

        price = info.get("navPrice") or info.get("regularMarketPrice") or float(hist["Close"].iloc[-1])
        prev_close = info.get("previousClose") or (float(hist["Close"].iloc[-2]) if len(hist) > 1 else price)
        day_chg_pct = ((price - prev_close) / prev_close * 100) if prev_close else 0.0

        w52_high = info.get("fiftyTwoWeekHigh") or float(hist["High"].max())
        w52_low = info.get("fiftyTwoWeekLow") or float(hist["Low"].min())
        avg_vol_20 = int(hist["Volume"].tail(20).mean()) if not hist["Volume"].empty else 0

        def _r(v, n=2):
            return round(v, n) if v is not None else None

        def _pct(v):
            return round(v * 100, 3) if v is not None else None

        expense_ratio = (
            info.get("netExpenseRatio")
            or info.get("annualReportExpenseRatio")
            or info.get("expenseRatio")
        )
        total_assets = info.get("totalAssets")

        ytd = info.get("ytdReturn")
        one_yr = None
        if len(hist) >= 252:
            one_yr = (float(hist["Close"].iloc[-1]) / float(hist["Close"].iloc[-252]) - 1) * 100
        three_yr = info.get("threeYearAverageReturn")
        five_yr = info.get("fiveYearAverageReturn")

        # Quality checklist
        checklist: list[str] = []
        if total_assets and total_assets < 100e6:
            checklist.append("⚠ AUM <$100M — low liquidity / closure risk")
        if expense_ratio and expense_ratio > 0.5:
            checklist.append(f"⚠ Expense ratio {expense_ratio:.3f}% — above low-cost threshold (0.50%)")
        if avg_vol_20 < 50_000:
            checklist.append("⚠ Low average daily volume — wide bid-ask spreads likely")
        if price and w52_high and (price / w52_high) < 0.7:
            checklist.append("⚠ >30% below 52W high — check if sector/theme is in structural decline")

        return {
            "ticker": ticker.upper(),
            "long_name": info.get("longName", ""),
            "fund_family": info.get("fundFamily", ""),
            "category": info.get("category", ""),
            "fund_type": info.get("quoteType", ""),
            "currency": info.get("currency", "USD"),
            "price": _r(price),
            "nav": _r(info.get("navPrice")),
            "prev_close": _r(prev_close),
            "day_change_pct": _r(day_chg_pct),
            "w52_high": _r(w52_high),
            "w52_low": _r(w52_low),
            "avg_vol_20d": avg_vol_20,
            "total_assets_b": _r(total_assets / 1e9) if total_assets else None,
            "expense_ratio_pct": _r(expense_ratio, 4) if expense_ratio is not None else None,
            "dividend_yield_pct": _pct(info.get("yield") or info.get("dividendYield")),
            "ytd_return_pct": _pct(ytd) if ytd is not None else (_r(one_yr, 2) if one_yr else None),
            "one_year_return_pct": _r(one_yr, 2) if one_yr else None,
            "three_year_avg_return_pct": _pct(three_yr) if three_yr is not None else None,
            "five_year_avg_return_pct": _pct(five_yr) if five_yr is not None else None,
            "holdings_count": info.get("holdings") and len(info.get("holdings", [])),
            "pe_ttm": _r(info.get("trailingPE"), 1),
            "price_to_book": _r(info.get("priceToBook")),
            "beta_3y": _r(info.get("beta3Year")),
            "morningstar_overall_rating": info.get("morningStarOverallRating"),
            "morningstar_risk_rating": info.get("morningStarRiskRating"),
            "checklist": checklist,
            "source": "Yahoo Finance / yfinance",
            "source_date": date.today().isoformat(),
        }
    except Exception as e:
        return {"ticker": ticker.upper(), "error": str(e)}


def _render_pretty(results: list[dict]) -> None:
    t = Table(title="US ETF / Fund Data", show_header=True, header_style="bold cyan")
    cols = [
        "Ticker", "Name", "Category", "AUM ($B)", "Expense%",
        "Price ($)", "Day%", "1Y Ret%", "3Y Avg%", "5Y Avg%", "Yield%",
    ]
    for c in cols:
        t.add_column(c, justify="right")

    for r in results:
        if "error" in r:
            t.add_row(r["ticker"], "[red]ERROR[/red]", *["—"] * (len(cols) - 2))
            continue
        day = r.get("day_change_pct") or 0
        day_col = f"[green]+{day:.2f}%[/green]" if day >= 0 else f"[red]{day:.2f}%[/red]"
        expense = r.get("expense_ratio_pct")
        expense_col = (
            f"[red]{expense:.3f}%[/red]" if expense and expense > 0.5 else
            (f"[green]{expense:.3f}%[/green]" if expense else "—")
        )
        t.add_row(
            r["ticker"],
            (r.get("long_name") or "")[:28],
            (r.get("category") or "")[:20],
            f"${r['total_assets_b']:,.1f}" if r.get("total_assets_b") else "—",
            expense_col,
            f"${r['price']:,.2f}" if r.get("price") else "—",
            day_col,
            f"{r['one_year_return_pct']:.1f}%" if r.get("one_year_return_pct") else "—",
            f"{r['three_year_avg_return_pct']:.1f}%" if r.get("three_year_avg_return_pct") else "—",
            f"{r['five_year_avg_return_pct']:.1f}%" if r.get("five_year_avg_return_pct") else "—",
            f"{r['dividend_yield_pct']:.2f}%" if r.get("dividend_yield_pct") else "—",
        )
    console.print(t)

    for r in results:
        if r.get("checklist"):
            console.print(f"\n[bold yellow]Checklist flags for {r['ticker']}:[/bold yellow]")
            for flag in r["checklist"]:
                console.print(f"  {flag}")


@app.command()
def main(
    tickers: list[str] = typer.Argument(
        ..., help="US ETF/fund tickers, e.g. SPY QQQ VTI VXUS BND ARKK"
    ),
    pretty: bool = typer.Option(False, "--pretty", help="Render Rich table instead of JSON"),
) -> None:
    results = [fetch_etf(tk) for tk in tickers]
    if pretty:
        _render_pretty(results)
    else:
        print(
            json.dumps(
                results if len(results) > 1 else results[0],
                indent=2,
                ensure_ascii=False,
            )
        )


if __name__ == "__main__":
    app()
