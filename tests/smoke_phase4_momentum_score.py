"""
Smoke tests for Phase 4: ms-momentum-score (momentum_score.py)

Run from project root:
    tools/.venv/bin/python tests/smoke_phase4_momentum_score.py

Tests are split into:
  - Unit tests (pure math, no network) — fast, deterministic
  - Integration tests (live yfinance data) — require network

Set SKIP_LIVE=1 to run only unit tests:
    SKIP_LIVE=1 tools/.venv/bin/python tests/smoke_phase4_momentum_score.py
"""

from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools", "src"))

# ── helpers ─────────────────────────────────────────────────────────────────

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


def close_enough(a: float, b: float, tol: float = 1e-6) -> bool:
    return math.isclose(a, b, rel_tol=tol)


# ── Unit tests ───────────────────────────────────────────────────────────────

def test_daily_returns_unit() -> None:
    print("\n[Unit] _daily_returns()")
    from market_sage.momentum_score import _daily_returns

    closes = [100.0, 110.0, 99.0, 108.9]
    rets = _daily_returns(closes)

    check("length = len(closes)-1", len(rets) == 3)
    check("ret[0] = (110/100)-1", close_enough(rets[0], 0.10))
    check("ret[1] = (99/110)-1", close_enough(rets[1], (99 / 110) - 1))
    check("ret[2] = (108.9/99)-1", close_enough(rets[2], (108.9 / 99) - 1))
    check("single-element input → empty list", _daily_returns([100.0]) == [])


def test_period_return_unit() -> None:
    print("\n[Unit] _period_return()")
    from market_sage.momentum_score import _period_return

    closes = [100.0] * 30 + [115.0]
    check("31-bar series, n=30 → 0.15", close_enough(_period_return(closes, 30), 0.15, tol=1e-4))

    flat = [100.0] * 21
    check("exact 21-bar series, n=21 → None (need n+1)", _period_return(flat, 21) is None)

    flat21 = [100.0] * 22
    check("22-bar series, n=21 → 0.0", close_enough(_period_return(flat21, 21), 0.0))

    check("n > len → None", _period_return([100.0, 110.0], 5) is None)


def test_annualized_vol_unit() -> None:
    print("\n[Unit] _annualized_vol()")
    from market_sage.momentum_score import _annualized_vol

    # Zero returns → vol = 0
    check("zero returns → 0.0 vol", _annualized_vol([0.0] * 252) == 0.0)

    # Known constant daily return of 0.01 → std=0, vol=0
    constant = [0.01] * 252
    check("constant returns → 0.0 vol", _annualized_vol(constant) == 0.0)

    # Alternating +0.02 / -0.02 — std should be 0.02, annualized = 0.02 * sqrt(252)
    alternating = [0.02 if i % 2 == 0 else -0.02 for i in range(252)]
    expected = 0.02 * (252 ** 0.5)
    result = _annualized_vol(alternating)
    check(
        f"alternating ±2% daily → ann_vol ≈ {expected:.4f}",
        close_enough(result, expected, tol=1e-4),
        f"got {result}",
    )

    # Under 2 bars → 0.0
    check("< 2 bars → 0.0", _annualized_vol([0.01]) == 0.0)


def test_vol_adjusted_momentum_higher_for_low_vol() -> None:
    print("\n[Unit] vol-adjusted score higher for lower volatility same-return stock")
    from market_sage.momentum_score import _annualized_vol

    # Both have same 12-1M return proxy, but different vols
    low_vol = [0.001] * 252   # tiny constant moves
    high_vol = [0.03 if i % 2 == 0 else -0.03 for i in range(252)]  # large alternating

    v_low = _annualized_vol(low_vol)
    v_high = _annualized_vol(high_vol)

    # low_vol should produce smaller annualized vol → higher vol-adj score for same return
    same_return = 0.30  # 30% 12-1M return
    score_low = same_return / v_low if v_low > 0 else float("inf")
    score_high = same_return / v_high if v_high > 0 else float("inf")

    check("low-vol stock scores higher than high-vol for same raw return", score_low > score_high)


def test_nse_ticker_helper() -> None:
    print("\n[Unit] _nse() helper from _utils")
    from market_sage._utils import _nse

    check("plain symbol → .NS suffix", _nse("HDFCBANK") == "HDFCBANK.NS")
    check(".NS already present → unchanged", _nse("HDFCBANK.NS") == "HDFCBANK.NS")
    check(".BO already present → unchanged", _nse("HDFCBANK.BO") == "HDFCBANK.BO")
    check("lowercase → uppercased", _nse("reliance") == "RELIANCE.NS")
    check("trailing whitespace stripped", _nse("  TCS  ") == "TCS.NS")


# ── Integration tests (require live network) ─────────────────────────────────

def test_live_momentum_score_single_symbol() -> None:
    print("\n[Live] _momentum_score() — single symbol")
    from market_sage.momentum_score import _momentum_score

    result = _momentum_score("HDFCBANK")
    print(f"       result keys: {list(result.keys())}")

    if "error" in result:
        check("no error returned", False, f"error={result['error']}")
        return

    check("symbol field uppercased", result.get("symbol") == "HDFCBANK")
    check("ticker has .NS suffix", result.get("ticker", "").endswith(".NS"))

    rets = result.get("returns", {})
    check("returns dict has 1m key", "1m" in rets)
    check("returns dict has 3m key", "3m" in rets)
    check("returns dict has 6m key", "6m" in rets)
    check("returns dict has 12m key", "12m" in rets)
    check("returns dict has 12_1m key", "12_1m" in rets)

    check("annualized_vol > 0", (result.get("annualized_vol") or 0) > 0)
    check("vol_adjusted_momentum is float or None", isinstance(result.get("vol_adjusted_momentum"), (float, type(None))))
    check("source_date present", bool(result.get("source_date")))

    # Sanity: 1M return should be within ±50% for a large-cap
    ret_1m = rets.get("1m")
    if ret_1m is not None:
        check("1M return within plausible range (±50%)", -0.5 < ret_1m < 0.5, f"got {ret_1m}")


def test_live_momentum_score_multi_symbol() -> None:
    print("\n[Live] analyze() — multiple symbols")
    from market_sage.momentum_score import analyze

    results = analyze(["HDFCBANK", "CDSL"])
    check("returns list of length 2", len(results) == 2)
    for r in results:
        if "error" not in r:
            check(f"{r['symbol']}: returns dict present", "returns" in r)


def test_live_insufficient_data() -> None:
    print("\n[Live] _momentum_score() — newly listed or invalid symbol returns error dict")
    from market_sage.momentum_score import _momentum_score

    result = _momentum_score("INVALIDTICKER999XYZ")
    check("error key present for invalid symbol", "error" in result)
    check("no crash — returns dict not exception", isinstance(result, dict))


def test_live_1m_return_math() -> None:
    print("\n[Live] 1M return matches manual calculation")
    import yfinance as yf
    from market_sage.momentum_score import _momentum_score

    ticker = "INFY.NS"
    hist = yf.Ticker(ticker).history(period="60d")
    if hist.empty or len(hist) < 22:
        print(f"       [{SKIP}] not enough bars for manual check")
        return
    hist = hist.dropna(subset=["Close"])
    closes = hist["Close"].tolist()
    manual_1m = round((closes[-1] / closes[-21]) - 1.0, 4)

    result = _momentum_score("INFY")
    if "error" in result:
        print(f"       [{SKIP}] live fetch failed: {result.get('error')}")
        return

    ret_1m = result["returns"].get("1m")
    check(
        f"1M return ≈ manual ({manual_1m:.4f})",
        ret_1m is not None and close_enough(ret_1m, manual_1m, tol=0.01),
        f"tool={ret_1m} manual={manual_1m}",
    )


# ── Runner ───────────────────────────────────────────────────────────────────

def main() -> None:
    skip_live = os.environ.get("SKIP_LIVE", "").strip() == "1"

    print("=" * 60)
    print("Phase 4 Smoke Tests — ms-momentum-score")
    print("=" * 60)

    # Unit tests (always run)
    test_daily_returns_unit()
    test_period_return_unit()
    test_annualized_vol_unit()
    test_vol_adjusted_momentum_higher_for_low_vol()
    test_nse_ticker_helper()

    # Integration tests
    if skip_live:
        print("\n[SKIP_LIVE=1] Skipping live network tests.")
    else:
        print("\n--- Live network tests (yfinance) ---")
        test_live_momentum_score_single_symbol()
        test_live_momentum_score_multi_symbol()
        test_live_insufficient_data()
        test_live_1m_return_math()

    print("\n" + "=" * 60)
    if _failures:
        print(f"\033[91mFAILED: {len(_failures)} test(s)\033[0m — {', '.join(_failures)}")
        sys.exit(1)
    else:
        print(f"\033[92mAll tests passed.\033[0m")


if __name__ == "__main__":
    main()
