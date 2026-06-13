"""
ms-momentum-screen [--index NIFTYMIDCAP150] [--symbols SYM1 SYM2 ...]
                   [--min-score 65] [--portfolio 500000] [--vs NIFTY500] [--pretty]

Full-pipeline momentum orchestrator. Takes a named NSE index (or an explicit
symbol list), runs every stock through the complete momentum + fundamental
pipeline, computes a 100-point composite score, and outputs a ranked buy-list.

Composite score (100 pts):
  12-1M price momentum  20   (intra-universe percentile, ms-momentum-score logic)
  6M price momentum     10   (intra-universe percentile)
  Vol-adjusted momentum 10   (12-1M return / annualised vol)
  IBD RS Rating         15   (intra-universe percentile, ms-rs-rank logic)
  SEPA Trend Template   15   (ms-technicals, RS injected into condition 8)
  ADX trend strength    10   (ms-technicals)
  OBV + CMF             10   (ms-volume-profile)
  Fundamental quality   10   (ms-screener — ROE, D/E, EPS growth; hard-fail gate)

Qualify for buy-list: composite >= min_score AND fundamental gate not hard-failed.

Architecture: RS Rating and momentum are computed IN-PROCESS from a single
batch yfinance download (one round-trip for the whole universe) rather than by
re-invoking ms-rs-rank per symbol — which would re-download the entire universe
for every stock. Per-symbol network calls are reserved for data that needs full
OHLCV or HTML: ms-technicals, ms-volume-profile, ms-screener, ms-quotes.

Screener.in results are cached to /tmp/ms_cache/ for CACHE_TTL_SECONDS to keep
re-runs fast and to respect screener.in rate limits.

Live data only — no training-knowledge values are ever used.
Runtime: NIFTYMIDCAP150 ≈ 8-15 minutes (first run); faster on cache hits.
"""

from __future__ import annotations

import json
import os
import time
from datetime import date
from pathlib import Path
from typing import Optional

import typer
from rich import box
from rich.console import Console
from rich.table import Table

from market_sage import CACHE_DIR, CACHE_TTL_SECONDS
from market_sage import screener, quotes, technicals, volume_profile
from market_sage._utils import _batch_download, _get_universe, _nse, _period_return
from market_sage.rs_rank import _ibdrs_score, _percentile_rank

app = typer.Typer(add_completion=False)
console = Console()
_err = Console(stderr=True)  # status/progress messages go to stderr, not stdout


# ── Numeric parsing helpers ──────────────────────────────────────────────────

def _num(value) -> float | None:
    """Coerce a screener.in cell (str/float/None) to float.

    Handles thousands separators, trailing %, and parenthesised negatives.
    Returns None when the cell cannot be parsed.
    """
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    if not s or s in {"-", "—", ""}:
        return None
    neg = s.startswith("(") and s.endswith(")")
    s = s.strip("()").replace(",", "").replace("%", "").replace("₹", "").strip()
    try:
        f = float(s)
        return -f if neg else f
    except ValueError:
        return None


def _extract_row(table: dict, label_substr: str) -> list[float | None]:
    """Pull a single labelled row from a screener data-table dict.

    screener._parse_data_table returns {col_header: [cell, cell, ...]} where the
    FIRST header is the row-label column. This finds the row whose label contains
    `label_substr` (case-insensitive) and returns its values across the period
    columns (label column excluded), parsed to float.
    """
    if not table:
        return []
    headers = list(table.keys())
    if not headers:
        return []
    label_col = headers[0]
    labels = table.get(label_col, [])
    target_idx: int | None = None
    for i, lab in enumerate(labels):
        if label_substr.lower() in str(lab).lower():
            target_idx = i
            break
    if target_idx is None:
        return []
    values: list[float | None] = []
    for h in headers[1:]:
        col = table.get(h, [])
        values.append(_num(col[target_idx]) if target_idx < len(col) else None)
    return values


def _cagr(values: list[float | None], years: int) -> float | None:
    """Compound annual growth rate between the value `years` periods back and the
    most recent non-None period value. Returns a decimal (0.18 = 18%).

    Returns None on insufficient data or when start/end signs make CAGR undefined
    (e.g. growing out of a loss).
    """
    clean = [v for v in values if v is not None]
    if len(clean) < years + 1:
        return None
    end = clean[-1]
    start = clean[-(years + 1)]
    if start is None or end is None or start <= 0 or end <= 0:
        return None
    return round((end / start) ** (1 / years) - 1, 4)


# ── 9.1 Fundamental quality gate ─────────────────────────────────────────────

def _score_fundamental_quality(screener_data: dict) -> tuple[float, bool, str]:
    """Score fundamental quality 0-10 and return (score, hard_fail, reason).

    Hard-fail (score forced to 0 overall) when D/E > 3 OR ROE < 0.
    Otherwise each available metric contributes an equal share of 10 points;
    metrics whose data is unavailable are excluded from the denominator so a
    missing data point neither rewards nor penalises the stock.

    Metrics: ROE > 15%, D/E < 1.0, 3Y EPS CAGR > 15%.
    """
    if not screener_data or "error" in screener_data:
        return 5.0, False, "fundamental_data_unavailable"

    top = screener_data.get("top_ratios", {}) or {}
    balance = screener_data.get("balance_sheet", {}) or {}
    annual = screener_data.get("annual_pl", {}) or {}

    # ROE — screener top-ratios key is normalised to "roe" (or "return_on_equity")
    roe = _num(top.get("roe"))
    if roe is None:
        roe = _num(top.get("return_on_equity"))

    # Debt/Equity — rarely a top-ratio; derive from balance sheet:
    #   D/E = Borrowings / (Equity Capital + Reserves)
    de = _num(top.get("debt_to_equity"))
    if de is None:
        borrow = _extract_row(balance, "Borrowing")
        equity = _extract_row(balance, "Equity Capital")
        reserves = _extract_row(balance, "Reserves")
        if borrow and equity and reserves:
            b = borrow[-1]
            e = equity[-1]
            r = reserves[-1]
            if b is not None and e is not None and r is not None and (e + r) > 0:
                de = round(b / (e + r), 2)

    # 3Y EPS CAGR — from the annual P&L "EPS" row
    eps_row = _extract_row(annual, "EPS")
    eps_cagr = _cagr(eps_row, 3)

    # Hard-fail conditions
    if de is not None and de > 3:
        return 0.0, True, f"D/E {de} > 3: hard fail"
    if roe is not None and roe < 0:
        return 0.0, True, f"ROE {roe}% < 0: hard fail"

    earned = 0.0
    possible = 0.0
    notes: list[str] = []
    if roe is not None:
        possible += 1
        if roe > 15:
            earned += 1
        else:
            notes.append(f"ROE {roe}%<15")
    if de is not None:
        possible += 1
        if de < 1.0:
            earned += 1
        else:
            notes.append(f"D/E {de}>=1")
    if eps_cagr is not None:
        possible += 1
        if eps_cagr > 0.15:
            earned += 1
        else:
            notes.append(f"EPS3Y {round(eps_cagr * 100, 1)}%<15")

    if possible == 0:
        return 5.0, False, "no_quantifiable_fundamentals"

    score = round(earned / possible * 10, 1)
    reason = "pass" if earned == possible else "; ".join(notes)
    return score, False, reason


# ── 9.2 Momentum score ───────────────────────────────────────────────────────

def _pct_rank(value: float | None, universe: list[float]) -> float:
    """Fraction (0.0-1.0) of `universe` strictly below `value`."""
    if value is None or not universe:
        return 0.0
    return sum(1 for u in universe if u < value) / len(universe)


def _score_momentum(
    ret_12_1m: float | None,
    ret_6m: float | None,
    vol_adj: float | None,
    rs_rating: int | None,
    universe_12_1m: list[float],
    universe_6m: list[float],
) -> dict:
    """Momentum component (max 55): 12-1M (20), 6M (10), vol-adj (10), RS (15)."""
    s_12_1m = round(_pct_rank(ret_12_1m, universe_12_1m) * 20, 1)
    s_6m = round(_pct_rank(ret_6m, universe_6m) * 10, 1)

    if vol_adj is None:
        s_vol = 0.0
    elif vol_adj > 2.0:
        s_vol = 10.0
    elif vol_adj >= 1.0:
        s_vol = 5.0
    else:
        s_vol = 0.0

    if rs_rating is None:
        s_rs = 0.0
    elif rs_rating >= 80:
        s_rs = 15.0
    elif rs_rating >= 70:
        s_rs = 10.0
    elif rs_rating >= 60:
        s_rs = 5.0
    else:
        s_rs = 0.0

    return {
        "score_12_1m": s_12_1m,
        "score_6m": s_6m,
        "score_vol_adj": s_vol,
        "score_rs": s_rs,
        "total": round(s_12_1m + s_6m + s_vol + s_rs, 1),
    }


# ── 9.3 Technical score ──────────────────────────────────────────────────────

def _score_technical(tech_data: dict) -> dict:
    """Technical component (max 25): SEPA (15) + ADX (10).

    SEPA score is taken directly from technicals.analyze() output, which already
    reflects the injected RS rating (condition 8) when analyze() was called with
    rs_rating set.
    """
    sepa = tech_data.get("sepa_template", {}) or {}
    conditions_met = sepa.get("conditions_met", 0)
    s_sepa = round(conditions_met / 8 * 15, 1)

    adx_block = tech_data.get("adx", {}) or {}
    adx = adx_block.get("adx")
    if adx is None:
        s_adx = 0.0
    elif adx > 25:
        s_adx = 10.0
    elif adx >= 20:
        s_adx = 5.0
    else:
        s_adx = 0.0

    return {
        "score_sepa": s_sepa,
        "score_adx": s_adx,
        "sepa_conditions_met": conditions_met,
        "adx": adx,
        "total": round(s_sepa + s_adx, 1),
    }


# ── 9.4 Volume score ─────────────────────────────────────────────────────────

def _score_volume(vol_data: dict) -> int:
    """Volume component (max 10): OBV Rising AND CMF>0.05 → 10; one positive → 5."""
    if not vol_data or "error" in vol_data:
        return 0
    obv_rising = vol_data.get("obv_trend") == "Rising"
    cmf = vol_data.get("cmf_20")
    cmf_positive = cmf is not None and cmf > 0.05
    if obv_rising and cmf_positive:
        return 10
    if obv_rising or cmf_positive:
        return 5
    return 0


# ── 9.5 Entry setup identification ───────────────────────────────────────────

def _identify_entry_setup(tech_data: dict, vol_data: dict, quotes_data: dict) -> str:
    """Classify the current actionable setup. First match wins."""
    ltp = quotes_data.get("ltp") if quotes_data else None
    if ltp is None:
        ltp = tech_data.get("ltp")
    if ltp is None:
        return "No Setup"

    w52_high = quotes_data.get("w52_high") if quotes_data else None
    rvol = vol_data.get("rvol_5d") if vol_data else None
    cmf = vol_data.get("cmf_20") if vol_data else None
    nr7 = vol_data.get("nr7_today") if vol_data else False

    ma = tech_data.get("moving_averages", {}) or {}
    dma_50 = ma.get("dma_50")
    dma_20 = ma.get("dma_20")
    sr = tech_data.get("support_resistance", {}) or {}
    resistance_1 = sr.get("resistance_1")

    # 1. Breakout: within 1% of 52W high AND RVOL > 1.5 AND CMF > 0
    if (
        w52_high and ltp >= w52_high * 0.99
        and rvol is not None and rvol > 1.5
        and cmf is not None and cmf > 0
    ):
        return "Breakout"

    # 2. Pullback: price between 50 DMA and 20 DMA, or touched 50 DMA ±2%
    if dma_50 is not None:
        if dma_20 is not None and dma_50 <= ltp <= dma_20:
            return "Pullback"
        if abs(ltp - dma_50) / dma_50 <= 0.02:
            return "Pullback"

    # 3. NR7 Coil: NR7 today AND within 3% of a resistance level
    if nr7 and resistance_1 and abs(ltp - resistance_1) / resistance_1 <= 0.03:
        return "NR7 Coil"

    # 4. Extended: more than 10% above 50 DMA — wait for pullback
    if dma_50 is not None and ltp > dma_50 * 1.10:
        return "Extended"

    return "No Setup"


# ── 9.6 ATR-based position sizing ────────────────────────────────────────────

def _compute_atr_position_size(
    entry: float,
    stop_loss: float,
    portfolio_value: float,
    risk_pct: float = 0.01,
) -> dict:
    """Position size for a fixed-fractional risk model."""
    risk_amount = portfolio_value * risk_pct
    risk_per_share = entry - stop_loss
    shares = int(risk_amount / risk_per_share) if risk_per_share > 0 else 0
    return {
        "entry": round(entry, 2),
        "stop_loss": round(stop_loss, 2),
        "risk_per_share": round(risk_per_share, 2),
        "shares": shares,
        "total_outlay": round(shares * entry, 2),
        "risk_amount": round(risk_amount, 2),
    }


# ── Screener cache ───────────────────────────────────────────────────────────

def _cached_fetch_symbol(symbol: str, cache_dir: str) -> dict:
    """screener.fetch_symbol with a JSON file cache (CACHE_TTL_SECONDS)."""
    try:
        os.makedirs(cache_dir, exist_ok=True)
        cache_path = Path(cache_dir) / f"{symbol.upper()}_screener.json"
        if cache_path.exists() and (time.time() - cache_path.stat().st_mtime) < CACHE_TTL_SECONDS:
            return json.loads(cache_path.read_text())
    except Exception:
        cache_path = None  # type: ignore[assignment]

    data = screener.fetch_symbol(symbol)

    try:
        if cache_path is not None and "error" not in data:
            cache_path.write_text(json.dumps(data))
    except Exception:
        pass
    return data


# ── 9.7 Per-symbol composite ─────────────────────────────────────────────────

def _compute_composite(
    symbol: str,
    batch_closes: dict[str, list[float]],
    universe_12_1m: list[float],
    universe_6m: list[float],
    universe_rs_scores: list[float],
    portfolio_value: float,
    cache_dir: str,
    exclude_last: int = 21,
) -> dict:
    """Run the full pipeline for one symbol and return its scored result dict."""
    sym = symbol.upper()
    closes = batch_closes.get(sym)

    # ── Momentum + RS from the shared batch (no extra network round-trip) ──
    ret_6m = ret_12_1m = ret_12m = vol_adj = None
    rs_rating: int | None = None
    if closes and len(closes) >= 252:
        ret_6m = _period_return(closes, 126)
        ret_12m = _period_return(closes, 252)
        trimmed = closes[:-exclude_last] if exclude_last > 0 else closes
        ret_12_1m = _period_return(trimmed, 252 - exclude_last) if len(trimmed) >= 252 else None

        daily = [(closes[i] / closes[i - 1]) - 1.0 for i in range(1, len(closes[-252:]))]
        if len(daily) >= 2:
            mean = sum(daily) / len(daily)
            var = sum((r - mean) ** 2 for r in daily) / len(daily)
            ann_vol = round((var ** 0.5) * (252 ** 0.5), 4)
        else:
            ann_vol = 0.0
        vol_adj = round(ret_12_1m / ann_vol, 3) if (ret_12_1m is not None and ann_vol > 0) else None

        raw_rs = _ibdrs_score(closes)
        if raw_rs is not None and universe_rs_scores:
            rs_rating = _percentile_rank(raw_rs, universe_rs_scores)

    # ── Technicals (RS injected → SEPA condition 8) ──
    try:
        tech = technicals.analyze(sym, period="2y", rs_rating=float(rs_rating) if rs_rating is not None else None)
    except Exception as exc:
        tech = {"error": f"technicals_failed: {exc}"}

    # ── Volume profile ──
    try:
        vol = volume_profile.analyze(sym, period="1y")
    except Exception as exc:
        vol = {"error": f"volume_failed: {exc}"}

    # ── Quotes (LTP, 52W high, delivery%, F&O ban) ──
    try:
        quote = quotes.fetch_quote(sym)
    except Exception as exc:
        quote = {"error": f"quotes_failed: {exc}"}

    # ── Fundamentals (cached) ──
    screen_data = _cached_fetch_symbol(sym, cache_dir)
    fund_score, hard_fail, fund_reason = _score_fundamental_quality(screen_data)

    # ── Component scores ──
    mom = _score_momentum(ret_12_1m, ret_6m, vol_adj, rs_rating, universe_12_1m, universe_6m)
    tech_score = _score_technical(tech) if "error" not in tech else {"total": 0.0, "score_sepa": 0.0, "score_adx": 0.0, "sepa_conditions_met": 0, "adx": None}
    vol_score = _score_volume(vol)

    composite = round(mom["total"] + tech_score["total"] + vol_score + fund_score, 1)
    if hard_fail:
        composite = 0.0

    # ── Entry setup + position sizing ──
    setup = _identify_entry_setup(tech, vol, quote) if "error" not in tech else "No Setup"

    ltp = quote.get("ltp") if "error" not in quote else tech.get("ltp")
    atr = tech.get("atr_14") if "error" not in tech else None
    position: dict | None = None
    if ltp is not None and atr is not None and setup not in ("Extended", "No Setup"):
        entry = ltp
        stop = ltp - 1.5 * atr
        position = _compute_atr_position_size(entry, stop, portfolio_value)

    weinstein = tech.get("weinstein_stage", {}) if "error" not in tech else {}

    return {
        "symbol": sym,
        "composite_score": composite,
        "qualifies": composite >= 65 and not hard_fail,
        "fundamental": {
            "score": fund_score,
            "hard_fail": hard_fail,
            "reason": fund_reason,
        },
        "momentum": {
            "ret_6m": ret_6m,
            "ret_12m": ret_12m,
            "ret_12_1m": ret_12_1m,
            "vol_adjusted": vol_adj,
            "rs_rating": rs_rating,
            **mom,
        },
        "technical": {
            "stage": weinstein.get("stage"),
            "stage_action": weinstein.get("action"),
            **tech_score,
        },
        "volume": {
            "score": vol_score,
            "obv_trend": vol.get("obv_trend") if "error" not in vol else None,
            "cmf_20": vol.get("cmf_20") if "error" not in vol else None,
            "verdict": vol.get("volume_verdict") if "error" not in vol else None,
        },
        "ltp": ltp,
        "atr_14": atr,
        "entry_setup": setup,
        "position_size": position,
        "fo_ban": quote.get("fo_ban") if "error" not in quote else None,
        "delivery_pct": quote.get("delivery_pct_today") if "error" not in quote else None,
        "source_date": date.today().isoformat(),
    }


# ── 9.8 Screen orchestration ─────────────────────────────────────────────────

def _resolve_tickers(symbols: Optional[list[str]], index: Optional[str]) -> list[str]:
    if symbols:
        return [s.upper().strip() for s in symbols]
    return _get_universe(index or "NIFTYMIDCAP150")


def screen(
    symbols: Optional[list[str]] = None,
    index: Optional[str] = None,
    min_score: float = 65,
    portfolio_value: float = 500000,
    cache_dir: str = CACHE_DIR,
    vs_universe: str = "NIFTY500",
) -> list[dict]:
    """Run the full momentum screen and return results sorted by composite score.

    First pass: a single batch download of the screened universe's closes, used
    to build intra-universe momentum and RS distributions. Second pass: per-symbol
    composite computation (technicals/volume/screener/quotes).
    """
    tickers = _resolve_tickers(symbols, index)
    label = ",".join(tickers) if symbols else (index or "NIFTYMIDCAP150")

    _err.print(
        f"[dim]Batch-downloading {len(tickers)} tickers ({label}) for momentum/RS "
        f"distribution — may take 15-30s...[/dim]",
        highlight=False,
    )
    batch = _batch_download(tickers, period="14mo")

    # Build intra-universe distributions from the batch
    universe_12_1m: list[float] = []
    universe_6m: list[float] = []
    universe_rs_scores: list[float] = []
    for _sym, closes in batch.items():
        if len(closes) < 252:
            continue
        r6 = _period_return(closes, 126)
        trimmed = closes[:-21]
        r121 = _period_return(trimmed, 231) if len(trimmed) >= 252 else None
        rs_raw = _ibdrs_score(closes)
        if r6 is not None:
            universe_6m.append(r6)
        if r121 is not None:
            universe_12_1m.append(r121)
        if rs_raw is not None:
            universe_rs_scores.append(rs_raw)

    _err.print(
        f"[dim]Scoring {len(tickers)} symbols through the full pipeline "
        f"(technicals + volume + screener + quotes)...[/dim]",
        highlight=False,
    )

    results: list[dict] = []
    for i, sym in enumerate(tickers, 1):
        _err.print(f"[dim]  [{i}/{len(tickers)}] {sym}[/dim]", highlight=False)
        try:
            res = _compute_composite(
                sym, batch, universe_12_1m, universe_6m, universe_rs_scores,
                portfolio_value, cache_dir,
            )
        except Exception as exc:
            res = {"symbol": sym, "composite_score": 0.0, "error": str(exc)}
        results.append(res)

    results.sort(key=lambda r: r.get("composite_score", 0.0), reverse=True)
    for rank, r in enumerate(results, 1):
        r["rank"] = rank

    return [r for r in results if r.get("composite_score", 0.0) >= min_score]


# ── 9.9 Pretty renderer + CLI ────────────────────────────────────────────────

def _score_colour(score: float) -> str:
    if score >= 65:
        return "green"
    if score >= 50:
        return "yellow"
    return "red"


def _render_pretty(results: list[dict], min_score: float, portfolio_value: float) -> None:
    tbl = Table(
        title=f"Momentum Screen — composite ≥ {min_score:.0f} (₹{portfolio_value:,.0f} portfolio, 1% risk)",
        box=box.SIMPLE,
        show_header=True,
        header_style="bold cyan",
        pad_edge=False,
    )
    tbl.add_column("#", justify="right", width=3)
    tbl.add_column("Symbol", style="bold", width=12)
    tbl.add_column("Score", justify="right", width=6)
    tbl.add_column("Fund", justify="right", width=6)
    tbl.add_column("SEPA", justify="right", width=5)
    tbl.add_column("RS", justify="right", width=4)
    tbl.add_column("Vol", justify="right", width=4)
    tbl.add_column("Setup", width=10)
    tbl.add_column("Entry", justify="right", width=9)
    tbl.add_column("Stop", justify="right", width=9)
    tbl.add_column("Shares", justify="right", width=7)

    for r in results:
        if "error" in r and "composite_score" not in r:
            continue
        score = r.get("composite_score", 0.0)
        colour = _score_colour(score)
        fund = r.get("fundamental", {})
        mom = r.get("momentum", {})
        tech = r.get("technical", {})
        vol = r.get("volume", {})
        pos = r.get("position_size") or {}
        setup = r.get("entry_setup", "No Setup")

        fund_cell = "[red]FUND.FAIL[/red]" if fund.get("hard_fail") else f"{fund.get('score', 0):.1f}"
        setup_cell = f"[orange1]{setup}[/orange1]" if setup == "Extended" else setup
        rs = mom.get("rs_rating")

        tbl.add_row(
            str(r.get("rank", "?")),
            r.get("symbol", "?"),
            f"[{colour}]{score:.1f}[/{colour}]",
            fund_cell,
            f"{tech.get('sepa_conditions_met', 0)}/8",
            str(rs) if rs is not None else "—",
            str(vol.get("score", 0)),
            setup_cell,
            f"₹{pos.get('entry'):,.0f}" if pos.get("entry") else "—",
            f"₹{pos.get('stop_loss'):,.0f}" if pos.get("stop_loss") else "—",
            str(pos.get("shares")) if pos.get("shares") else "—",
        )

    console.print(tbl)
    qualifiers = [r for r in results if r.get("qualifies")]
    console.print(
        f"[dim]{len(qualifiers)} stock(s) qualify (score ≥ 65, fundamental gate passed) | "
        f"Source: yfinance + screener.in | Date: {date.today().isoformat()}[/dim]"
    )


@app.command()
def main(
    index: str = typer.Option(
        "NIFTYMIDCAP150", "--index",
        help="Index to screen: NIFTY50, NIFTY100, NIFTY500, NIFTYMIDCAP150",
    ),
    symbols: Optional[list[str]] = typer.Option(
        None, "--symbols", help="Explicit symbol list (overrides --index)",
    ),
    min_score: float = typer.Option(65, "--min-score", help="Minimum composite score to list"),
    portfolio: float = typer.Option(500000, "--portfolio", help="Portfolio value (₹) for position sizing"),
    vs: str = typer.Option("NIFTY500", "--vs", help="Reference universe for RS context (unused when screening a full index)"),
    pretty: bool = typer.Option(False, "--pretty", help="Render a Rich ranked table"),
) -> None:
    """Rank a momentum buy-list across an index or symbol list.

    NIFTYMIDCAP150 takes ~8-15 minutes on a cold cache; re-runs are faster.
    """
    results = screen(
        symbols=symbols,
        index=index,
        min_score=min_score,
        portfolio_value=portfolio,
        vs_universe=vs,
    )
    if pretty:
        _render_pretty(results, min_score, portfolio)
    else:
        console.print(json.dumps(results, indent=2))
