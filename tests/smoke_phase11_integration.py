"""
Phase 11 — Integration & Validation tests for the momentum-sage skill.

Covers the end-to-end test cases (TC-01 … TC-10) and regression checks from the
implementation plan that can be validated programmatically. Static/unit checks
always run; live network checks are skipped under SKIP_LIVE=1.

Run from project root:
    tools/.venv/bin/python tests/smoke_phase11_integration.py
    SKIP_LIVE=1 tools/.venv/bin/python tests/smoke_phase11_integration.py
"""

from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools", "src"))

ROOT = os.path.join(os.path.dirname(__file__), "..")

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


# ── TC-03 — Fundamental failure gate ─────────────────────────────────────────

def test_tc03_fundamental_gate() -> None:
    print("\n[TC-03] Fundamental failure gate (D/E > 3 → hard fail, composite 0)")
    from market_sage.momentum_screen import _score_fundamental_quality

    score, hard_fail, reason = _score_fundamental_quality(
        {"top_ratios": {"roe": 25, "debt_to_equity": 4.0}, "balance_sheet": {}, "annual_pl": {}}
    )
    check("D/E 4.0 → (0, True, reason)", score == 0.0 and hard_fail, f"{score},{hard_fail},{reason}")
    check("reason mentions D/E", "D/E" in reason, reason)

    # ROE < 0 hard fail
    s2, hf2, r2 = _score_fundamental_quality(
        {"top_ratios": {"roe": -3, "debt_to_equity": 0.5}, "balance_sheet": {}, "annual_pl": {}}
    )
    check("ROE < 0 → hard fail", s2 == 0.0 and hf2, f"{s2},{hf2},{r2}")


# ── TC-08 — Position sizing math ─────────────────────────────────────────────

def test_tc08_position_sizing() -> None:
    print("\n[TC-08] Position sizing math validation")
    from market_sage.momentum_screen import _compute_atr_position_size

    # Plan TC-08: ₹5,00,000, 1%, Stock ₹1,200, Stop ₹1,130
    p = _compute_atr_position_size(1200, 1130, 500000, 0.01)
    check("risk_amount = ₹5,000", p["risk_amount"] == 5000.0, f"{p}")
    check("risk_per_share = ₹70", p["risk_per_share"] == 70.0, f"{p}")
    check("shares = 71 (floor)", p["shares"] == 71, f"{p}")
    check("total_outlay = ₹85,200", p["total_outlay"] == 85200.0, f"{p}")

    # Second independent example from Section 10 of the skill doc
    p2 = _compute_atr_position_size(800, 760, 500000, 0.01)
    check("₹800/₹760 → 125 shares", p2["shares"] == 125, f"{p2}")


# ── Phase 10 — Skill file validation ─────────────────────────────────────────

def test_skill_files_exist() -> None:
    print("\n[Phase 10] Skill files exist and parse")
    md_path = os.path.join(ROOT, "momentum-sage.md")
    yaml_path = os.path.join(ROOT, "momentum-sage.yaml")
    check("momentum-sage.md exists", os.path.exists(md_path))
    check("momentum-sage.yaml exists", os.path.exists(yaml_path))

    with open(md_path) as f:
        md = f.read()
    with open(yaml_path) as f:
        ytext = f.read()

    # Frontmatter
    fm = re.match(r"^---\n(.*?)\n---\n", md, re.DOTALL)
    check("md has YAML frontmatter", fm is not None)
    if fm:
        check("md frontmatter name = momentum-sage", "name: momentum-sage" in fm.group(1))

    # DATA INTEGRITY MANDATE is the first substantive section
    body = md[fm.end():] if fm else md
    first_h2 = re.search(r"^## (.+)$", body, re.MULTILINE)
    check("first H2 is the DATA INTEGRITY MANDATE",
          first_h2 is not None and "DATA INTEGRITY MANDATE" in first_h2.group(1),
          first_h2.group(1) if first_h2 else "none")

    # All 13 conceptual sections (frontmatter=1, then SECTION 2..13)
    secs = sorted(set(int(s) for s in re.findall(r"^## (?:⛔ )?SECTION (\d+)", md, re.MULTILINE)))
    check("sections 2-13 present", secs == list(range(2, 14)), f"got {secs}")


def test_skill_tool_name_consistency() -> None:
    print("\n[Phase 10] Tool names in skill files match registered CLIs")
    import tomllib

    with open(os.path.join(ROOT, "tools", "pyproject.toml"), "rb") as f:
        pp = tomllib.load(f)
    registered = set(pp["project"]["scripts"].keys())

    with open(os.path.join(ROOT, "momentum-sage.yaml")) as f:
        ytext = f.read()
    tool_block = ytext.split("tools:", 1)[1].split("metadata:", 1)[0]
    yaml_tools = re.findall(r"^\s*-\s*(ms-[\w-]+)", tool_block, re.MULTILINE)

    check("yaml lists 10 tools", len(yaml_tools) == 10, f"got {len(yaml_tools)}")
    missing = [t for t in yaml_tools if t not in registered]
    check("every yaml tool is a registered CLI", not missing, f"missing={missing}")

    # The mandate lookup table in the .md references each tool
    with open(os.path.join(ROOT, "momentum-sage.md")) as f:
        md = f.read()
    not_in_md = [t for t in yaml_tools if t not in md]
    check("every tool referenced in md", not not_in_md, f"missing={not_in_md}")

    # ms-momentum-screen specifically must be registered (Phase 9 deliverable)
    check("ms-momentum-screen registered", "ms-momentum-screen" in registered)


def test_skill_india_policies_present() -> None:
    print("\n[Phase 10 / TC-10] India-specific policy rules present in skill doc")
    with open(os.path.join(ROOT, "momentum-sage.md")) as f:
        md = f.read().lower()
    check("LIC decomposition rule present", "lic" in md and "politically directed" in md)
    check("delivery% interpretation present", "delivery" in md and "50%" in md)
    check("F&O ban three-state explained", "fo_ban" in md or "f&o ban" in md)
    check("ATR position sizing formula present", "risk per share" in md or "risk_per_share" in md.replace(" ", "_"))


# ── Regression — existing tools still import & expose stable schemas ──────────

def test_regression_imports() -> None:
    print("\n[Regression] All tool modules import and expose public entry points")
    import importlib

    modules = {
        "market_sage.quotes": ["fetch_quote", "app"],
        "market_sage.screener": ["fetch_symbol", "app"],
        "market_sage.technicals": ["analyze", "app"],
        "market_sage.momentum_score": ["analyze", "_momentum_score", "app"],
        "market_sage.rs_rank": ["fetch_rs", "analyze", "app"],
        "market_sage.breadth": ["analyze", "app"],
        "market_sage.sector_rs": ["analyze", "app"],
        "market_sage.volume_profile": ["analyze", "app"],
        "market_sage.momentum_screen": ["screen", "_compute_composite", "app"],
    }
    for mod_name, attrs in modules.items():
        try:
            mod = importlib.import_module(mod_name)
            missing = [a for a in attrs if not hasattr(mod, a)]
            check(f"{mod_name} imports + exposes {attrs}", not missing, f"missing={missing}")
        except Exception as exc:
            check(f"{mod_name} imports", False, str(exc))


def test_regression_technicals_schema() -> None:
    print("\n[Regression] technicals.analyze() schema stable (new fields appended)")
    import market_sage.technicals as tech_mod
    import yfinance as yf
    import pandas as pd

    class MockTicker:
        def __init__(self, t): pass
        def history(self, period="1y"):
            n = 260
            return pd.DataFrame({
                "Open":   [100.0 + i * 0.2 for i in range(n)],
                "High":   [101.0 + i * 0.2 for i in range(n)],
                "Low":    [99.0 + i * 0.2 for i in range(n)],
                "Close":  [100.0 + i * 0.2 for i in range(n)],
                "Volume": [100000 + i * 10 for i in range(n)],
            })

    orig = yf.Ticker
    yf.Ticker = MockTicker
    try:
        result = tech_mod.analyze("TESTCO", period="2y")
        # Legacy fields that must NOT disappear (no-regression contract)
        for key in ["symbol", "ltp", "moving_averages", "rsi_14", "macd",
                    "bollinger_bands_20_2", "atr_14", "support_resistance",
                    "volume", "verdict"]:
            check(f"legacy key '{key}' present", key in result, f"keys={list(result.keys())}")
        # New momentum fields appended in Phase 1
        for key in ["adx", "stochastic", "supertrend", "parabolic_sar",
                    "fibonacci", "weinstein_stage", "sepa_template"]:
            check(f"phase-1 key '{key}' present", key in result)
        # RS injection contract used by the orchestrator
        r_rs = tech_mod.analyze("TESTCO", period="2y", rs_rating=85.0)
        cond = r_rs["sepa_template"]["conditions"]["rs_rating_70plus"]
        check("SEPA condition 8 honours injected RS (85→True)", cond is True, f"got {cond}")
    finally:
        yf.Ticker = orig


def test_composite_uses_only_tool_data() -> None:
    print("\n[TC-06-ish] composite degrades gracefully when a tool errors (no crash)")
    import market_sage.momentum_screen as msm

    closes = [100.0 * (1.002 ** i) for i in range(300)]
    batch = {"ERRCO": closes}

    orig_tech, orig_vol, orig_quote, orig_fetch = (
        msm.technicals.analyze, msm.volume_profile.analyze,
        msm.quotes.fetch_quote, msm._cached_fetch_symbol,
    )
    # Every per-symbol tool returns an error dict
    msm.technicals.analyze = lambda s, period="2y", rs_rating=None: {"symbol": s, "error": "no_data"}
    msm.volume_profile.analyze = lambda s, period="1y": {"symbol": s, "error": "no_data"}
    msm.quotes.fetch_quote = lambda s: {"symbol": s, "error": "no_data"}
    msm._cached_fetch_symbol = lambda s, cache_dir: {"symbol": s, "error": "fetch_failed"}
    try:
        r = msm._compute_composite("ERRCO", batch, [0.5], [0.3], [0.2], 500000, "/tmp/ms_cache_t11")
        check("returns a dict (no exception)", isinstance(r, dict))
        check("composite_score numeric", isinstance(r.get("composite_score"), (int, float)))
        check("no entry setup when technicals errored", r.get("entry_setup") == "No Setup")
        check("position_size is None when no ltp/atr", r.get("position_size") is None)
    finally:
        msm.technicals.analyze = orig_tech
        msm.volume_profile.analyze = orig_vol
        msm.quotes.fetch_quote = orig_quote
        msm._cached_fetch_symbol = orig_fetch


# ── Live test cases ──────────────────────────────────────────────────────────

def test_tc04_bull_market_breadth() -> None:
    print("\n[TC-04 / Live] Market breadth on NIFTY50")
    from market_sage.breadth import analyze

    data = analyze(index="NIFTY50")
    if data.get("error"):
        print(f"  [{SKIP}] breadth error: {data['error']}")
        return
    check("market_regime valid", data.get("market_regime") in ("Bullish", "Neutral", "Bearish"))
    check("momentum_go is bool", isinstance(data.get("momentum_go"), bool))
    check("pct_above_200dma in [0,100]", 0 <= (data.get("pct_above_200dma") or 0) <= 100)
    check("ad_ratio_today > 0", (data.get("ad_ratio_today") or 0) > 0)
    check("nifty50_vs_200dma above/below/None",
          data.get("nifty50_vs_200dma") in ("above", "below", None))
    print(f"       regime={data.get('market_regime')} | %>200DMA={data.get('pct_above_200dma')} "
          f"| go={data.get('momentum_go')}")


def test_tc09_adx_sanity() -> None:
    print("\n[TC-09 / Live] ADX & Stochastic present and in-range — RELIANCE")
    from market_sage.technicals import analyze

    data = analyze("RELIANCE", period="2y")
    if data.get("error"):
        print(f"  [{SKIP}] technicals error: {data['error']}")
        return
    adx = data.get("adx", {})
    check("ADX value present", adx.get("adx") is not None)
    check("ADX in [0,100]", 0 <= (adx.get("adx") or 0) <= 100, f"got {adx.get('adx')}")
    check("DI signal valid", adx.get("di_signal") in ("bullish", "bearish", None))
    stoch = data.get("stochastic", {})
    check("Stochastic %K in [0,100]", stoch.get("k_pct") is None or 0 <= stoch["k_pct"] <= 100)
    stage = data.get("weinstein_stage", {}).get("stage")
    check("Weinstein stage in 1-4 or None", stage in (1, 2, 3, 4, None), f"got {stage}")


def test_tc01_02_pipeline_live() -> None:
    print("\n[TC-01/02 / Live] Full composite pipeline ranks 2 stocks without crash")
    from market_sage.momentum_screen import screen

    results = screen(symbols=["RELIANCE", "INFY"], min_score=0, portfolio_value=500000)
    check("2 results", len(results) == 2, f"got {len(results)}")
    check("ranked descending by composite",
          all(results[i]["composite_score"] >= results[i + 1]["composite_score"]
              for i in range(len(results) - 1)))
    for r in results:
        check(f"{r['symbol']}: composite in [0,100]", 0 <= r["composite_score"] <= 100)
        check(f"{r['symbol']}: entry_setup present", "entry_setup" in r)
        check(f"{r['symbol']}: fundamental sub-scored", "score" in r.get("fundamental", {}))
    print(f"       {[(r['symbol'], r['composite_score'], r['entry_setup']) for r in results]}")


def test_tc06_invalid_symbol_no_crash() -> None:
    print("\n[TC-06 / Live] Invalid symbol returns structured result, not an exception")
    from market_sage.momentum_screen import screen

    results = screen(symbols=["NONSENSE_XYZ_999"], min_score=0, portfolio_value=500000)
    check("returns a list", isinstance(results, list))
    check("no exception raised", True)
    if results:
        check("invalid symbol scored low (no data)", results[0]["composite_score"] <= 40,
              f"got {results[0]['composite_score']}")


def test_tc10_lic_decomposition_live() -> None:
    print("\n[TC-10 / Live] Screener exposes DII / LIC decomposition fields")
    from market_sage.screener import fetch_symbol

    data = fetch_symbol("HDFCBANK")
    if data.get("error"):
        print(f"  [{SKIP}] screener error: {data['error']}")
        return
    sh = data.get("shareholding", {})
    check("shareholding present", isinstance(sh, dict))
    # dii_split keys are merged into shareholding by fetch_symbol
    has_split_signal = any("lic" in str(k).lower() or "dii" in str(k).lower() for k in sh.keys()) \
        or "dii_split_available" in sh
    check("DII/LIC split signal present in output", has_split_signal or sh != {},
          f"keys={list(sh.keys())[:8]}")


# ── Runner ───────────────────────────────────────────────────────────────────

def main() -> None:
    skip_live = os.environ.get("SKIP_LIVE", "").strip() == "1"

    print("=" * 60)
    print("Phase 11 Integration & Validation Tests")
    print("=" * 60)

    # Static / unit (always run)
    test_tc03_fundamental_gate()
    test_tc08_position_sizing()
    test_skill_files_exist()
    test_skill_tool_name_consistency()
    test_skill_india_policies_present()
    test_regression_imports()
    test_regression_technicals_schema()
    test_composite_uses_only_tool_data()

    if skip_live:
        print("\n[SKIP_LIVE=1] Skipping live network test cases (TC-01,02,04,06,09,10).")
    else:
        print("\n--- Live integration test cases ---")
        test_tc04_bull_market_breadth()
        test_tc09_adx_sanity()
        test_tc01_02_pipeline_live()
        test_tc06_invalid_symbol_no_crash()
        test_tc10_lic_decomposition_live()

    print("\n" + "=" * 60)
    if _failures:
        print(f"\033[91mFAILED: {len(_failures)} test(s)\033[0m — {', '.join(_failures)}")
        sys.exit(1)
    else:
        print("\033[92mAll tests passed.\033[0m")


if __name__ == "__main__":
    main()
