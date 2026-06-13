"""Shared utilities for momentum-sage tools (Phases 4–9).

Extracted here to avoid duplication across momentum_score.py, rs_rank.py,
breadth.py, sector_rs.py, and momentum_screen.py. All callers import from
this module.
"""

from __future__ import annotations

import yfinance as yf


def _nse(symbol: str) -> str:
    """Append .NS suffix unless the symbol already has an exchange suffix."""
    s = symbol.upper().strip()
    return s if s.endswith((".NS", ".BO")) else s + ".NS"


def _period_return(closes: list[float], n_bars: int) -> float | None:
    """Price return over the last n_bars trading days, as a decimal.

    Returns None when the series is too short (need n_bars + 1 bars minimum).
    """
    if len(closes) < n_bars + 1:
        return None
    return round((closes[-1] / closes[-n_bars]) - 1.0, 4)


def _get_universe(index_name: str) -> list[str]:
    """Return an NSE ticker list for a named index.

    Primary: nsepython live constituent fetch.
    Fallback: hardcoded list from market_sage.data.nifty500_tickers.
    The fallback is a quarterly-refreshed snapshot; the primary is always preferred.
    """
    _idx = index_name.upper().strip()
    try:
        from nsepython import nse_get_index_quote_info  # type: ignore[import]
        data = nse_get_index_quote_info(_idx)
        if data and isinstance(data, list):
            symbols = [s.get("symbol", "") for s in data if s.get("symbol")]
            if len(symbols) >= 10:
                return symbols
    except Exception:
        pass

    from market_sage.data.nifty500_tickers import (
        NIFTY50,
        NIFTY100,
        NIFTYMIDCAP150,
        NIFTYSMALLCAP250,
        NIFTY500,
    )
    mapping: dict[str, list[str]] = {
        "NIFTY50": NIFTY50,
        "NIFTY 50": NIFTY50,
        "NIFTY100": NIFTY100,
        "NIFTY 100": NIFTY100,
        "NIFTYMIDCAP150": NIFTYMIDCAP150,
        "NIFTY MIDCAP 150": NIFTYMIDCAP150,
        "NIFTYSMALLCAP250": NIFTYSMALLCAP250,
        "NIFTY SMALLCAP 250": NIFTYSMALLCAP250,
        "NIFTY500": NIFTY500,
        "NIFTY 500": NIFTY500,
    }
    return mapping.get(_idx, NIFTY500)


def _batch_download(tickers: list[str], period: str = "1y") -> dict[str, list[float]]:
    """Batch-download OHLCV close prices for a list of NSE tickers via yfinance.

    Returns dict mapping stripped symbol (no exchange suffix) → list[float] of
    close prices. Symbols with < 100 bars of data are excluded silently.

    Uses a single yf.download() call (not one per symbol) to minimise round-trips.
    Fetching 500 tickers takes 15-30 seconds; Nifty 50 takes 3-5 seconds.
    """
    if not tickers:
        return {}

    ns_tickers = [t if t.endswith((".NS", ".BO")) else t + ".NS" for t in tickers]

    try:
        raw = yf.download(
            ns_tickers,
            period=period,
            auto_adjust=True,
            progress=False,
            threads=True,
        )
    except Exception:
        return {}

    if raw is None or (hasattr(raw, "empty") and raw.empty):
        return {}

    # yf.download with multiple tickers → MultiIndex columns (Price, Ticker).
    # raw["Close"] → DataFrame with columns = ticker strings.
    # With a single ticker, raw.columns is flat and raw["Close"] is a Series.
    try:
        if hasattr(raw.columns, "levels"):
            # Multi-ticker MultiIndex path
            level_values = list(raw.columns.get_level_values(0))
            if "Close" in level_values:
                closes_df = raw["Close"]
            else:
                # Fallback: try level-1
                closes_df = raw.xs("Close", axis=1, level=1)
        elif "Close" in raw.columns:
            # Single-ticker flat columns
            sym = ns_tickers[0].replace(".NS", "").replace(".BO", "")
            vals = raw["Close"].dropna().tolist()
            return {sym: vals} if len(vals) >= 100 else {}
        else:
            return {}
    except Exception:
        return {}

    result: dict[str, list[float]] = {}
    for col in closes_df.columns:
        ticker_str = str(col)
        sym = ticker_str.replace(".NS", "").replace(".BO", "")
        vals = closes_df[col].dropna().tolist()
        if len(vals) >= 100:
            result[sym] = vals
    return result
