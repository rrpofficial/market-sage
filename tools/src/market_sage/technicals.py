"""
ms-technicals SYMBOL [--period 1y] [--pretty]

Fetches OHLCV data via yfinance and computes:
  DMAs (20/50/200), RSI(14), MACD(12,26,9), Bollinger Bands(20,2),
  ATR(14), ADX(14) with DI+/DI-, Stochastic(14,3), Supertrend(7, 3xATR),
  Parabolic SAR, Fibonacci retracement/extension levels, Weinstein Stage
  Analysis (1-4), Minervini SEPA Trend Template (8 conditions),
  support/resistance levels, volume profile, and a technical verdict.
Outputs JSON by default; --pretty renders Rich tables.
Use --period 2y for Stage Analysis and SEPA (both need 150-221+ bars).
"""

from __future__ import annotations

import json
from datetime import date
from typing import Optional

import polars as pl
import typer
import yfinance as yf
from rich.console import Console
from rich.table import Table

app = typer.Typer(add_completion=False)
console = Console()


def _nse(symbol: str) -> str:
    s = symbol.upper().strip()
    return s if s.endswith((".NS", ".BO")) else s + ".NS"


# ── Pure-math indicator implementations (no extra deps beyond polars) ──────────

def _ema(series: list[float], span: int) -> list[float]:
    k = 2 / (span + 1)
    result = [series[0]]
    for v in series[1:]:
        result.append(v * k + result[-1] * (1 - k))
    return result


def _rsi(closes: list[float], period: int = 14) -> float:
    deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    gains = [max(d, 0.0) for d in deltas]
    losses = [max(-d, 0.0) for d in deltas]
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
    rs = avg_gain / avg_loss if avg_loss else float("inf")
    return round(100 - 100 / (1 + rs), 2)


def _macd(closes: list[float]) -> tuple[float, float, float]:
    ema12 = _ema(closes, 12)
    ema26 = _ema(closes, 26)
    macd_line = [a - b for a, b in zip(ema12, ema26)]
    signal = _ema(macd_line, 9)
    histogram = [m - s for m, s in zip(macd_line, signal)]
    return round(macd_line[-1], 4), round(signal[-1], 4), round(histogram[-1], 4)


def _bollinger(closes: list[float], period: int = 20, std_dev: float = 2.0) -> dict:
    window = closes[-period:]
    mid = sum(window) / period
    variance = sum((x - mid) ** 2 for x in window) / period
    std = variance ** 0.5
    return {
        "upper": round(mid + std_dev * std, 2),
        "middle": round(mid, 2),
        "lower": round(mid - std_dev * std, 2),
    }


def _true_range(highs: list[float], lows: list[float], closes: list[float]) -> list[float]:
    trs = []
    for i in range(1, len(closes)):
        tr = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i - 1]),
            abs(lows[i] - closes[i - 1]),
        )
        trs.append(tr)
    return trs


def _atr(highs: list[float], lows: list[float], closes: list[float], period: int = 14) -> float:
    trs = _true_range(highs, lows, closes)
    atr = sum(trs[:period]) / period
    for tr in trs[period:]:
        atr = (atr * (period - 1) + tr) / period
    return round(atr, 2)


def _wilder_smooth(series: list[float], period: int) -> list[float]:
    """Wilder's smoothed sum (not the 2/(span+1) EMA): seeded with the sum of the
    first `period` values, then smoothed[i] = smoothed[i-1] - smoothed[i-1]/period + current[i]."""
    smoothed = [sum(series[:period])]
    for v in series[period:]:
        smoothed.append(smoothed[-1] - smoothed[-1] / period + v)
    return smoothed


def _adx(highs: list[float], lows: list[float], closes: list[float], period: int = 14) -> dict:
    if len(closes) < 2 * period + 1:
        return {"adx": None, "di_plus": None, "di_minus": None,
                "trend_strength": "insufficient_data", "di_signal": None}

    trs = _true_range(highs, lows, closes)
    plus_dm: list[float] = []
    minus_dm: list[float] = []
    for i in range(1, len(closes)):
        up_move = highs[i] - highs[i - 1]
        down_move = lows[i - 1] - lows[i]
        plus_dm.append(up_move if up_move > down_move and up_move > 0 else 0.0)
        minus_dm.append(down_move if down_move > up_move and down_move > 0 else 0.0)

    sm_tr = _wilder_smooth(trs, period)
    sm_plus = _wilder_smooth(plus_dm, period)
    sm_minus = _wilder_smooth(minus_dm, period)

    di_plus = [100 * p / t if t else 0.0 for p, t in zip(sm_plus, sm_tr)]
    di_minus = [100 * m / t if t else 0.0 for m, t in zip(sm_minus, sm_tr)]
    dx = [100 * abs(p - m) / (p + m) if (p + m) else 0.0 for p, m in zip(di_plus, di_minus)]

    adx_series = [sum(dx[:period]) / period]
    for d in dx[period:]:
        adx_series.append((adx_series[-1] * (period - 1) + d) / period)

    adx = adx_series[-1]
    return {
        "adx": round(adx, 2),
        "di_plus": round(di_plus[-1], 2),
        "di_minus": round(di_minus[-1], 2),
        "trend_strength": "strong" if adx > 25 else ("developing" if adx > 20 else "choppy"),
        "di_signal": "bullish" if di_plus[-1] > di_minus[-1] else "bearish",
    }


def _stochastic(highs: list[float], lows: list[float], closes: list[float], k: int = 14, d: int = 3) -> dict:
    if len(closes) < k + d - 1:
        return {"k_pct": None, "d_pct": None, "signal": "insufficient_data"}

    k_values = []
    for i in range(k - 1, len(closes)):
        window_high = max(highs[i - k + 1 : i + 1])
        window_low = min(lows[i - k + 1 : i + 1])
        denom = window_high - window_low
        k_val = 100 * (closes[i] - window_low) / denom if denom else 50.0
        k_values.append(k_val)
    d_values = [sum(k_values[i - d + 1 : i + 1]) / d for i in range(d - 1, len(k_values))]

    k_last = k_values[-1]
    return {
        "k_pct": round(k_last, 2),
        "d_pct": round(d_values[-1], 2),
        "signal": "overbought" if k_last > 80 else ("oversold" if k_last < 20 else "neutral"),
    }


def _supertrend(highs: list[float], lows: list[float], closes: list[float],
                period: int = 7, multiplier: float = 3.0) -> dict:
    if len(closes) < period + 2:
        return {"supertrend": None, "direction": None, "distance_pct": None}

    trs = _true_range(highs, lows, closes)
    # Rolling Wilder ATR series; atrs[j] corresponds to bar index j + period
    atrs = [sum(trs[:period]) / period]
    for tr in trs[period:]:
        atrs.append((atrs[-1] * (period - 1) + tr) / period)

    final_ub: float | None = None
    final_lb: float | None = None
    direction = 1
    st_value = closes[-1]
    for j, atr in enumerate(atrs):
        i = j + period
        mid = (highs[i] + lows[i]) / 2
        basic_ub = mid + multiplier * atr
        basic_lb = mid - multiplier * atr
        if final_ub is None or final_lb is None:
            final_ub, final_lb = basic_ub, basic_lb
        else:
            # Bands ratchet: only tighten unless price closed beyond them
            final_ub = basic_ub if (basic_ub < final_ub or closes[i - 1] > final_ub) else final_ub
            final_lb = basic_lb if (basic_lb > final_lb or closes[i - 1] < final_lb) else final_lb
        if direction == 1 and closes[i] < final_lb:
            direction = -1
        elif direction == -1 and closes[i] > final_ub:
            direction = 1
        st_value = final_lb if direction == 1 else final_ub

    return {
        "supertrend": round(st_value, 2),
        "direction": "bullish" if direction == 1 else "bearish",
        "distance_pct": round((closes[-1] - st_value) / closes[-1] * 100, 2),
    }


def _parabolic_sar(highs: list[float], lows: list[float], closes: list[float],
                   initial_af: float = 0.02, max_af: float = 0.20) -> dict:
    if len(closes) < 5:
        return {"sar": None, "trend": None, "distance_pct": None}

    bullish = True
    sar = lows[0]
    ep = highs[0]
    af = initial_af
    for i in range(1, len(closes)):
        sar = sar + af * (ep - sar)
        if bullish:
            # SAR must not enter the prior two bars' range
            sar = min(sar, lows[i - 1], lows[i - 2] if i >= 2 else lows[i - 1])
            if lows[i] < sar:
                bullish = False
                sar = ep
                ep = lows[i]
                af = initial_af
            elif highs[i] > ep:
                ep = highs[i]
                af = min(af + initial_af, max_af)
        else:
            sar = max(sar, highs[i - 1], highs[i - 2] if i >= 2 else highs[i - 1])
            if highs[i] > sar:
                bullish = True
                sar = ep
                ep = highs[i]
                af = initial_af
            elif lows[i] < ep:
                ep = lows[i]
                af = min(af + initial_af, max_af)

    return {
        "sar": round(sar, 2),
        "trend": "bullish" if bullish else "bearish",
        "distance_pct": round((closes[-1] - sar) / closes[-1] * 100, 2),
    }


def _fibonacci_levels(highs: list[float], lows: list[float], closes: list[float], lookback: int = 60) -> dict:
    swing_high = max(highs[-lookback:])
    swing_low = min(lows[-lookback:])
    diff = swing_high - swing_low
    if diff <= 0:
        return {"swing_high": round(swing_high, 2), "swing_low": round(swing_low, 2),
                "error": "flat_range"}

    pullback_depth_pct = round((swing_high - closes[-1]) / diff * 100, 1)
    if pullback_depth_pct < 38.2:
        pullback_class = "shallow"
    elif pullback_depth_pct <= 61.8:
        pullback_class = "normal"
    else:
        pullback_class = "deep"

    return {
        "swing_high": round(swing_high, 2),
        "swing_low": round(swing_low, 2),
        "retracements": {
            "r_23_6": round(swing_high - 0.236 * diff, 2),
            "r_38_2": round(swing_high - 0.382 * diff, 2),
            "r_50_0": round(swing_high - 0.500 * diff, 2),
            "r_61_8": round(swing_high - 0.618 * diff, 2),
            "r_78_6": round(swing_high - 0.786 * diff, 2),
        },
        "extensions": {
            "e_127_2": round(swing_high + 0.272 * diff, 2),
            "e_161_8": round(swing_high + 0.618 * diff, 2),
            "e_200_0": round(swing_high + 1.000 * diff, 2),
        },
        "pullback_depth_pct": pullback_depth_pct,
        "pullback_class": pullback_class,
    }


def _weinstein_stage(closes: list[float], highs: list[float], lows: list[float],
                     volumes: list[float]) -> dict:
    if len(closes) < 150:
        return {"stage": None, "stage_label": "insufficient_data (need >= 150 bars)",
                "dma_150": None, "dma_150_trending_up": None, "action": None}

    dma_150 = sum(closes[-150:]) / 150
    dma_150_21d_ago = sum(closes[-171:-21]) / 150 if len(closes) >= 171 else None
    dma_150_trending_up = (dma_150 > dma_150_21d_ago) if dma_150_21d_ago else None
    slope_pct = (
        round((dma_150 - dma_150_21d_ago) / dma_150_21d_ago * 100, 2)
        if dma_150_21d_ago else None
    )

    ltp = closes[-1]
    within_5pct = abs(ltp - dma_150) / dma_150 <= 0.05
    near_flat = dma_150_trending_up is None or (slope_pct is not None and abs(slope_pct) < 1.0)

    # First match wins
    if ltp > dma_150 and dma_150_trending_up:
        stage, label, action = 2, "Markup — BUY zone", "BUY"
    elif ltp < dma_150 and dma_150_trending_up is False and not (within_5pct and near_flat):
        stage, label, action = 4, "Decline — never buy", "AVOID"
    elif within_5pct and near_flat:
        stage, label, action = 1, "Base — watch only", "WATCH"
    elif ltp >= dma_150 and dma_150_trending_up is False:
        stage, label, action = 3, "Top — distribution, exit/avoid new entries", "SELL/AVOID"
    else:
        # e.g. deep pullback below a still-rising 150 DMA — treat as base/transition
        stage, label, action = 1, "Base/Transition — watch only", "WATCH"

    avg_vol_20 = sum(volumes[-20:]) / 20 if len(volumes) >= 20 else None
    avg_vol_50 = sum(volumes[-50:]) / 50 if len(volumes) >= 50 else None
    volume_expanding = (avg_vol_20 > avg_vol_50) if (avg_vol_20 and avg_vol_50) else None

    return {
        "stage": stage,
        "stage_label": label,
        "dma_150": round(dma_150, 2),
        "dma_150_trending_up": dma_150_trending_up,
        "dma_150_slope_pct": slope_pct,
        "volume_expanding": volume_expanding,
        "action": action,
    }


def _sepa_template(ltp: float, closes: list[float], highs: list[float], lows: list[float],
                   rs_rating: float | None = None) -> dict:
    dma_50 = sum(closes[-50:]) / 50 if len(closes) >= 50 else None
    dma_150 = sum(closes[-150:]) / 150 if len(closes) >= 150 else None
    dma_200 = sum(closes[-200:]) / 200 if len(closes) >= 200 else None
    w52_high = max(highs[-252:]) if len(highs) >= 252 else max(highs)
    w52_low = min(lows[-252:]) if len(lows) >= 252 else min(lows)
    dma_200_21d_ago = sum(closes[-221:-21]) / 200 if len(closes) >= 221 else None

    conditions: dict[str, bool | None] = {
        "price_above_150_200dma": (ltp > dma_150 and ltp > dma_200) if (dma_150 and dma_200) else None,
        "150dma_above_200dma": (dma_150 > dma_200) if (dma_150 and dma_200) else None,
        "200dma_trending_up_1m": (dma_200 > dma_200_21d_ago) if (dma_200 and dma_200_21d_ago) else None,
        "50dma_above_150_200dma": (dma_50 > dma_150 and dma_50 > dma_200) if (dma_50 and dma_150 and dma_200) else None,
        "price_above_50dma": (ltp > dma_50) if dma_50 else None,
        "price_30pct_above_52w_low": ltp >= w52_low * 1.30,
        "price_within_25pct_of_52w_high": ltp >= w52_high * 0.75,
        "rs_rating_70plus": (rs_rating >= 70) if rs_rating is not None else None,
    }

    conditions_met = sum(1 for c in conditions.values() if c is True)
    return {
        "conditions": conditions,
        "conditions_met": conditions_met,
        "sepa_score": round(conditions_met / 8 * 15, 1),
        "failed_conditions": [k for k, v in conditions.items() if v is False],
        "data_gaps": [k for k, v in conditions.items() if v is None],
        # Minervini recommends 7/8 minimum; 6/8 used as the qualifying threshold here
        "qualifies": conditions_met >= 6,
    }


def _support_resistance(highs: list[float], lows: list[float], closes: list[float]) -> dict:
    """Derive S/R from recent swing highs/lows and 52W range."""
    recent_highs = sorted(highs[-60:], reverse=True)
    recent_lows = sorted(lows[-60:])
    r1 = round(recent_highs[5], 2) if len(recent_highs) > 5 else round(max(highs[-20:]), 2)
    r2 = round(recent_highs[0], 2)
    s1 = round(recent_lows[5], 2) if len(recent_lows) > 5 else round(min(lows[-20:]), 2)
    s2 = round(recent_lows[0], 2)
    return {
        "resistance_2": r2,
        "resistance_1": r1,
        "support_1": s1,
        "support_2": s2,
    }


def _technical_verdict(rsi: float, macd_h: float, dma_50: float, dma_200: float, ltp: float) -> dict:
    signals = []
    if ltp > dma_200:
        signals.append("above_200dma")
    else:
        signals.append("below_200dma")
    if dma_50 > dma_200:
        signals.append("golden_cross")
    else:
        signals.append("death_cross")
    if rsi > 70:
        signals.append("overbought_rsi")
    elif rsi < 30:
        signals.append("oversold_rsi")
    else:
        signals.append("neutral_rsi")
    if macd_h > 0:
        signals.append("macd_bullish")
    else:
        signals.append("macd_bearish")

    bull_count = sum(1 for s in signals if s in ("above_200dma", "golden_cross", "oversold_rsi", "macd_bullish"))
    bear_count = sum(1 for s in signals if s in ("below_200dma", "death_cross", "overbought_rsi", "macd_bearish"))

    if bull_count >= 3:
        short_term = "Bullish"
    elif bear_count >= 3:
        short_term = "Bearish"
    else:
        short_term = "Neutral"

    return {
        "short_term": short_term,
        "signals": signals,
        "note": "Technical analysis is secondary to fundamentals for long-term investors. Use for entry timing only.",
    }


def analyze(symbol: str, period: str = "1y", rs_rating: float | None = None) -> dict:
    ticker = _nse(symbol)
    t = yf.Ticker(ticker)
    hist = t.history(period=period)

    if hist.empty:
        return {"symbol": symbol, "error": "no_data"}

    # yfinance can return NaN bars (trading halts, F&O ban days) that poison the math
    hist = hist.dropna(subset=["High", "Low", "Close"])
    if hist.empty:
        return {"symbol": symbol, "error": "no_data"}

    closes = hist["Close"].tolist()
    highs = hist["High"].tolist()
    lows = hist["Low"].tolist()
    volumes = hist["Volume"].tolist()

    if len(closes) < 30:
        return {"symbol": symbol, "error": "insufficient_data", "bars": len(closes)}

    ltp = closes[-1]

    dma_20 = round(sum(closes[-20:]) / 20, 2)
    dma_50 = round(sum(closes[-50:]) / 50, 2) if len(closes) >= 50 else None
    dma_200 = round(sum(closes[-200:]) / 200, 2) if len(closes) >= 200 else None

    rsi = _rsi(closes)
    macd_line, macd_signal, macd_histogram = _macd(closes)
    bb = _bollinger(closes)
    atr = _atr(highs, lows, closes)
    sr = _support_resistance(highs, lows, closes)

    avg_vol_20 = int(sum(volumes[-20:]) / 20)
    avg_vol_50 = int(sum(volumes[-50:]) / 50) if len(volumes) >= 50 else None

    dma_signals = {}
    if dma_50:
        dma_signals["vs_50dma"] = "above" if ltp > dma_50 else "below"
    if dma_200:
        dma_signals["vs_200dma"] = "above" if ltp > dma_200 else "below"
    if dma_50 and dma_200:
        dma_signals["cross"] = "golden" if dma_50 > dma_200 else "death"

    verdict = _technical_verdict(rsi, macd_histogram, dma_50 or ltp, dma_200 or ltp, ltp)

    return {
        "symbol": symbol.upper(),
        "ticker": ticker,
        "ltp": round(ltp, 2),
        "source_date": date.today().isoformat(),
        "moving_averages": {
            "dma_20": dma_20,
            "dma_50": dma_50,
            "dma_200": dma_200,
            **dma_signals,
        },
        "rsi_14": rsi,
        "macd": {
            "macd_line": macd_line,
            "signal_line": macd_signal,
            "histogram": macd_histogram,
            "signal": "bullish" if macd_histogram > 0 else "bearish",
        },
        "bollinger_bands_20_2": bb,
        "atr_14": atr,
        "adx": _adx(highs, lows, closes),
        "stochastic": _stochastic(highs, lows, closes),
        "supertrend": _supertrend(highs, lows, closes),
        "parabolic_sar": _parabolic_sar(highs, lows, closes),
        "fibonacci": _fibonacci_levels(highs, lows, closes),
        "weinstein_stage": _weinstein_stage(closes, highs, lows, volumes),
        "sepa_template": _sepa_template(ltp, closes, highs, lows, rs_rating=rs_rating),
        "support_resistance": sr,
        "volume": {
            "avg_20d": avg_vol_20,
            "avg_50d": avg_vol_50,
            "last_bar": int(volumes[-1]),
            "vs_20d_avg": round(volumes[-1] / avg_vol_20, 2) if avg_vol_20 else None,
        },
        "verdict": verdict,
    }


def _render_pretty(data: dict) -> None:
    if "error" in data:
        console.print(f"[red]Error for {data['symbol']}: {data['error']}[/red]")
        return

    console.rule(f"[bold cyan]{data['symbol']} — Technical Analysis[/bold cyan]")
    console.print(f"LTP: ₹{data['ltp']:,.2f}  |  Date: {data['source_date']}\n")

    ma = data["moving_averages"]
    t = Table(title="Moving Averages", header_style="bold cyan")
    t.add_column("Indicator", style="cyan")
    t.add_column("Value", justify="right")
    t.add_column("Signal", justify="center")
    ltp = data["ltp"]
    for label, val in [("DMA 20", ma.get("dma_20")), ("DMA 50", ma.get("dma_50")), ("DMA 200", ma.get("dma_200"))]:
        if val:
            sig = "[green]Above[/green]" if ltp > val else "[red]Below[/red]"
            t.add_row(label, f"₹{val:,.2f}", sig)
    if "cross" in ma:
        t.add_row("50/200 Cross", "", f"[{'green' if ma['cross'] == 'golden' else 'red'}]{ma['cross'].title()} Cross[/]")
    console.print(t)

    rsi = data["rsi_14"]
    rsi_col = "[red]Overbought[/red]" if rsi > 70 else ("[green]Oversold[/green]" if rsi < 30 else "Neutral")
    console.print(f"\nRSI(14): [bold]{rsi}[/bold]  → {rsi_col}")

    macd = data["macd"]
    macd_col = "[green]Bullish[/green]" if macd["histogram"] > 0 else "[red]Bearish[/red]"
    console.print(f"MACD: {macd['macd_line']:.4f}  Signal: {macd['signal_line']:.4f}  Hist: {macd['histogram']:.4f}  → {macd_col}")

    adx = data.get("adx", {})
    if adx.get("adx") is not None:
        strength_col = {"strong": "green", "developing": "yellow", "choppy": "red"}.get(adx["trend_strength"], "white")
        di_col = "green" if adx["di_signal"] == "bullish" else "red"
        console.print(
            f"ADX(14): [bold]{adx['adx']}[/bold] ([{strength_col}]{adx['trend_strength']}[/]) "
            f" DI+: {adx['di_plus']}  DI-: {adx['di_minus']}  → [{di_col}]{adx['di_signal']}[/]"
        )

    stoch = data.get("stochastic", {})
    if stoch.get("k_pct") is not None:
        st_col = "[red]Overbought[/red]" if stoch["signal"] == "overbought" else (
            "[green]Oversold[/green]" if stoch["signal"] == "oversold" else "Neutral")
        console.print(f"Stochastic(14,3): %K {stoch['k_pct']}  %D {stoch['d_pct']}  → {st_col}")

    st = data.get("supertrend", {})
    if st.get("supertrend") is not None:
        st_dir_col = "green" if st["direction"] == "bullish" else "red"
        console.print(f"Supertrend(7,3): ₹{st['supertrend']:,.2f}  → [{st_dir_col}]{st['direction']}[/] ({st['distance_pct']}% from price)")

    psar = data.get("parabolic_sar", {})
    if psar.get("sar") is not None:
        sar_col = "green" if psar["trend"] == "bullish" else "red"
        console.print(f"Parabolic SAR: ₹{psar['sar']:,.2f}  → [{sar_col}]{psar['trend']}[/]")

    fib = data.get("fibonacci", {})
    if fib and "error" not in fib:
        t = Table(title=f"Fibonacci Levels (swing ₹{fib['swing_low']:,.2f} → ₹{fib['swing_high']:,.2f})", header_style="bold cyan")
        t.add_column("Level", style="cyan")
        t.add_column("Price", justify="right")
        for label, key in [("Retr 23.6%", "r_23_6"), ("Retr 38.2%", "r_38_2"), ("Retr 50.0%", "r_50_0"),
                           ("Retr 61.8%", "r_61_8"), ("Retr 78.6%", "r_78_6")]:
            t.add_row(label, f"₹{fib['retracements'][key]:,.2f}")
        for label, key in [("Ext 127.2%", "e_127_2"), ("Ext 161.8%", "e_161_8"), ("Ext 200.0%", "e_200_0")]:
            t.add_row(label, f"₹{fib['extensions'][key]:,.2f}")
        console.print()
        console.print(t)
        console.print(f"Pullback depth: {fib['pullback_depth_pct']}% from swing high → [bold]{fib['pullback_class']}[/bold]")

    stage = data.get("weinstein_stage", {})
    if stage.get("stage") is not None:
        stage_col = {2: "green", 1: "yellow", 3: "yellow", 4: "red"}.get(stage["stage"], "white")
        console.print(
            f"\n[bold {stage_col}]Weinstein Stage {stage['stage']}: {stage['stage_label']}[/bold {stage_col}]"
            f"  (150 DMA ₹{stage['dma_150']:,.2f}, "
            f"{'rising' if stage['dma_150_trending_up'] else 'falling/flat'})  → Action: {stage['action']}"
        )

    sepa = data.get("sepa_template", {})
    if sepa:
        t = Table(title=f"SEPA Trend Template — {sepa['conditions_met']}/8 met "
                        f"({'QUALIFIES' if sepa['qualifies'] else 'does not qualify'})",
                  header_style="bold cyan")
        t.add_column("Condition", style="cyan")
        t.add_column("Status", justify="center")
        for name, status in sepa["conditions"].items():
            mark = "[green]✓[/green]" if status is True else ("[red]✗[/red]" if status is False else "[dim]n/a[/dim]")
            t.add_row(name.replace("_", " "), mark)
        console.print()
        console.print(t)

    sr = data["support_resistance"]
    console.print(f"\nR2: ₹{sr['resistance_2']:,.2f}  R1: ₹{sr['resistance_1']:,.2f}")
    console.print(f"[bold]LTP: ₹{ltp:,.2f}[/bold]")
    console.print(f"S1: ₹{sr['support_1']:,.2f}  S2: ₹{sr['support_2']:,.2f}")

    v = data["verdict"]
    console.print(f"\n[bold]Verdict:[/bold] {v['short_term']}  |  {', '.join(v['signals'])}")


@app.command()
def main(
    symbol: str = typer.Argument(..., help="NSE symbol, e.g. KAYNES"),
    period: str = typer.Option("1y", "--period", help="History period: 6mo, 1y, 2y (default 1y)"),
    pretty: bool = typer.Option(False, "--pretty", help="Render Rich tables instead of JSON"),
) -> None:
    result = analyze(symbol, period)
    if pretty:
        _render_pretty(result)
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    app()
