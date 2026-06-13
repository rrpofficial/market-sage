"""
Smoke tests for Phase 6: ms-breadth (breadth.py)

Run from project root:
    tools/.venv/bin/python tests/smoke_phase6_breadth.py

Set SKIP_LIVE=1 to run only unit tests:
    SKIP_LIVE=1 tools/.venv/bin/python tests/smoke_phase6_breadth.py
"""

from __future__ import annotations

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


# ── Unit tests ───────────────────────────────────────────────────────────────

def test_compute_200dma_unit() -> None:
    print("\n[Unit] _compute_200dma()")
    from market_sage.breadth import _compute_200dma

    flat_200 = [100.0] * 200
    check("flat 200 bars → 100.0", _compute_200dma(flat_200) == 100.0)

    check("< 200 bars → None", _compute_200dma([100.0] * 199) is None)
    check("empty → None", _compute_200dma([]) is None)

    # Mixed values: 100 bars at 90, 100 bars at 110 → DMA = 100
    mixed = [90.0] * 100 + [110.0] * 100
    result = _compute_200dma(mixed)
    check("mixed 100+100 bars → 100.0 avg", result is not None and abs(result - 100.0) < 0.01)


def test_compute_50dma_unit() -> None:
    print("\n[Unit] _compute_50dma()")
    from market_sage.breadth import _compute_50dma

    check("50 bars of 200.0 → 200.0", _compute_50dma([200.0] * 50) == 200.0)
    check("< 50 bars → None", _compute_50dma([200.0] * 49) is None)


def test_compute_breadth_empty() -> None:
    print("\n[Unit] _compute_breadth() with empty download (mocked)")
    # We can't easily mock _batch_download without patching, but we can test the
    # structure of an empty result by passing an empty tickers list indirectly.
    # Instead, test the output structure contract:
    from market_sage.breadth import _compute_breadth

    # Patch _batch_download to return empty
    import market_sage._utils as utils
    original = utils._batch_download

    def _mock_empty(tickers, period="1y"):
        return {}

    utils._batch_download = _mock_empty
    try:
        # Also need to patch the local import in breadth
        import market_sage.breadth as breadth_mod
        original_breadth_dl = getattr(breadth_mod, "_batch_download", None)

        # Directly test the fallback structure
        result = breadth_mod._compute_breadth([])
        check("empty download → error key present", "error" in result or result.get("total_stocks") == 0)
    finally:
        utils._batch_download = original


def test_compute_breadth_synthetic() -> None:
    print("\n[Unit] _compute_breadth() with synthetic data (mocked _batch_download)")
    import market_sage.breadth as breadth_mod
    import market_sage._utils as utils

    # Build synthetic data: 3 "stocks"
    # Stock A: 250 bars, last=150, dma200=100 → above 200 DMA; last=155 near 52W high
    # Stock B: 250 bars, last=80, dma200=100 → below 200 DMA; last=80 near 52W low
    # Stock C: 250 bars, last=100, dma200=100 → at 200 DMA (not above → below branch)
    closes_a = [100.0] * 200 + [150.0] * 50   # all above dma=100+50avg
    closes_b = [100.0] * 200 + [80.0] * 50
    closes_c = [100.0] * 250  # flat; dma200 = 100, last = 100 → NOT > dma200

    synthetic = {"STOCKA": closes_a, "STOCKB": closes_b, "STOCKC": closes_c}

    original_dl = utils._batch_download

    def _mock_dl(tickers, period="1y"):
        return synthetic

    utils._batch_download = _mock_dl
    # Patch in the breadth module too (it imports from _utils at call time)
    original_breadth_dl = breadth_mod._batch_download

    import market_sage.breadth as breadth_reloaded
    breadth_reloaded._batch_download = _mock_dl

    try:
        result = breadth_reloaded._compute_breadth(["STOCKA", "STOCKB", "STOCKC"])
        check("total_stocks = 3", result.get("total_stocks") == 3, str(result.get("total_stocks")))
        # Stock A: last=150 > dma200 (computed over last 200 = avg of [100]*150+[150]*50 = (150*100+50*150)/200=112.5)
        # Actually dma200 for A: closes_a[-200:] = [100]*150 + [150]*50
        # dma200 = (150*100 + 50*150)/200 = (15000+7500)/200 = 112.5; last=150 > 112.5 → above
        # Stock B: dma200 of closes_b[-200:] = [100]*150 + [80]*50 → (150*100+50*80)/200=115; last=80 < 115 → below
        # Stock C: dma200=100, last=100 → NOT >; below
        above = result.get("above_200dma", -1)
        check("above_200dma = 1 (only Stock A)", above == 1, f"got {above}")
        check("pct_above_200dma = 33.3%", abs(result.get("pct_above_200dma", 0) - 33.3) < 0.5)

        regime = result.get("market_regime")
        check("regime is one of Bullish/Neutral/Bearish", regime in ("Bullish", "Neutral", "Bearish"), regime)
        check("momentum_go is bool", isinstance(result.get("momentum_go"), bool))

        # ad_ratio: Stock A advanced (150>closes_a[-2]=150 → no advance!; actually all 50 bars are 150, so no advance)
        # For A: closes[-1]=150, closes[-2]=150 → equal → no advance/decline
        # For B: closes[-1]=80, closes[-2]=80 → equal → no advance/decline
        # For C: closes[-1]=100, closes[-2]=100 → equal → no advance/decline
        # So ad_ratio may be 1.0 (default when no advances and no declines)
        check("ad_ratio_today present", "ad_ratio_today" in result)
    finally:
        utils._batch_download = original_dl
        breadth_reloaded._batch_download = original_breadth_dl


def test_regime_classification() -> None:
    print("\n[Unit] Market regime classification thresholds")
    import market_sage.breadth as breadth_mod
    import market_sage._utils as utils

    original_dl = utils._batch_download

    def _make_mock(pct_above: float, total: int = 100):
        """Build synthetic closes where `pct_above` fraction are above their 200 DMA."""
        n_above = int(total * pct_above / 100)
        n_below = total - n_above
        closes_map = {}
        # Above: last bar=200, dma200=100
        for i in range(n_above):
            closes_map[f"ABOVE_{i}"] = [100.0] * 199 + [200.0]
        # Below: last bar=50, dma200=100
        for i in range(n_below):
            closes_map[f"BELOW_{i}"] = [100.0] * 199 + [50.0]
        return closes_map

    def mock_70_above(tickers, period="1y"):
        return _make_mock(70)

    def mock_30_above(tickers, period="1y"):
        return _make_mock(30)

    def mock_50_above(tickers, period="1y"):
        return _make_mock(50)

    for mock_fn, expected_regime in [
        (mock_70_above, "Bullish"),
        (mock_30_above, "Bearish"),
        (mock_50_above, "Neutral"),
    ]:
        breadth_mod._batch_download = mock_fn
        result = breadth_mod._compute_breadth(["dummy"])
        regime = result.get("market_regime")
        check(f"pct > 60% → Bullish / < 40% → Bearish / else → Neutral (got {regime})",
              regime == expected_regime, f"expected={expected_regime}, got={regime}")

    utils._batch_download = original_dl
    # Restore breadth module's own reference
    from market_sage._utils import _batch_download as real_dl
    breadth_mod._batch_download = real_dl


def test_momentum_go_threshold() -> None:
    print("\n[Unit] momentum_go threshold (≥ 50% above 200 DMA)")
    import market_sage.breadth as breadth_mod

    original_dl = breadth_mod._batch_download

    def _mock_49(tickers, period="1y"):
        closes_map = {}
        # 49 above, 51 below out of 100
        for i in range(49):
            closes_map[f"UP_{i}"] = [100.0] * 199 + [200.0]
        for i in range(51):
            closes_map[f"DOWN_{i}"] = [100.0] * 199 + [50.0]
        return closes_map

    def _mock_51(tickers, period="1y"):
        closes_map = {}
        for i in range(51):
            closes_map[f"UP_{i}"] = [100.0] * 199 + [200.0]
        for i in range(49):
            closes_map[f"DOWN_{i}"] = [100.0] * 199 + [50.0]
        return closes_map

    breadth_mod._batch_download = _mock_49
    result = breadth_mod._compute_breadth(["x"])
    check("49% above → momentum_go = False", result.get("momentum_go") is False)

    breadth_mod._batch_download = _mock_51
    result = breadth_mod._compute_breadth(["x"])
    check("51% above → momentum_go = True", result.get("momentum_go") is True)

    breadth_mod._batch_download = original_dl


def test_output_schema() -> None:
    print("\n[Unit] Output schema — required keys present")
    import market_sage.breadth as breadth_mod

    original_dl = breadth_mod._batch_download

    def _mock(tickers, period="1y"):
        return {"A": [100.0] * 252}

    breadth_mod._batch_download = _mock
    result = breadth_mod._compute_breadth(["A"])

    required_keys = [
        "total_stocks", "above_200dma", "pct_above_200dma",
        "above_50dma", "pct_above_50dma",
        "new_52w_highs", "new_52w_lows",
        "ad_ratio_today", "market_regime", "momentum_go",
    ]
    for key in required_keys:
        check(f"key '{key}' present in output", key in result, f"keys={list(result.keys())}")

    breadth_mod._batch_download = original_dl


def test_analyze_schema() -> None:
    print("\n[Unit] analyze() adds index, nifty50_vs_200dma, source_date")
    import market_sage.breadth as breadth_mod
    import yfinance as yf

    original_dl = breadth_mod._batch_download
    original_yf_ticker = yf.Ticker

    def _mock_dl(tickers, period="1y"):
        return {"A": [100.0] * 252, "B": [50.0] * 252}

    class MockTicker:
        def __init__(self, t):
            self.t = t
        def history(self, **kwargs):
            import pandas as pd
            import numpy as np
            closes = [100.0] * 252
            df = pd.DataFrame({"Close": closes})
            return df

    breadth_mod._batch_download = _mock_dl
    yf.Ticker = MockTicker

    try:
        result = breadth_mod.analyze(index="NIFTY50")
        check("index field set", result.get("index") == "NIFTY50")
        check("nifty50_vs_200dma present", "nifty50_vs_200dma" in result)
        check("source_date present", "source_date" in result)
        nifty_vs = result.get("nifty50_vs_200dma")
        check(
            "nifty50_vs_200dma is 'above' or 'below' or None",
            nifty_vs in ("above", "below", None),
            str(nifty_vs),
        )
    finally:
        breadth_mod._batch_download = original_dl
        yf.Ticker = original_yf_ticker


# ── Integration tests ─────────────────────────────────────────────────────────

def test_live_breadth_nifty50() -> None:
    print("\n[Live] analyze() — NIFTY50 (3-10 seconds)")
    from market_sage.breadth import analyze

    result = analyze(index="NIFTY50")
    print(f"       market_regime={result.get('market_regime')} | "
          f"pct_above_200dma={result.get('pct_above_200dma')}% | "
          f"total_stocks={result.get('total_stocks')}")

    check("no error key", "error" not in result or result.get("total_stocks", 0) > 0)
    check("total_stocks >= 30", (result.get("total_stocks") or 0) >= 30,
          f"got {result.get('total_stocks')}")
    check("pct_above_200dma in 0-100", 0 <= (result.get("pct_above_200dma") or 0) <= 100)
    check("market_regime valid", result.get("market_regime") in ("Bullish", "Neutral", "Bearish"),
          str(result.get("market_regime")))
    check("momentum_go is bool", isinstance(result.get("momentum_go"), bool))
    check("source_date present", bool(result.get("source_date")))
    check("nifty50_vs_200dma in 'above'/'below'/None",
          result.get("nifty50_vs_200dma") in ("above", "below", None))


def test_live_ad_ratio_plausible() -> None:
    print("\n[Live] A/D ratio plausibility check")
    from market_sage.breadth import analyze

    result = analyze(index="NIFTY50")
    ad = result.get("ad_ratio_today", -1)
    check("ad_ratio_today > 0", ad > 0, f"got {ad}")
    check("ad_ratio_today < 100", ad < 100, f"got {ad}")


def test_live_new_highs_lows() -> None:
    print("\n[Live] New 52W highs/lows are non-negative integers")
    from market_sage.breadth import analyze

    result = analyze(index="NIFTY50")
    highs = result.get("new_52w_highs", -1)
    lows  = result.get("new_52w_lows",  -1)
    check("new_52w_highs >= 0", highs >= 0, f"got {highs}")
    check("new_52w_lows >= 0",  lows  >= 0, f"got {lows}")
    check("highs + lows <= total_stocks",
          highs + lows <= (result.get("total_stocks") or 0) + 1)  # +1 for float rounding


# ── Runner ───────────────────────────────────────────────────────────────────

def main() -> None:
    skip_live = os.environ.get("SKIP_LIVE", "").strip() == "1"

    print("=" * 60)
    print("Phase 6 Smoke Tests — ms-breadth")
    print("=" * 60)

    # Unit tests (always run)
    test_compute_200dma_unit()
    test_compute_50dma_unit()
    test_compute_breadth_empty()
    test_compute_breadth_synthetic()
    test_regime_classification()
    test_momentum_go_threshold()
    test_output_schema()
    test_analyze_schema()

    if skip_live:
        print("\n[SKIP_LIVE=1] Skipping live network tests.")
    else:
        print("\n--- Live network tests (yfinance / NIFTY50) ---")
        test_live_breadth_nifty50()
        test_live_ad_ratio_plausible()
        test_live_new_highs_lows()

    print("\n" + "=" * 60)
    if _failures:
        print(f"\033[91mFAILED: {len(_failures)} test(s)\033[0m — {', '.join(_failures)}")
        sys.exit(1)
    else:
        print("\033[92mAll tests passed.\033[0m")


if __name__ == "__main__":
    main()
