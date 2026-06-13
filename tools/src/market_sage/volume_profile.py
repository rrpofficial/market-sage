"""
ms-volume-profile SYMBOL [--period 6mo] [--pretty]

Volume quality analysis — confirms whether price moves have institutional backing.

Indicators (all pure-Python, no external TA library):
  OBV  (On-Balance Volume) — cumulative; slope + divergence vs price
  CMF  (Chaikin Money Flow, 20-bar) — accumulation vs distribution
  RVOL (Relative Volume, 5D vs 20D) — recent activity vs baseline
  VWAP (52W anchored) — institutional benchmark reference price
  NR7 / NR4 — volatility contraction signals before breakout

  --period  yfinance period string for price history (default 6mo).
  --pretty  Render a Rich output panel instead of raw JSON.

Live data only — no training-knowledge values are ever used.
"""

from __future__ import annotations

import json
from datetime import date

import typer
import yfinance as yf
from rich import box
from rich.console import Console
from rich.table import Table

from market_sage._utils import _nse

app = typer.Typer(add_completion=False)
console = Console()


# ── Pure-math helpers ────────────────────────────────────────────────────────

def _obv(closes: list[float], volumes: list[int]) -> dict:
    """On-Balance Volume — cumulative volume with direction sign.

    OBV rises when each close is above the prior close (buying pressure) and falls
    on down-closes (selling pressure). Slope computed via plain-Python least-squares
    regression over the last 20 bars. Divergence detected when OBV and price slopes
    have opposite signs.
    """
    if len(closes) < 2 or len(volumes) < 2:
        return {"obv_last": 0, "obv_slope": 0.0, "obv_trend": "Flat", "obv_divergence": False}

    obv_series: list[float] = [0.0]
    for i in range(1, len(closes)):
        if closes[i] > closes[i - 1]:
            obv_series.append(obv_series[-1] + volumes[i])
        elif closes[i] < closes[i - 1]:
            obv_series.append(obv_series[-1] - volumes[i])
        else:
            obv_series.append(obv_series[-1])

    # Linear regression slope over last 20 bars (plain Python, no numpy/scipy)
    window = obv_series[-20:] if len(obv_series) >= 20 else obv_series
    n = len(window)
    x_mean = (n - 1) / 2.0
    y_mean = sum(window) / n
    num = sum((i - x_mean) * (window[i] - y_mean) for i in range(n))
    den = sum((i - x_mean) ** 2 for i in range(n))
    slope = num / den if den != 0 else 0.0

    # Price slope over the same window
    price_window = closes[-n:]
    p_mean = sum(price_window) / n
    p_num = sum((i - x_mean) * (price_window[i] - p_mean) for i in range(n))
    p_slope = p_num / den if den != 0 else 0.0

    # Divergence: OBV and price moving in opposite directions
    divergence = (slope > 0 and p_slope < 0) or (slope < 0 and p_slope > 0)

    return {
        "obv_last": int(obv_series[-1]),
        "obv_slope": round(slope, 2),
        "obv_trend": "Rising" if slope > 0 else ("Falling" if slope < 0 else "Flat"),
        "obv_divergence": divergence,
    }


def _cmf(
    highs: list[float],
    lows: list[float],
    closes: list[float],
    volumes: list[int],
    period: int = 20,
) -> float:
    """Chaikin Money Flow over `period` bars.

    CMF = Sum(MFV[-period:]) / Sum(Volume[-period:])
    where MFV = ((Close - Low) - (High - Close)) / (High - Low) × Volume
    Range: -1 to +1. Positive = accumulation; negative = distribution.
    Values above +0.05 signal buying pressure; below -0.05 signal selling.
    """
    if len(closes) < period or len(volumes) < period:
        return 0.0

    mfv: list[float] = []
    for i in range(len(closes)):
        hl = highs[i] - lows[i]
        if hl == 0:
            mfv.append(0.0)
        else:
            mfm = ((closes[i] - lows[i]) - (highs[i] - closes[i])) / hl
            mfv.append(mfm * volumes[i])

    period_mfv = sum(mfv[-period:])
    period_vol  = sum(volumes[-period:])
    return round(period_mfv / period_vol, 4) if period_vol else 0.0


def _rvol(volumes: list[int], short: int = 5, long: int = 20) -> float:
    """Relative Volume: average of last `short` sessions vs last `long` sessions.

    RVOL > 1.5 = above-average volume activity (institutional participation likely).
    RVOL < 0.7 = below-average (thin, unconvincing move).
    """
    if len(volumes) < long:
        return 1.0
    avg_short = sum(volumes[-short:]) / short
    avg_long  = sum(volumes[-long:])  / long
    return round(avg_short / avg_long, 2) if avg_long else 1.0


def _anchored_vwap(
    highs: list[float],
    lows: list[float],
    closes: list[float],
    volumes: list[int],
) -> float:
    """52-week anchored VWAP: weighted average of daily typical price × volume.

    Uses up to 252 bars (1 year). Typical price = (High + Low + Close) / 3.
    Serves as the institutional cost-basis reference for the past year.
    """
    # Use the last 252 bars or all available bars, whichever is smaller
    n = min(len(closes), 252)
    h = highs[-n:]
    l = lows[-n:]
    c = closes[-n:]
    v = volumes[-n:]

    tp_v_sum = sum(((h[i] + l[i] + c[i]) / 3) * v[i] for i in range(n))
    v_sum    = sum(v)
    return round(tp_v_sum / v_sum, 2) if v_sum else closes[-1]


def _nr7(highs: list[float], lows: list[float]) -> bool:
    """True when today's range (High - Low) is the narrowest of the last 7 bars.

    NR7 is a volatility contraction signal — compressed energy before a potential
    breakout. Common in Minervini's VCP (Volatility Contraction Pattern).
    Requires at least 7 bars.
    """
    if len(highs) < 7 or len(lows) < 7:
        return False
    ranges = [highs[i] - lows[i] for i in range(-7, 0)]
    return ranges[-1] == min(ranges)


def _nr4(highs: list[float], lows: list[float]) -> bool:
    """True when today's range is the narrowest of the last 4 bars."""
    if len(highs) < 4 or len(lows) < 4:
        return False
    ranges = [highs[i] - lows[i] for i in range(-4, 0)]
    return ranges[-1] == min(ranges)


def _volume_verdict(obv_data: dict, cmf: float, rvol: float) -> str:
    """Synthesise a one-line institutional activity verdict from OBV, CMF, RVOL."""
    obv_rising = obv_data.get("obv_trend") == "Rising"
    obv_falling = obv_data.get("obv_trend") == "Falling"
    divergence = obv_data.get("obv_divergence", False)

    if divergence:
        return "Divergence — OBV and price moving in opposite directions; caution"
    if obv_rising and cmf > 0.05 and rvol > 1.0:
        return "Strong institutional accumulation"
    if obv_rising and cmf > 0.0:
        return "Moderate accumulation — volume supports price"
    if obv_falling and cmf < -0.05:
        return "Distribution in progress — be cautious"
    if obv_falling and cmf < 0.0:
        return "Mild distribution — watch for trend exhaustion"
    return "Neutral — no clear institutional direction"


# ── Core analysis ─────────────────────────────────────────────────────────────

def analyze(symbol: str, period: str = "6mo") -> dict:
    """Fetch OHLCV and compute volume quality metrics for one NSE symbol.

    Returns a structured dict. On failure returns {"symbol": ..., "error": ...}.
    """
    ticker = _nse(symbol)

    try:
        hist = yf.Ticker(ticker).history(period=period)
    except Exception as exc:
        return {"symbol": symbol.upper(), "ticker": ticker, "error": f"fetch_failed: {exc}"}

    if hist is None or hist.empty:
        return {"symbol": symbol.upper(), "ticker": ticker, "error": "no_data"}

    hist = hist.dropna(subset=["High", "Low", "Close", "Volume"])
    if len(hist) < 20:
        return {
            "symbol": symbol.upper(),
            "ticker": ticker,
            "error": "insufficient_data",
            "bars": len(hist),
        }

    highs   = hist["High"].tolist()
    lows    = hist["Low"].tolist()
    closes  = hist["Close"].tolist()
    volumes = [int(v) for v in hist["Volume"].tolist()]

    obv_data  = _obv(closes, volumes)
    cmf_val   = _cmf(highs, lows, closes, volumes, period=20)
    rvol_val  = _rvol(volumes)
    vwap_val  = _anchored_vwap(highs, lows, closes, volumes)
    nr7_val   = _nr7(highs, lows)
    nr4_val   = _nr4(highs, lows)
    verdict   = _volume_verdict(obv_data, cmf_val, rvol_val)

    price_vs_vwap = "above" if closes[-1] > vwap_val else "below"

    cmf_signal = (
        "Buying pressure" if cmf_val > 0.05
        else ("Selling pressure" if cmf_val < -0.05 else "Neutral")
    )

    return {
        "symbol": symbol.upper(),
        "ticker": ticker,
        "obv_last": obv_data["obv_last"],
        "obv_slope": obv_data["obv_slope"],
        "obv_trend": obv_data["obv_trend"],
        "obv_divergence": obv_data["obv_divergence"],
        "cmf_20": cmf_val,
        "cmf_signal": cmf_signal,
        "rvol_5d": rvol_val,
        "vwap_52w": vwap_val,
        "price_vs_vwap": price_vs_vwap,
        "nr7_today": nr7_val,
        "nr4_today": nr4_val,
        "volume_verdict": verdict,
        "bars_analysed": len(closes),
        "source_date": date.today().isoformat(),
    }


# ── Pretty renderer ──────────────────────────────────────────────────────────

def _render_pretty(data: dict) -> None:
    if "error" in data:
        console.print(f"[red]Error for {data.get('symbol','?')}: {data['error']}[/red]")
        return

    sym = data.get("symbol", "?")
    console.print(f"\n[bold cyan]Volume Profile — {sym}[/bold cyan]")

    tbl = Table(box=box.SIMPLE, show_header=False, pad_edge=False)
    tbl.add_column("Metric", style="bold", width=25)
    tbl.add_column("Value",  width=20)
    tbl.add_column("Signal", width=35)

    obv_colour  = "green" if data["obv_trend"] == "Rising" else ("red" if data["obv_trend"] == "Falling" else "yellow")
    div_str     = "[red]YES — DIVERGENCE[/red]" if data["obv_divergence"] else "[green]No[/green]"
    cmf_colour  = "green" if data["cmf_20"] > 0.05 else ("red" if data["cmf_20"] < -0.05 else "yellow")
    rvol_colour = "green" if data["rvol_5d"] > 1.2 else ("red" if data["rvol_5d"] < 0.8 else "yellow")
    vwap_colour = "green" if data["price_vs_vwap"] == "above" else "red"
    nr7_str     = "[bold yellow]YES — Volatility Coil[/bold yellow]" if data["nr7_today"] else "No"
    nr4_str     = "[yellow]YES[/yellow]" if data["nr4_today"] else "No"

    tbl.add_row("OBV Trend",       f"[{obv_colour}]{data['obv_trend']}[/{obv_colour}]",  "")
    tbl.add_row("OBV Slope",       str(data["obv_slope"]),                                "")
    tbl.add_row("OBV Divergence",  div_str,                                               "Price/OBV move in opposite directions")
    tbl.add_row("CMF (20-bar)",    f"[{cmf_colour}]{data['cmf_20']:+.4f}[/{cmf_colour}]", data["cmf_signal"])
    tbl.add_row("RVOL (5D/20D)",   f"[{rvol_colour}]{data['rvol_5d']:.2f}x[/{rvol_colour}]",
                "High volume" if data["rvol_5d"] > 1.5 else ("Low volume" if data["rvol_5d"] < 0.7 else "Normal volume"))
    tbl.add_row("VWAP (52W)",      f"₹{data['vwap_52w']:,.2f}",                          "")
    tbl.add_row("Price vs VWAP",   f"[{vwap_colour}]{data['price_vs_vwap'].upper()}[/{vwap_colour}]", "")
    tbl.add_row("NR7 today",       nr7_str,                                               "Narrowest range of last 7 bars")
    tbl.add_row("NR4 today",       nr4_str,                                               "Narrowest range of last 4 bars")

    console.print(tbl)

    verdict = data.get("volume_verdict", "")
    verdict_colour = "green" if "accumulation" in verdict.lower() else ("red" if "distribution" in verdict.lower() or "caution" in verdict.lower() else "yellow")
    console.print(f"\n[bold {verdict_colour}]VERDICT: {verdict}[/bold {verdict_colour}]")
    console.print(f"[dim]Source: yfinance | {data.get('bars_analysed', '?')} bars | Date: {data.get('source_date', '?')}[/dim]")


# ── CLI ───────────────────────────────────────────────────────────────────────

@app.command()
def main(
    symbol: str = typer.Argument(..., help="NSE symbol (e.g. KAYNES, HDFCBANK)"),
    period: str = typer.Option("6mo", "--period", help="yfinance period string (e.g. 6mo, 1y, 2y)"),
    pretty: bool = typer.Option(False, "--pretty", help="Render Rich output panel"),
) -> None:
    """Volume quality analysis — OBV, CMF, RVOL, VWAP, NR7/NR4."""
    data = analyze(symbol, period=period)
    if pretty:
        _render_pretty(data)
    else:
        console.print(json.dumps(data, indent=2))
