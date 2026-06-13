"""
Smoke tests for Phase 5: ms-rs-rank (rs_rank.py)

Run from project root:
    tools/.venv/bin/python tests/smoke_phase5_rs_rank.py

Set SKIP_LIVE=1 to run only unit tests:
    SKIP_LIVE=1 tools/.venv/bin/python tests/smoke_phase5_rs_rank.py
"""

from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools", "src"))

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
SKIP = "\033[93mSKIP\033[0m"

_failures: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"  [{PASS}] {name}")
    else:
        print(f"  [{FAIL}] {name}" + (f" — {detail}" if detail else ""))
        _failures.append(name)


def close_enough(a: float, b: float, tol: float = 1e-4) -> bool:
    return math.isclose(a, b, rel_tol=tol)


# ── Unit tests ───────────────────────────────────────────────────────────────

def test_ibdrs_score_unit() -> None:
    print("\n[Unit] _ibdrs_score()")
    from market_sage.rs_rank import _ibdrs_score

    # Build a synthetic price series: 252 bars
    # q1 (last 63 bars): flat → return = 0
    # q2 (63-126 bars ago): +20%
    # q3 (126-189 bars ago): flat
    # q4 (189-252 bars ago): flat
    # Build backwards: price at -252 = 100, -189 = 100, -126 = 100, -63 = 120, -1 = 120
    closes: list[float] = []
    closes += [100.0] * 63   # bars 252..189 ago (q4 period base)
    closes += [100.0] * 63   # bars 189..126 ago (q3)
    closes += [100.0] * 63   # bars 126..63 ago (q2 base → end at 120)
    # Interpolate bar 189 to 126: stays at 100 and then rises from 100 to 120 over 63 bars
    # Simplify: just set exact values at the quarter boundaries
    # Re-build with clear values:
    # close[-252] = 100, close[-189] = 100, close[-126] = 100, close[-63] = 120, close[-1] = 120
    closes = [100.0] * 252
    closes[-189] = 100.0
    closes[-126] = 100.0
    closes[-63] = 120.0
    closes[-1] = 120.0

    score = _ibdrs_score(closes)
    # Expected: q1 = (120/120)-1 = 0, q2 = (120/100)-1 = 0.2, q3 = (100/100)-1 = 0, q4 = (100/100)-1 = 0
    # score = 0.40*0 + 0.20*0.20 + 0.20*0 + 0.20*0 = 0.04
    check("score with q2 +20%: approx 0.04", score is not None and close_enough(score, 0.04, tol=0.02))

    # Insufficient data → None
    check("< 252 bars → None", _ibdrs_score([100.0] * 200) is None)

    # All flat → score = 0.0
    flat_252 = [100.0] * 252
    score_flat = _ibdrs_score(flat_252)
    check("all-flat series → 0.0", score_flat is not None and close_enough(score_flat, 0.0))


def test_percentile_rank_unit() -> None:
    print("\n[Unit] _percentile_rank()")
    from market_sage.rs_rank import _percentile_rank

    universe = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]

    # Score = 10.0 → beats 9 of 10 (s < score, not <=) → 9/10*99+1 = 89
    # 99 is only possible when score strictly exceeds ALL universe members
    r = _percentile_rank(10.0, universe)
    check("top-of-universe score → high rating (≥85)", r >= 85, f"got {r}")

    # Score = 15.0 → beats all 10 → 10/10*99 = 99 → min(99, 99+1)=99
    r = _percentile_rank(15.0, universe)
    check("score above all → 99", r == 99, f"got {r}")

    # Score = 0.0 → beats none → rank = 1 (min)
    r = _percentile_rank(0.0, universe)
    check("bottom score → 1", r == 1, f"got {r}")

    # Score = 5.5 → beats 5 of 10 = 50% → ~50
    r = _percentile_rank(5.5, universe)
    check("mid score → ~50", 45 <= r <= 55, f"got {r}")

    # Empty universe → 50
    check("empty universe → 50", _percentile_rank(5.0, []) == 50)

    # Result always in 1–99
    for v in [0.0, 3.5, 10.0, 15.0]:
        r = _percentile_rank(v, universe)
        check(f"result in 1-99 for score={v}", 1 <= r <= 99, f"got {r}")


def test_mansfield_rs_unit() -> None:
    print("\n[Unit] _mansfield_rs()")
    from market_sage.rs_rank import _mansfield_rs

    # Stock outperformed index: stock +50%, index +20%
    # mansfield = (1.50/1.20) - 1 = 0.25 = 25%
    stock_closes = [100.0] + [100.0] * 250 + [150.0]   # 252 bars, +50% total
    index_closes = [100.0] + [100.0] * 250 + [120.0]   # 252 bars, +20% total
    result = _mansfield_rs(stock_closes, index_closes)
    check(
        "outperform: stock +50% vs index +20% → mansfield ≈ 0.25",
        result is not None and close_enough(result, 0.25, tol=0.01),
        f"got {result}",
    )

    # Stock and index same return → mansfield = 0.0
    same_closes = [100.0] * 250 + [130.0, 130.0]
    result_same = _mansfield_rs(same_closes, same_closes)
    check("same return → mansfield ≈ 0.0", result_same is not None and close_enough(result_same, 0.0))

    # Stock underperformed: stock +10%, index +30% → mansfield = (1.10/1.30)-1 = -0.154
    stock_under = [100.0] * 252
    stock_under[-1] = 110.0
    index_out = [100.0] * 252
    index_out[-1] = 130.0
    result_under = _mansfield_rs(stock_under, index_out)
    expected_under = (110.0 / 130.0) - 1  # ≈ -0.154
    check(
        f"underperform: stock+10% vs index+30% → mansfield ≈ {expected_under:.3f}",
        result_under is not None and close_enough(result_under, expected_under, tol=0.01),
        f"got {result_under}",
    )

    # Insufficient data → None
    check("< 252 bars → None", _mansfield_rs([100.0] * 100, [100.0] * 100) is None)


def test_nifty500_tickers_data() -> None:
    print("\n[Unit] nifty500_tickers.py data module")
    from market_sage.data.nifty500_tickers import (
        NIFTY50, NIFTY100, NIFTYMIDCAP150, NIFTYSMALLCAP250, NIFTY500
    )

    check("NIFTY50 has 45-55 symbols", 45 <= len(NIFTY50) <= 55, f"got {len(NIFTY50)}")
    check("NIFTY100 has 95-110 symbols", 95 <= len(NIFTY100) <= 110, f"got {len(NIFTY100)}")
    check("NIFTYMIDCAP150 has 140-160 symbols", 140 <= len(NIFTYMIDCAP150) <= 160, f"got {len(NIFTYMIDCAP150)}")
    check("NIFTYSMALLCAP250 has 240-260 symbols", 240 <= len(NIFTYSMALLCAP250) <= 260, f"got {len(NIFTYSMALLCAP250)}")
    check("NIFTY500 has 450+ symbols", len(NIFTY500) >= 450, f"got {len(NIFTY500)}")

    # No duplicates within NIFTY50
    check("NIFTY50: no duplicates", len(NIFTY50) == len(set(NIFTY50)))
    check("NIFTY100: no duplicates", len(NIFTY100) == len(set(NIFTY100)))

    # NIFTY50 is subset of NIFTY100
    check("NIFTY50 ⊆ NIFTY100", all(s in NIFTY100 for s in NIFTY50))

    # Key large-cap names present
    for sym in ["HDFCBANK", "RELIANCE", "TCS", "INFY", "ICICIBANK"]:
        check(f"{sym} in NIFTY50", sym in NIFTY50)

    # No .NS suffixes in the raw lists
    all_in_500 = set(NIFTY500)
    for sym in all_in_500:
        check(f"no .NS suffix in list: {sym[:15]}", not sym.endswith(".NS"), sym)
        break  # Check one representative


def test_get_universe_fallback() -> None:
    print("\n[Unit] _get_universe() fallback (no nsepython)")
    from market_sage._utils import _get_universe

    # These always use the fallback since nsepython won't recognise our test names
    nifty50 = _get_universe("NIFTY50")
    check("NIFTY50 universe has 45+ symbols", len(nifty50) >= 45, f"got {len(nifty50)}")

    nifty100 = _get_universe("NIFTY100")
    check("NIFTY100 universe has 95+ symbols", len(nifty100) >= 95)

    midcap = _get_universe("NIFTYMIDCAP150")
    check("NIFTYMIDCAP150 universe has 140+ symbols", len(midcap) >= 140)

    # Unknown index → falls back to NIFTY500
    unknown = _get_universe("UNKNOWNINDEX")
    check("unknown index → NIFTY500 fallback (450+)", len(unknown) >= 450)


# ── Integration tests (require live network) ─────────────────────────────────

def test_live_rs_rank_hdfcbank() -> None:
    print("\n[Live] fetch_rs() — HDFCBANK vs NIFTY50")
    from market_sage.rs_rank import fetch_rs

    result = fetch_rs("HDFCBANK", vs="NIFTY50")
    print(f"       result keys: {list(result.keys())}")

    if "error" in result:
        check("no error", False, f"error={result['error']}")
        return

    rs = result.get("rs_rating")
    check("rs_rating is int between 1 and 99", isinstance(rs, int) and 1 <= rs <= 99, f"got {rs}")

    mansfield = result.get("mansfield_rs")
    check("mansfield_rs is float or None", isinstance(mansfield, (float, type(None))))

    check("rs_label is non-empty string", isinstance(result.get("rs_label"), str) and len(result["rs_label"]) > 0)
    check("mansfield_signal present", result.get("mansfield_signal") in ("Outperforming", "Underperforming"))
    check("universe_size >= 45", (result.get("universe_size") or 0) >= 45)
    check("source_date present", bool(result.get("source_date")))


def test_live_rs_rating_scale() -> None:
    print("\n[Live] RS Ratings — relative scale makes sense")
    from market_sage.rs_rank import fetch_rs

    # Run two stocks vs NIFTY50: one likely leader, one likely laggard indicator
    # We can't assert absolute values since market conditions change; we assert range
    for sym in ["HDFCBANK", "TCS"]:
        result = fetch_rs(sym, vs="NIFTY50")
        if "error" in result:
            print(f"       [{SKIP}] {sym}: {result.get('error')}")
            continue
        rs = result.get("rs_rating", 0)
        check(f"{sym} RS in 1–99 range", 1 <= rs <= 99, f"got {rs}")


def test_live_invalid_symbol() -> None:
    print("\n[Live] fetch_rs() — invalid symbol returns error dict")
    from market_sage.rs_rank import fetch_rs

    result = fetch_rs("TOTALNONSENSE999XYZ", vs="NIFTY50")
    check("error key present", "error" in result, f"keys={list(result.keys())}")
    check("no crash — returns dict", isinstance(result, dict))


def test_live_mansfield_positive_for_leader() -> None:
    """A stock that outperformed Nifty over 12M should have positive Mansfield RS."""
    print("\n[Live] Mansfield RS — directional logic")
    import yfinance as yf

    # Manually check: if stock return > index return → mansfield should be > 0
    stock_ticker = "HDFCBANK.NS"
    index_ticker = "^NSEI"

    s_hist = yf.Ticker(stock_ticker).history(period="1y")["Close"].dropna().tolist()
    i_hist = yf.Ticker(index_ticker).history(period="1y")["Close"].dropna().tolist()

    if len(s_hist) < 252 or len(i_hist) < 252:
        print(f"       [{SKIP}] insufficient history for directional check")
        return

    stock_ret = (s_hist[-1] / s_hist[-252]) - 1
    index_ret = (i_hist[-1] / i_hist[-252]) - 1
    print(f"       HDFCBANK 12M return: {stock_ret:.2%} | Nifty 12M: {index_ret:.2%}")

    from market_sage.rs_rank import _mansfield_rs
    mansfield = _mansfield_rs(s_hist, i_hist)

    if stock_ret > index_ret:
        check("stock outperformed → mansfield > 0", mansfield is not None and mansfield > 0, f"got {mansfield}")
    else:
        check("stock underperformed → mansfield < 0", mansfield is not None and mansfield < 0, f"got {mansfield}")


# ── Runner ───────────────────────────────────────────────────────────────────

def main() -> None:
    skip_live = os.environ.get("SKIP_LIVE", "").strip() == "1"

    print("=" * 60)
    print("Phase 5 Smoke Tests — ms-rs-rank")
    print("=" * 60)

    # Unit tests (always run)
    test_ibdrs_score_unit()
    test_percentile_rank_unit()
    test_mansfield_rs_unit()
    test_nifty500_tickers_data()
    test_get_universe_fallback()

    # Integration tests
    if skip_live:
        print("\n[SKIP_LIVE=1] Skipping live network tests.")
    else:
        print("\n--- Live network tests (yfinance) ---")
        test_live_rs_rank_hdfcbank()
        test_live_rs_rating_scale()
        test_live_invalid_symbol()
        test_live_mansfield_positive_for_leader()

    print("\n" + "=" * 60)
    if _failures:
        print(f"\033[91mFAILED: {len(_failures)} test(s)\033[0m — {', '.join(_failures)}")
        sys.exit(1)
    else:
        print(f"\033[92mAll tests passed.\033[0m")


if __name__ == "__main__":
    main()
