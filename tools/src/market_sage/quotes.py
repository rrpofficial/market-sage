"""
ms-quotes SYMBOL [SYMBOL ...] [--pretty]

Fetches live price, 52W high/low, day change, MCap, volume, delivery %,
and F&O ban status for NSE/BSE symbols.
Appends .NS suffix automatically if no exchange suffix is present.
Outputs JSON by default; --pretty renders a Rich table.
"""

from __future__ import annotations

import csv
import io
import json
import os
import time
import zipfile
from datetime import date, timedelta
from typing import Optional

import requests
import typer
import yfinance as yf
from rich.console import Console
from rich.table import Table

from market_sage import CACHE_DIR

app = typer.Typer(add_completion=False)
console = Console()

_NSE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def _nse(symbol: str) -> str:
    s = symbol.upper().strip()
    if s.endswith(".NS") or s.endswith(".BO"):
        return s
    return s + ".NS"


def _cached_get(url: str, cache_name: str, ttl: int = 86400, binary: bool = False) -> bytes | str | None:
    """GET with a /tmp file cache. Returns None on any network/HTTP failure."""
    path = os.path.join(CACHE_DIR, cache_name)
    try:
        if os.path.exists(path) and time.time() - os.path.getmtime(path) < ttl:
            with open(path, "rb" if binary else "r") as f:
                return f.read()
    except Exception:
        pass
    try:
        r = requests.get(url, headers=_NSE_HEADERS, timeout=20)
        if r.status_code != 200:
            return None
        os.makedirs(CACHE_DIR, exist_ok=True)
        with open(path, "wb" if binary else "w") as f:
            f.write(r.content if binary else r.text)
        return r.content if binary else r.text
    except Exception:
        return None


def _fetch_delivery_pct(symbol: str) -> tuple[float | None, str | None]:
    """Latest available single-day delivery % and its trade date.

    Primary: nsepython live quote (NSE main API; reachable only from Indian IPs).
    Fallback: NSE daily bhav copy (sec_bhavdata_full) on archives.nseindia.com,
    walking back up to 7 calendar days to the most recent trading session.
    """
    sym = symbol.upper().split(".")[0]
    try:
        from nsepython import nse_eq
        data = nse_eq(sym) or {}
        sec = data.get("securityWiseDP") or {}
        traded = sec.get("quantityTraded")
        delivered = sec.get("deliveryQuantity")
        if traded and delivered is not None:
            return round(delivered / traded * 100, 2), date.today().isoformat()
    except Exception:
        pass

    for back in range(0, 8):
        day = date.today() - timedelta(days=back)
        tag = day.strftime("%d%m%Y")
        text = _cached_get(
            f"https://archives.nseindia.com/products/content/sec_bhavdata_full_{tag}.csv",
            f"bhav_{tag}.csv",
        )
        if not isinstance(text, str):
            continue  # weekend/holiday/not yet published — try the previous day
        for row in csv.reader(io.StringIO(text)):
            if len(row) >= 15 and row[0].strip() == sym and row[1].strip() == "EQ":
                try:
                    return float(row[14].strip()), day.isoformat()
                except ValueError:
                    return None, None
        return None, None  # bhav copy found but symbol not in it (BSE-only/SME)
    return None, None


def _fo_ban_list() -> list[str] | None:
    """Current F&O ban list symbols, or None if it cannot be fetched."""
    try:
        from nsepython import nsefetch
        data = nsefetch("https://www.nseindia.com/api/foCPForbidden") or {}
        secs = data.get("data") or data.get("securities") or []
        names = [s.get("symbol") if isinstance(s, dict) else s for s in secs]
        names = [str(n).upper() for n in names if n]
        if names:
            return names
    except Exception:
        pass

    text = _cached_get("https://archives.nseindia.com/content/fo/fo_secban.csv",
                       "fo_secban.csv", ttl=21600)
    if not isinstance(text, str):
        return None
    # Format: header line "Securities in Ban For Trade Date DD-MMM-YYYY:", then "1,SYMBOL" rows
    syms = []
    for line in text.splitlines():
        parts = line.split(",")
        if len(parts) == 2 and parts[0].strip().isdigit():
            syms.append(parts[1].strip().upper())
    return syms


def _fo_universe() -> set[str] | None:
    """All symbols with F&O contracts, or None if the list cannot be derived."""
    try:
        from nsepython import fnolist
        syms = fnolist()
        if syms:
            return {str(s).upper() for s in syms}
    except Exception:
        pass

    # Fallback: ticker symbols present in the latest F&O bhav copy on archives
    for back in range(0, 8):
        day = date.today() - timedelta(days=back)
        tag = day.strftime("%Y%m%d")
        cache_path = os.path.join(CACHE_DIR, f"fo_universe_{tag}.txt")
        try:
            if os.path.exists(cache_path):
                with open(cache_path) as f:
                    return {line.strip() for line in f if line.strip()}
        except Exception:
            pass
        blob = _cached_get(
            f"https://archives.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_{tag}_F_0000.csv.zip",
            f"fo_bhav_{tag}.zip", binary=True,
        )
        if not isinstance(blob, bytes):
            continue
        try:
            z = zipfile.ZipFile(io.BytesIO(blob))
            text = z.read(z.namelist()[0]).decode("utf-8", "replace")
            reader = csv.reader(io.StringIO(text))
            header = next(reader)
            col = header.index("TckrSymb")
            universe = {row[col].strip().upper() for row in reader if len(row) > col}
            os.makedirs(CACHE_DIR, exist_ok=True)
            with open(cache_path, "w") as f:
                f.write("\n".join(sorted(universe)))
            return universe
        except Exception:
            return None
    return None


def _is_fo_ban(symbol: str) -> bool | None:
    """True if in the F&O ban period, False if in F&O but not banned,
    None if not in the F&O universe or status cannot be determined."""
    sym = symbol.upper().split(".")[0]
    ban = _fo_ban_list()
    if ban is None:
        return None
    if sym in ban:
        return True
    universe = _fo_universe()
    if universe and sym in universe:
        return False
    return None


def fetch_quote(symbol: str) -> dict:
    ticker_sym = _nse(symbol)
    t = yf.Ticker(ticker_sym)
    try:
        hist = t.history(period="1y")
        if hist.empty:
            return {"symbol": symbol, "error": "no_data"}
        # yfinance can return NaN bars (trading halts, F&O ban days) that poison the math
        hist = hist.dropna(subset=["High", "Low", "Close"])
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
        delivery_pct, delivery_date = _fetch_delivery_pct(symbol)
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
            "delivery_pct_today": delivery_pct,
            "delivery_data_date": delivery_date,
            "fo_ban": _is_fo_ban(symbol),
            "source": "yfinance/NSE",
            "source_date": date.today().isoformat(),
        }
    except Exception as e:
        return {"symbol": symbol, "error": str(e)}


def _render_pretty(results: list[dict]) -> None:
    t = Table(title="Live Quotes", show_header=True, header_style="bold cyan")
    cols = ["Symbol", "LTP", "Day%", "52W High", "52W Low", "% from High", "MCap (Cr)", "PE", "Delivery%", "F&O Ban"]
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
            f"{r['delivery_pct_today']}%" if r.get("delivery_pct_today") is not None else "—",
            "[red]BANNED[/red]" if r.get("fo_ban") else ("No" if r.get("fo_ban") is False else "—"),
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
