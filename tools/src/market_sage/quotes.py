"""
ms-quotes SYMBOL [SYMBOL ...] [--pretty]

Fetches live price, 52W high/low, day change, MCap, volume for NSE/BSE symbols.
Appends .NS suffix automatically if no exchange suffix is present.
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


def _nse(symbol: str) -> str:
    s = symbol.upper().strip()
    if s.endswith(".NS") or s.endswith(".BO"):
        return s
    return s + ".NS"


def fetch_quote(symbol: str) -> dict:
    ticker_sym = _nse(symbol)
    t = yf.Ticker(ticker_sym)
    try:
        hist = t.history(period="1y")
        if hist.empty:
            return {"symbol": symbol, "error": "no_data"}
        info = t.info or {}
        ltp = float(hist["Close"].iloc[-1])
        prev_close = float(hist["Close"].iloc[-2]) if len(hist) > 1 else ltp
        day_chg_pct = ((ltp - prev_close) / prev_close * 100) if prev_close else 0.0
        w52_high = float(hist["High"].max())
        w52_low = float(hist["Low"].min())
        avg_vol_20 = int(hist["Volume"].tail(20).mean())
        mcap = info.get("marketCap") or 0
        pe = info.get("trailingPE")
        pb = info.get("priceToBook")
        return {
            "symbol": symbol.upper(),
            "ticker": ticker_sym,
            "ltp": round(ltp, 2),
            "prev_close": round(prev_close, 2),
            "day_change_pct": round(day_chg_pct, 2),
            "w52_high": round(w52_high, 2),
            "w52_low": round(w52_low, 2),
            "pct_from_52w_high": round((ltp - w52_high) / w52_high * 100, 1),
            "pct_from_52w_low": round((ltp - w52_low) / w52_low * 100, 1),
            "avg_vol_20d": avg_vol_20,
            "market_cap_cr": round(mcap / 1e7, 0) if mcap else None,
            "pe_ttm": round(pe, 1) if pe else None,
            "pb": round(pb, 2) if pb else None,
            "source": "yfinance/NSE",
            "source_date": date.today().isoformat(),
        }
    except Exception as e:
        return {"symbol": symbol, "error": str(e)}


def _render_pretty(results: list[dict]) -> None:
    t = Table(title="Live Quotes", show_header=True, header_style="bold cyan")
    cols = ["Symbol", "LTP", "Day%", "52W High", "52W Low", "% from High", "MCap (Cr)", "PE"]
    for c in cols:
        t.add_column(c, justify="right")
    for r in results:
        if "error" in r:
            t.add_row(r["symbol"], "[red]ERROR[/red]", *["—"] * (len(cols) - 2))
            continue
        pct_high = r["pct_from_52w_high"]
        pct_col = f"[red]{pct_high}%[/red]" if pct_high < -30 else f"[yellow]{pct_high}%[/yellow]"
        day_col = f"[green]+{r['day_change_pct']}%[/green]" if r["day_change_pct"] >= 0 else f"[red]{r['day_change_pct']}%[/red]"
        t.add_row(
            r["symbol"],
            f"₹{r['ltp']:,.2f}",
            day_col,
            f"₹{r['w52_high']:,.2f}",
            f"₹{r['w52_low']:,.2f}",
            pct_col,
            f"₹{r['market_cap_cr']:,.0f}" if r["market_cap_cr"] else "—",
            str(r["pe_ttm"]) if r["pe_ttm"] else "—",
        )
    console.print(t)


@app.command()
def main(
    symbols: list[str] = typer.Argument(..., help="NSE symbols, e.g. KAYNES CDSL ICICIBANK"),
    pretty: bool = typer.Option(False, "--pretty", help="Render Rich table instead of JSON"),
) -> None:
    results = [fetch_quote(s) for s in symbols]
    if pretty:
        _render_pretty(results)
    else:
        print(json.dumps(results if len(results) > 1 else results[0], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    app()
