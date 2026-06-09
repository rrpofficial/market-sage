"""
ms-us-quotes TICKER [TICKER ...] [--pretty]

Fetches live price, 52W high/low, day change %, market cap ($B),
P/E (TTM), forward P/E, PEG, EV/EBITDA, P/B, dividend yield,
beta, short ratio, analyst target, and TTM financials for US
stocks and ETFs via Yahoo Finance.

Tickers are used as-is — no exchange suffix is added.
Examples: AAPL, MSFT, GOOGL, JPM, BRK-B, SPY, QQQ
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


def fetch_quote(ticker: str) -> dict:
    t = yf.Ticker(ticker.upper().strip())
    try:
        hist = t.history(period="1y")
        if hist.empty:
            return {"ticker": ticker.upper(), "error": "no_data"}
        info = t.info or {}

        ltp = (
            info.get("currentPrice")
            or info.get("regularMarketPrice")
            or float(hist["Close"].iloc[-1])
        )
        prev_close = info.get("previousClose") or (
            float(hist["Close"].iloc[-2]) if len(hist) > 1 else ltp
        )
        day_chg_pct = ((ltp - prev_close) / prev_close * 100) if prev_close else 0.0

        w52_high = info.get("fiftyTwoWeekHigh") or float(hist["High"].max())
        w52_low = info.get("fiftyTwoWeekLow") or float(hist["Low"].min())
        avg_vol_20 = int(hist["Volume"].tail(20).mean()) if not hist["Volume"].empty else 0

        mcap = info.get("marketCap") or 0
        ev = info.get("enterpriseValue")

        def _pct(v):
            return round(v * 100, 2) if v is not None else None

        def _r(v, n=2):
            return round(v, n) if v is not None else None

        return {
            "ticker": ticker.upper(),
            "long_name": info.get("longName", ""),
            "exchange": info.get("exchange", ""),
            "sector": info.get("sector", ""),
            "industry": info.get("industry", ""),
            "currency": info.get("currency", "USD"),
            "price": _r(ltp),
            "prev_close": _r(prev_close),
            "day_change_pct": _r(day_chg_pct),
            "w52_high": _r(w52_high),
            "w52_low": _r(w52_low),
            "pct_from_52w_high": _r((ltp - w52_high) / w52_high * 100, 1),
            "pct_from_52w_low": _r((ltp - w52_low) / w52_low * 100, 1),
            "avg_vol_20d": avg_vol_20,
            "market_cap_b": _r(mcap / 1e9, 2) if mcap else None,
            "enterprise_value_b": _r(ev / 1e9, 2) if ev else None,
            "pe_ttm": _r(info.get("trailingPE"), 1),
            "forward_pe": _r(info.get("forwardPE"), 1),
            "peg_ratio": _r(info.get("pegRatio")),
            "ev_ebitda": _r(info.get("enterpriseToEbitda"), 1),
            "ev_revenue": _r(info.get("enterpriseToRevenue"), 2),
            "price_to_book": _r(info.get("priceToBook")),
            "price_to_sales": _r(info.get("priceToSalesTrailing12Months")),
            "dividend_yield_pct": _pct(info.get("dividendYield")),
            "beta": _r(info.get("beta")),
            "short_ratio": _r(info.get("shortRatio"), 1),
            "short_pct_of_float": _pct(info.get("shortPercentOfFloat")),
            "analyst_target_price": _r(info.get("targetMeanPrice")),
            "analyst_low_target": _r(info.get("targetLowPrice")),
            "analyst_high_target": _r(info.get("targetHighPrice")),
            "analyst_recommendation": info.get("recommendationKey", ""),
            "analyst_count": info.get("numberOfAnalystOpinions"),
            "roe_pct": _pct(info.get("returnOnEquity")),
            "roa_pct": _pct(info.get("returnOnAssets")),
            "revenue_ttm_b": _r((info.get("totalRevenue") or 0) / 1e9) if info.get("totalRevenue") else None,
            "gross_margin_pct": _pct(info.get("grossMargins")),
            "operating_margin_pct": _pct(info.get("operatingMargins")),
            "profit_margin_pct": _pct(info.get("profitMargins")),
            "debt_to_equity": _r(info.get("debtToEquity")),
            "current_ratio": _r(info.get("currentRatio")),
            "free_cashflow_b": _r((info.get("freeCashflow") or 0) / 1e9) if info.get("freeCashflow") else None,
            "eps_ttm": _r(info.get("trailingEps")),
            "eps_forward": _r(info.get("forwardEps")),
            "shares_outstanding_b": _r((info.get("sharesOutstanding") or 0) / 1e9) if info.get("sharesOutstanding") else None,
            "insider_pct": _pct(info.get("heldPercentInsiders")),
            "institution_pct": _pct(info.get("heldPercentInstitutions")),
            "source": "Yahoo Finance / yfinance",
            "source_date": date.today().isoformat(),
        }
    except Exception as e:
        return {"ticker": ticker.upper(), "error": str(e)}


def _render_pretty(results: list[dict]) -> None:
    t = Table(title="US Stock / ETF Quotes", show_header=True, header_style="bold cyan")
    cols = [
        "Ticker", "Name", "Price ($)", "Day%",
        "52W High", "52W Low", "% from High",
        "MCap ($B)", "P/E (TTM)", "Fwd P/E", "EV/EBITDA", "Div Yield%",
    ]
    for c in cols:
        t.add_column(c, justify="right")
    for r in results:
        if "error" in r:
            t.add_row(r["ticker"], "[red]ERROR[/red]", *["—"] * (len(cols) - 2))
            continue
        pct_high = r.get("pct_from_52w_high") or 0
        pct_col = (
            f"[red]{pct_high}%[/red]" if pct_high < -30
            else f"[yellow]{pct_high}%[/yellow]"
        )
        day = r.get("day_change_pct") or 0
        day_col = (
            f"[green]+{day}%[/green]" if day >= 0 else f"[red]{day}%[/red]"
        )
        t.add_row(
            r["ticker"],
            (r.get("long_name") or "")[:28],
            f"${r['price']:,.2f}",
            day_col,
            f"${r['w52_high']:,.2f}",
            f"${r['w52_low']:,.2f}",
            pct_col,
            f"${r['market_cap_b']:,.1f}" if r.get("market_cap_b") else "—",
            str(r["pe_ttm"]) if r.get("pe_ttm") else "—",
            str(r["forward_pe"]) if r.get("forward_pe") else "—",
            str(r["ev_ebitda"]) if r.get("ev_ebitda") else "—",
            f"{r['dividend_yield_pct']}%" if r.get("dividend_yield_pct") else "—",
        )
    console.print(t)


@app.command()
def main(
    tickers: list[str] = typer.Argument(
        ..., help="US stock/ETF tickers, e.g. AAPL MSFT SPY QQQ"
    ),
    pretty: bool = typer.Option(False, "--pretty", help="Render Rich table instead of JSON"),
) -> None:
    results = [fetch_quote(tk) for tk in tickers]
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
