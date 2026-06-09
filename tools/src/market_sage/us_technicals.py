"""
ms-us-technicals TICKER [--period 1y] [--pretty]

Fetches OHLCV data via yfinance and computes technical indicators
for US stocks and ETFs:
  DMAs (20/50/200), RSI(14), MACD(12,26,9), Bollinger Bands(20,2),
  ATR(14), support/resistance levels, volume profile, and a verdict.

Tickers are used as-is — no exchange suffix appended.
Examples: AAPL, MSFT, SPY, QQQ, NVDA

Outputs JSON by default; --pretty renders Rich tables.
"""

from __future__ import annotations

import json
from datetime import date

import typer
import yfinance as yf
from rich.console import Console
from rich.table import Table

app = typer.Typer(add_completion=False)
console = Console()


# ── Pure-math indicator implementations ───────────────────────────────────────

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


def _atr(highs: list[float], lows: list[float], closes: list[float], period: int = 14) -> float:
    trs = []
    for i in range(1, len(closes)):
        tr = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i - 1]),
            abs(lows[i] - closes[i - 1]),
        )
        trs.append(tr)
    atr_vals = trs[:period]
    atr = sum(atr_vals) / period
    for tr in trs[period:]:
        atr = (atr * (period - 1) + tr) / period
    return round(atr, 2)


def _support_resistance(highs: list[float], lows: list[float]) -> dict:
    recent_highs = sorted(highs[-60:], reverse=True)
    recent_lows = sorted(lows[-60:])
    r1 = round(recent_highs[5], 2) if len(recent_highs) > 5 else round(max(highs[-20:]), 2)
    r2 = round(recent_highs[0], 2)
    s1 = round(recent_lows[5], 2) if len(recent_lows) > 5 else round(min(lows[-20:]), 2)
    s2 = round(recent_lows[0], 2)
    return {"resistance_2": r2, "resistance_1": r1, "support_1": s1, "support_2": s2}


def _verdict(rsi: float, macd_h: float, dma_50: float, dma_200: float, ltp: float) -> dict:
    signals = []
    signals.append("above_200dma" if ltp > dma_200 else "below_200dma")
    signals.append("golden_cross" if dma_50 > dma_200 else "death_cross")
    if rsi > 70:
        signals.append("overbought_rsi")
    elif rsi < 30:
        signals.append("oversold_rsi")
    else:
        signals.append("neutral_rsi")
    signals.append("macd_bullish" if macd_h > 0 else "macd_bearish")

    bull = sum(1 for s in signals if s in ("above_200dma", "golden_cross", "oversold_rsi", "macd_bullish"))
    bear = sum(1 for s in signals if s in ("below_200dma", "death_cross", "overbought_rsi", "macd_bearish"))

    short_term = "Bullish" if bull >= 3 else ("Bearish" if bear >= 3 else "Neutral")
    return {
        "short_term": short_term,
        "signals": signals,
        "note": "Technical analysis is secondary to fundamentals for long-term investors.",
    }


def analyze(ticker: str, period: str = "1y") -> dict:
    t = yf.Ticker(ticker.upper().strip())
    hist = t.history(period=period)

    if hist.empty:
        return {"ticker": ticker.upper(), "error": "no_data"}

    closes = hist["Close"].tolist()
    highs = hist["High"].tolist()
    lows = hist["Low"].tolist()
    volumes = hist["Volume"].tolist()

    if len(closes) < 30:
        return {"ticker": ticker.upper(), "error": "insufficient_data", "bars": len(closes)}

    ltp = closes[-1]
    dma_20 = round(sum(closes[-20:]) / 20, 2)
    dma_50 = round(sum(closes[-50:]) / 50, 2) if len(closes) >= 50 else None
    dma_200 = round(sum(closes[-200:]) / 200, 2) if len(closes) >= 200 else None

    rsi = _rsi(closes)
    macd_line, macd_signal, macd_histogram = _macd(closes)
    bb = _bollinger(closes)
    atr = _atr(highs, lows, closes)
    sr = _support_resistance(highs, lows)

    avg_vol_20 = int(sum(volumes[-20:]) / 20)
    avg_vol_50 = int(sum(volumes[-50:]) / 50) if len(volumes) >= 50 else None

    dma_signals: dict = {}
    if dma_50:
        dma_signals["vs_50dma"] = "above" if ltp > dma_50 else "below"
    if dma_200:
        dma_signals["vs_200dma"] = "above" if ltp > dma_200 else "below"
    if dma_50 and dma_200:
        dma_signals["cross"] = "golden" if dma_50 > dma_200 else "death"

    v = _verdict(rsi, macd_histogram, dma_50 or ltp, dma_200 or ltp, ltp)

    return {
        "ticker": ticker.upper(),
        "price": round(ltp, 2),
        "currency": "USD",
        "source_date": date.today().isoformat(),
        "moving_averages": {"dma_20": dma_20, "dma_50": dma_50, "dma_200": dma_200, **dma_signals},
        "rsi_14": rsi,
        "macd": {
            "macd_line": macd_line,
            "signal_line": macd_signal,
            "histogram": macd_histogram,
            "signal": "bullish" if macd_histogram > 0 else "bearish",
        },
        "bollinger_bands_20_2": bb,
        "atr_14": atr,
        "support_resistance": sr,
        "volume": {
            "avg_20d": avg_vol_20,
            "avg_50d": avg_vol_50,
            "last_bar": int(volumes[-1]),
            "vs_20d_avg": round(volumes[-1] / avg_vol_20, 2) if avg_vol_20 else None,
        },
        "verdict": v,
    }


def _render_pretty(data: dict) -> None:
    if "error" in data:
        console.print(f"[red]Error for {data['ticker']}: {data['error']}[/red]")
        return

    console.rule(f"[bold cyan]{data['ticker']} — US Technical Analysis[/bold cyan]")
    console.print(f"Price: ${data['price']:,.2f}  |  Date: {data['source_date']}\n")

    ma = data["moving_averages"]
    t = Table(title="Moving Averages", header_style="bold cyan")
    t.add_column("Indicator", style="cyan")
    t.add_column("Value", justify="right")
    t.add_column("Signal", justify="center")
    ltp = data["price"]
    for label, val in [("DMA 20", ma.get("dma_20")), ("DMA 50", ma.get("dma_50")), ("DMA 200", ma.get("dma_200"))]:
        if val:
            sig = "[green]Above[/green]" if ltp > val else "[red]Below[/red]"
            t.add_row(label, f"${val:,.2f}", sig)
    if "cross" in ma:
        color = "green" if ma["cross"] == "golden" else "red"
        t.add_row("50/200 Cross", "", f"[{color}]{ma['cross'].title()} Cross[/]")
    console.print(t)

    rsi = data["rsi_14"]
    rsi_col = "[red]Overbought[/red]" if rsi > 70 else ("[green]Oversold[/green]" if rsi < 30 else "Neutral")
    console.print(f"\nRSI(14): [bold]{rsi}[/bold]  → {rsi_col}")

    macd = data["macd"]
    macd_col = "[green]Bullish[/green]" if macd["histogram"] > 0 else "[red]Bearish[/red]"
    console.print(f"MACD: {macd['macd_line']:.4f}  Signal: {macd['signal_line']:.4f}  Hist: {macd['histogram']:.4f}  → {macd_col}")

    sr = data["support_resistance"]
    console.print(f"\nR2: ${sr['resistance_2']:,.2f}  R1: ${sr['resistance_1']:,.2f}")
    console.print(f"[bold]Price: ${ltp:,.2f}[/bold]")
    console.print(f"S1: ${sr['support_1']:,.2f}  S2: ${sr['support_2']:,.2f}")

    v = data["verdict"]
    console.print(f"\n[bold]Verdict:[/bold] {v['short_term']}  |  {', '.join(v['signals'])}")


@app.command()
def main(
    ticker: str = typer.Argument(..., help="US ticker, e.g. AAPL MSFT SPY"),
    period: str = typer.Option("1y", "--period", help="History period: 6mo, 1y, 2y (default 1y)"),
    pretty: bool = typer.Option(False, "--pretty", help="Render Rich tables instead of JSON"),
) -> None:
    result = analyze(ticker, period)
    if pretty:
        _render_pretty(result)
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    app()
