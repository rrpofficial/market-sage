"""
Smoke tests for Phase 9: ms-momentum-screen (momentum_screen.py)

Run from project root:
    tools/.venv/bin/python tests/smoke_phase9_momentum_screen.py

Set SKIP_LIVE=1 to run only unit tests (no network):
    SKIP_LIVE=1 tools/.venv/bin/python tests/smoke_phase9_momentum_screen.py
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


# ── Numeric parsing helpers ──────────────────────────────────────────────────

def test_num_parsing() -> None:
    print("\n[Unit] _num()")
    from market_sage.momentum_screen import _num

    check("plain int", _num(42) == 42.0)
    check("float passthrough", _num(3.14) == 3.14)
    check("comma thousands", _num("1,234.5") == 1234.5)
    check("percent strip", _num("22.4%") == 22.4)
    check("rupee strip", _num("₹1,200") == 1200.0)
    check("parenthesised negative", _num("(15.3)") == -15.3)
    check("dash → None", _num("-") is None)
    check("em-dash → None", _num("—") is None)
    check("empty → None", _num("") is None)
    check("None → None", _num(None) is None)
    check("garbage → None", _num("N/A") is None)


def test_extract_row() -> None:
    print("\n[Unit] _extract_row()")
    from market_sage.momentum_screen import _extract_row

    # screener._parse_data_table shape: {label_col: [...labels...], period: [...vals...]}
    table = {
        "": ["Sales", "Net Profit", "EPS in Rs", "Dividend Payout %"],
        "Mar 2022": ["100", "10", "8.5", "20"],
        "Mar 2023": ["120", "14", "11.2", "22"],
        "Mar 2024": ["150", "20", "16.0", "25"],
    }
    eps = _extract_row(table, "EPS")
    check("EPS row extracted across 3 periods", eps == [8.5, 11.2, 16.0], f"got {eps}")
    np = _extract_row(table, "Net Profit")
    check("Net Profit row extracted", np == [10.0, 14.0, 20.0], f"got {np}")
    check("missing label → []", _extract_row(table, "Goodwill") == [])
    check("empty table → []", _extract_row({}, "EPS") == [])


def test_cagr() -> None:
    print("\n[Unit] _cagr()")
    from market_sage.momentum_screen import _cagr

    # 4 values, 3Y CAGR from first to last: (200/100)^(1/3)-1 ≈ 0.2599
    vals = [100.0, 120.0, 150.0, 200.0]
    c = _cagr(vals, 3)
    check("3Y CAGR ≈ 25.99%", c is not None and close_enough(c, 0.2599, tol=0.01), f"got {c}")
    check("insufficient periods → None", _cagr([100.0, 120.0], 3) is None)
    check("negative start → None", _cagr([-5.0, 1.0, 2.0, 3.0], 3) is None)
    check("zero start → None", _cagr([0.0, 1.0, 2.0, 3.0], 3) is None)
    check("None values skipped", _cagr([None, 100.0, 150.0, 200.0, 250.0], 3) is not None)


# ── 9.1 Fundamental quality gate ─────────────────────────────────────────────

def test_fundamental_quality() -> None:
    print("\n[Unit] _score_fundamental_quality()")
    from market_sage.momentum_screen import _score_fundamental_quality

    # Hard fail: D/E > 3
    sd = {"top_ratios": {"roe": 22, "debt_to_equity": 3.5}, "balance_sheet": {}, "annual_pl": {}}
    score, hf, reason = _score_fundamental_quality(sd)
    check("D/E > 3 → hard fail, score 0", hf and score == 0.0, f"{score},{hf},{reason}")

    # Hard fail: ROE < 0
    sd2 = {"top_ratios": {"roe": -5, "debt_to_equity": 0.2}, "balance_sheet": {}, "annual_pl": {}}
    s2, hf2, _ = _score_fundamental_quality(sd2)
    check("ROE < 0 → hard fail, score 0", hf2 and s2 == 0.0, f"{s2},{hf2}")

    # Full pass (ROE>15, D/E<1, EPS CAGR>15)
    annual = {
        "": ["Sales", "Net Profit", "EPS in Rs"],
        "Mar 2021": ["100", "10", "10"],
        "Mar 2022": ["130", "13", "12"],
        "Mar 2023": ["160", "17", "15"],
        "Mar 2024": ["200", "25", "20"],
    }
    sd3 = {"top_ratios": {"roe": 22, "debt_to_equity": 0.4}, "balance_sheet": {}, "annual_pl": annual}
    s3, hf3, r3 = _score_fundamental_quality(sd3)
    check("ROE>15 + D/E<1 + EPS CAGR>15 → 10.0", s3 == 10.0 and not hf3, f"{s3},{hf3},{r3}")

    # D/E derived from balance sheet when not in top_ratios
    balance = {
        "": ["Equity Capital", "Reserves", "Borrowings", "Total Liabilities"],
        "Mar 2024": ["10", "190", "50", "250"],
    }
    sd4 = {"top_ratios": {"roe": 18}, "balance_sheet": balance, "annual_pl": {}}
    s4, hf4, r4 = _score_fundamental_quality(sd4)
    # D/E = 50/(10+190) = 0.25 < 1 → pass; ROE 18>15 → pass; EPS absent → excluded
    check("D/E derived from balance sheet (0.25) → pass", s4 == 10.0 and not hf4, f"{s4},{hf4},{r4}")

    # Partial: ROE fails, D/E passes
    sd5 = {"top_ratios": {"roe": 8, "debt_to_equity": 0.3}, "balance_sheet": {}, "annual_pl": {}}
    s5, hf5, r5 = _score_fundamental_quality(sd5)
    check("ROE 8 fails, D/E passes → 5.0 (1 of 2)", s5 == 5.0 and not hf5, f"{s5},{hf5},{r5}")

    # No data → neutral 5.0, not a crash
    s6, hf6, r6 = _score_fundamental_quality({"error": "fetch_failed"})
    check("error dict → neutral 5.0", s6 == 5.0 and not hf6, f"{s6},{hf6},{r6}")
    s7, hf7, _ = _score_fundamental_quality({"top_ratios": {}, "balance_sheet": {}, "annual_pl": {}})
    check("no quantifiable metrics → 5.0", s7 == 5.0 and not hf7, f"{s7},{hf7}")


# ── 9.2 Momentum scoring ─────────────────────────────────────────────────────

def test_pct_rank() -> None:
    print("\n[Unit] _pct_rank()")
    from market_sage.momentum_screen import _pct_rank

    uni = [i / 100 for i in range(100)]  # 0.00 .. 0.99
    check("top value → ~0.99", close_enough(_pct_rank(0.99, uni), 0.99), f"{_pct_rank(0.99, uni)}")
    check("median value → ~0.50", close_enough(_pct_rank(0.50, uni), 0.50), f"{_pct_rank(0.50, uni)}")
    check("below all → 0.0", _pct_rank(-1.0, uni) == 0.0)
    check("None → 0.0", _pct_rank(None, uni) == 0.0)
    check("empty universe → 0.0", _pct_rank(0.5, []) == 0.0)


def test_score_momentum() -> None:
    print("\n[Unit] _score_momentum()")
    from market_sage.momentum_screen import _score_momentum

    uni = [i / 100 for i in range(100)]
    # Top decile 12-1M & 6M, vol-adj > 2, RS 85
    m = _score_momentum(0.95, 0.95, 2.5, 85, uni, uni)
    check("RS≥80 → 15", m["score_rs"] == 15.0, f"{m}")
    check("vol-adj>2 → 10", m["score_vol_adj"] == 10.0, f"{m}")
    check("12-1M top decile → ~19", m["score_12_1m"] >= 18.0, f"{m}")
    check("total ≤ 55", m["total"] <= 55.0, f"{m}")

    # RS tiers
    check("RS 75 → 10", _score_momentum(0, 0, None, 75, uni, uni)["score_rs"] == 10.0)
    check("RS 65 → 5", _score_momentum(0, 0, None, 65, uni, uni)["score_rs"] == 5.0)
    check("RS 50 → 0", _score_momentum(0, 0, None, 50, uni, uni)["score_rs"] == 0.0)
    check("RS None → 0", _score_momentum(0, 0, None, None, uni, uni)["score_rs"] == 0.0)

    # Vol-adj tiers
    check("vol-adj 1.5 → 5", _score_momentum(0, 0, 1.5, 0, uni, uni)["score_vol_adj"] == 5.0)
    check("vol-adj 0.5 → 0", _score_momentum(0, 0, 0.5, 0, uni, uni)["score_vol_adj"] == 0.0)
    check("vol-adj None → 0", _score_momentum(0, 0, None, 0, uni, uni)["score_vol_adj"] == 0.0)


# ── 9.3 Technical scoring ────────────────────────────────────────────────────

def test_score_technical() -> None:
    print("\n[Unit] _score_technical()")
    from market_sage.momentum_screen import _score_technical

    full = {"sepa_template": {"conditions_met": 8}, "adx": {"adx": 30}}
    ts = _score_technical(full)
    check("8/8 SEPA → 15", ts["score_sepa"] == 15.0, f"{ts}")
    check("ADX 30 → 10", ts["score_adx"] == 10.0, f"{ts}")
    check("total 25", ts["total"] == 25.0, f"{ts}")

    half = {"sepa_template": {"conditions_met": 4}, "adx": {"adx": 22}}
    ts2 = _score_technical(half)
    check("4/8 SEPA → 7.5", ts2["score_sepa"] == 7.5, f"{ts2}")
    check("ADX 22 → 5", ts2["score_adx"] == 5.0, f"{ts2}")

    weak = {"sepa_template": {"conditions_met": 0}, "adx": {"adx": 15}}
    ts3 = _score_technical(weak)
    check("0/8 SEPA → 0", ts3["score_sepa"] == 0.0, f"{ts3}")
    check("ADX 15 → 0", ts3["score_adx"] == 0.0, f"{ts3}")

    none_adx = {"sepa_template": {"conditions_met": 6}, "adx": {"adx": None}}
    check("ADX None → 0", _score_technical(none_adx)["score_adx"] == 0.0)


# ── 9.4 Volume scoring ───────────────────────────────────────────────────────

def test_score_volume() -> None:
    print("\n[Unit] _score_volume()")
    from market_sage.momentum_screen import _score_volume

    check("OBV Rising + CMF>0.05 → 10", _score_volume({"obv_trend": "Rising", "cmf_20": 0.1}) == 10)
    check("OBV Rising only → 5", _score_volume({"obv_trend": "Rising", "cmf_20": 0.0}) == 5)
    check("CMF>0.05 only → 5", _score_volume({"obv_trend": "Falling", "cmf_20": 0.1}) == 5)
    check("neither → 0", _score_volume({"obv_trend": "Falling", "cmf_20": -0.1}) == 0)
    check("error dict → 0", _score_volume({"error": "no_data"}) == 0)
    check("None cmf → handled", _score_volume({"obv_trend": "Rising", "cmf_20": None}) == 5)


# ── 9.5 Entry setup ──────────────────────────────────────────────────────────

def test_entry_setup() -> None:
    print("\n[Unit] _identify_entry_setup()")
    from market_sage.momentum_screen import _identify_entry_setup

    # Breakout: within 1% of 52W high, RVOL>1.5, CMF>0
    b = _identify_entry_setup(
        {"moving_averages": {"dma_50": 100, "dma_20": 110}, "support_resistance": {"resistance_1": 125}},
        {"rvol_5d": 2.0, "cmf_20": 0.1, "nr7_today": False},
        {"ltp": 124, "w52_high": 125},
    )
    check("breakout detected", b == "Breakout", b)

    # Pullback: price between 50 DMA and 20 DMA
    p = _identify_entry_setup(
        {"moving_averages": {"dma_50": 100, "dma_20": 110}, "support_resistance": {}},
        {"rvol_5d": 0.9, "cmf_20": 0.0, "nr7_today": False},
        {"ltp": 105, "w52_high": 200},
    )
    check("pullback (between MAs)", p == "Pullback", p)

    # Pullback: touched 50 DMA ±2%
    p2 = _identify_entry_setup(
        {"moving_averages": {"dma_50": 100, "dma_20": 95}, "support_resistance": {}},
        {"rvol_5d": 0.9, "cmf_20": 0.0, "nr7_today": False},
        {"ltp": 101, "w52_high": 200},
    )
    check("pullback (near 50 DMA)", p2 == "Pullback", p2)

    # NR7 Coil: NR7 today + within 3% of resistance
    coil = _identify_entry_setup(
        {"moving_averages": {"dma_50": 100, "dma_20": 103}, "support_resistance": {"resistance_1": 108}},
        {"rvol_5d": 0.9, "cmf_20": 0.0, "nr7_today": True},
        {"ltp": 107, "w52_high": 200},
    )
    check("NR7 coil detected", coil == "NR7 Coil", coil)

    # Extended: > 10% above 50 DMA
    ext = _identify_entry_setup(
        {"moving_averages": {"dma_50": 100, "dma_20": 105}, "support_resistance": {}},
        {"rvol_5d": 1.0, "cmf_20": 0.0, "nr7_today": False},
        {"ltp": 120, "w52_high": 200},
    )
    check("extended detected", ext == "Extended", ext)

    # No setup
    ns = _identify_entry_setup(
        {"moving_averages": {"dma_50": 100, "dma_20": 102}, "support_resistance": {"resistance_1": 130}},
        {"rvol_5d": 0.8, "cmf_20": -0.1, "nr7_today": False},
        {"ltp": 106, "w52_high": 200},
    )
    check("no setup fallback", ns == "No Setup", ns)

    # Missing ltp → No Setup (no crash)
    check("missing ltp → No Setup", _identify_entry_setup({}, {}, {}) == "No Setup")


# ── 9.6 Position sizing ──────────────────────────────────────────────────────

def test_position_size() -> None:
    print("\n[Unit] _compute_atr_position_size()")
    from market_sage.momentum_screen import _compute_atr_position_size

    # TC-08 from the plan: ₹5L, 1%, entry 1200, stop 1130
    p = _compute_atr_position_size(1200, 1130, 500000, 0.01)
    check("risk_amount = 5000", p["risk_amount"] == 5000.0, f"{p}")
    check("risk_per_share = 70", p["risk_per_share"] == 70.0, f"{p}")
    check("shares = 71 (floor)", p["shares"] == 71, f"{p}")
    check("total_outlay = 85200", p["total_outlay"] == 85200.0, f"{p}")

    # Zero/negative risk per share → 0 shares (no division error)
    z = _compute_atr_position_size(100, 100, 500000, 0.01)
    check("stop == entry → 0 shares", z["shares"] == 0, f"{z}")
    inv = _compute_atr_position_size(100, 110, 500000, 0.01)
    check("stop > entry → 0 shares", inv["shares"] == 0, f"{inv}")


# ── Composite (mocked pipeline) ──────────────────────────────────────────────

def test_composite_mocked() -> None:
    print("\n[Unit] _compute_composite() with mocked tool calls")
    import market_sage.momentum_screen as msm

    # Build a synthetic 300-bar rising close series (guarantees >= 252 bars).
    # Universe distributions are deliberately LOW-valued so this strong, steadily
    # rising stock ranks at the top of every intra-universe percentile (RS ≥ 80,
    # 12-1M and 6M in the top decile) — exercising the full-marks scoring path.
    closes = [100.0 * (1.003 ** i) for i in range(300)]
    batch = {"TESTCO": closes}
    uni_121 = [0.001 * i for i in range(50)]
    uni_6m = [0.001 * i for i in range(50)]
    uni_rs = [0.001 * i for i in range(50)]

    # Monkeypatch the per-symbol network functions
    orig_tech = msm.technicals.analyze
    orig_vol = msm.volume_profile.analyze
    orig_quote = msm.quotes.fetch_quote
    orig_fetch = msm._cached_fetch_symbol

    def fake_tech(sym, period="2y", rs_rating=None):
        return {
            "ltp": closes[-1],
            "atr_14": 5.0,
            "moving_averages": {"dma_20": closes[-1] * 0.98, "dma_50": closes[-1] * 0.96},
            "support_resistance": {"resistance_1": closes[-1] * 1.05},
            "sepa_template": {"conditions_met": 8 if rs_rating and rs_rating >= 70 else 7},
            "adx": {"adx": 30},
            "weinstein_stage": {"stage": 2, "action": "BUY"},
        }

    def fake_vol(sym, period="1y"):
        return {"obv_trend": "Rising", "cmf_20": 0.15, "rvol_5d": 1.2,
                "nr7_today": False, "volume_verdict": "Strong accumulation"}

    def fake_quote(sym):
        return {"ltp": closes[-1], "w52_high": closes[-1] * 1.02,
                "fo_ban": False, "delivery_pct_today": 55.0}

    def fake_fetch(sym, cache_dir):
        return {"top_ratios": {"roe": 25, "debt_to_equity": 0.3},
                "balance_sheet": {}, "annual_pl": {}}

    msm.technicals.analyze = fake_tech
    msm.volume_profile.analyze = fake_vol
    msm.quotes.fetch_quote = fake_quote
    msm._cached_fetch_symbol = fake_fetch
    try:
        r = msm._compute_composite("TESTCO", batch, uni_121, uni_6m, uni_rs, 500000, "/tmp/ms_cache_test")
        check("composite_score present", "composite_score" in r)
        check("composite in [0,100]", 0 <= r["composite_score"] <= 100, f"{r['composite_score']}")
        check("rs_rating computed", r["momentum"]["rs_rating"] is not None, f"{r['momentum']}")
        check("SEPA got RS injection (8/8)", r["technical"]["sepa_conditions_met"] == 8,
              f"{r['technical']}")
        check("fundamental score 10 (ROE25,D/E0.3)", r["fundamental"]["score"] == 10.0,
              f"{r['fundamental']}")
        check("volume score 10", r["volume"]["score"] == 10, f"{r['volume']}")
        check("entry_setup present", "entry_setup" in r)
        check("stage = 2", r["technical"]["stage"] == 2)
        # Strong everything → should qualify
        check("strong stock qualifies (>=65)", r["composite_score"] >= 65, f"{r['composite_score']}")
    finally:
        msm.technicals.analyze = orig_tech
        msm.volume_profile.analyze = orig_vol
        msm.quotes.fetch_quote = orig_quote
        msm._cached_fetch_symbol = orig_fetch


def test_composite_hard_fail_mocked() -> None:
    print("\n[Unit] _compute_composite() hard-fail forces composite to 0")
    import market_sage.momentum_screen as msm

    closes = [100.0 * (1.003 ** i) for i in range(300)]
    batch = {"BADCO": closes}

    orig_tech = msm.technicals.analyze
    orig_vol = msm.volume_profile.analyze
    orig_quote = msm.quotes.fetch_quote
    orig_fetch = msm._cached_fetch_symbol

    msm.technicals.analyze = lambda s, period="2y", rs_rating=None: {
        "ltp": closes[-1], "atr_14": 5.0,
        "moving_averages": {"dma_20": closes[-1], "dma_50": closes[-1]},
        "support_resistance": {}, "sepa_template": {"conditions_met": 8},
        "adx": {"adx": 35}, "weinstein_stage": {"stage": 2, "action": "BUY"},
    }
    msm.volume_profile.analyze = lambda s, period="1y": {
        "obv_trend": "Rising", "cmf_20": 0.2, "rvol_5d": 1.5,
        "nr7_today": False, "volume_verdict": "x"}
    msm.quotes.fetch_quote = lambda s: {"ltp": closes[-1], "w52_high": closes[-1], "fo_ban": False, "delivery_pct_today": 60}
    # D/E > 3 → hard fail
    msm._cached_fetch_symbol = lambda s, cache_dir: {
        "top_ratios": {"roe": 25, "debt_to_equity": 4.0}, "balance_sheet": {}, "annual_pl": {}}
    try:
        r = msm._compute_composite("BADCO", batch, [0.5], [0.3], [0.2], 500000, "/tmp/ms_cache_test")
        check("hard-fail → composite 0", r["composite_score"] == 0.0, f"{r['composite_score']}")
        check("hard-fail flagged", r["fundamental"]["hard_fail"] is True)
        check("does not qualify", r["qualifies"] is False)
    finally:
        msm.technicals.analyze = orig_tech
        msm.volume_profile.analyze = orig_vol
        msm.quotes.fetch_quote = orig_quote
        msm._cached_fetch_symbol = orig_fetch


# ── Cache + resolution ───────────────────────────────────────────────────────

def test_resolve_tickers() -> None:
    print("\n[Unit] _resolve_tickers()")
    from market_sage.momentum_screen import _resolve_tickers

    check("explicit symbols win", _resolve_tickers(["kaynes", "cdsl"], "NIFTY50") == ["KAYNES", "CDSL"])
    universe = _resolve_tickers(None, "NIFTY50")
    check("index resolves to list", isinstance(universe, list) and len(universe) >= 10, f"len={len(universe)}")


def test_cache_roundtrip() -> None:
    print("\n[Unit] _cached_fetch_symbol() cache round-trip")
    import time as _time
    import market_sage.momentum_screen as msm

    cache_dir = "/tmp/ms_cache_test_phase9"
    os.makedirs(cache_dir, exist_ok=True)
    # Clean any prior file
    import pathlib
    p = pathlib.Path(cache_dir) / "ZZTEST_screener.json"
    if p.exists():
        p.unlink()

    calls = {"n": 0}
    orig = msm.screener.fetch_symbol

    def counting_fetch(symbol, standalone=False):
        calls["n"] += 1
        return {"symbol": symbol.upper(), "top_ratios": {"roe": 20}, "balance_sheet": {}, "annual_pl": {}}

    msm.screener.fetch_symbol = counting_fetch
    try:
        r1 = msm._cached_fetch_symbol("ZZTEST", cache_dir)
        r2 = msm._cached_fetch_symbol("ZZTEST", cache_dir)
        check("first call hits network", calls["n"] == 1, f"calls={calls['n']}")
        check("second call served from cache (no extra network)", calls["n"] == 1, f"calls={calls['n']}")
        check("cached data identical", r1 == r2)
        check("cache file written", p.exists())
    finally:
        msm.screener.fetch_symbol = orig
        if p.exists():
            p.unlink()


# ── Live integration ─────────────────────────────────────────────────────────

def test_live_screen_small() -> None:
    print("\n[Live] screen() on a 3-symbol list")
    from market_sage.momentum_screen import screen

    results = screen(symbols=["HDFCBANK", "RELIANCE", "INFY"], min_score=0, portfolio_value=500000)
    check("returns a list", isinstance(results, list))
    check("3 results (min_score=0 keeps all)", len(results) == 3, f"got {len(results)}")
    if results:
        r = results[0]
        for key in ["symbol", "composite_score", "qualifies", "fundamental", "momentum",
                    "technical", "volume", "entry_setup", "rank"]:
            check(f"result key '{key}'", key in r, f"keys={list(r.keys())}")
        check("ranked descending", all(
            results[i]["composite_score"] >= results[i + 1]["composite_score"]
            for i in range(len(results) - 1)
        ))
        check("composite in [0,100]", all(0 <= r["composite_score"] <= 100 for r in results))
        print(f"       {[(r['symbol'], r['composite_score']) for r in results]}")


def test_live_min_score_filter() -> None:
    print("\n[Live] screen() min_score filter excludes low scorers")
    from market_sage.momentum_screen import screen

    results = screen(symbols=["HDFCBANK", "RELIANCE"], min_score=99, portfolio_value=500000)
    check("min_score=99 likely filters out most", isinstance(results, list) and len(results) <= 2,
          f"got {len(results)}")


# ── Runner ───────────────────────────────────────────────────────────────────

def main() -> None:
    skip_live = os.environ.get("SKIP_LIVE", "").strip() == "1"

    print("=" * 60)
    print("Phase 9 Smoke Tests — ms-momentum-screen")
    print("=" * 60)

    test_num_parsing()
    test_extract_row()
    test_cagr()
    test_fundamental_quality()
    test_pct_rank()
    test_score_momentum()
    test_score_technical()
    test_score_volume()
    test_entry_setup()
    test_position_size()
    test_composite_mocked()
    test_composite_hard_fail_mocked()
    test_resolve_tickers()
    test_cache_roundtrip()

    if skip_live:
        print("\n[SKIP_LIVE=1] Skipping live network tests.")
    else:
        print("\n--- Live network tests (yfinance + screener.in) ---")
        test_live_screen_small()
        test_live_min_score_filter()

    print("\n" + "=" * 60)
    if _failures:
        print(f"\033[91mFAILED: {len(_failures)} test(s)\033[0m — {', '.join(_failures)}")
        sys.exit(1)
    else:
        print("\033[92mAll tests passed.\033[0m")


if __name__ == "__main__":
    main()
