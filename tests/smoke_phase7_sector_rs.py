"""
Smoke tests for Phase 7: ms-sector-rs (sector_rs.py)

Run from project root:
    tools/.venv/bin/python tests/smoke_phase7_sector_rs.py

Set SKIP_LIVE=1 to run only unit tests:
    SKIP_LIVE=1 tools/.venv/bin/python tests/smoke_phase7_sector_rs.py
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

def test_sector_rs_unit() -> None:
    print("\n[Unit] _sector_rs()")
    from market_sage.sector_rs import _sector_rs

    # Sector up 20%, Nifty up 10% → RS = +10pp
    sector = [100.0] * 62 + [120.0]   # 63 bars; period-return = +20%
    nifty  = [100.0] * 62 + [110.0]   # period-return = +10%
    rs = _sector_rs(sector, nifty, 63)
    check("sector+20% vs nifty+10% → RS ≈ +0.0909", rs is not None and abs(rs - 0.0909) < 0.01,
          f"got {rs}")

    # Same return → RS = 0
    same = [100.0] * 62 + [115.0]
    rs_same = _sector_rs(same, same, 63)
    check("same return → RS = 0.0", rs_same is not None and close_enough(rs_same, 0.0))

    # Not enough bars → None
    check("< period bars → None", _sector_rs([100.0] * 10, [100.0] * 10, 63) is None)

    # Sector down 10%, Nifty up 5% → RS is negative
    sector_down = [100.0] * 62 + [90.0]
    nifty_up    = [100.0] * 62 + [105.0]
    rs_neg = _sector_rs(sector_down, nifty_up, 63)
    check("sector-10% vs nifty+5% → RS < 0", rs_neg is not None and rs_neg < 0, f"got {rs_neg}")


def test_rrg_quadrant_unit() -> None:
    print("\n[Unit] _rrg_quadrant()")
    from market_sage.sector_rs import _rrg_quadrant

    # rs_now > 0, improving momentum → Leading
    check("rs>0 + rising momentum → Leading", _rrg_quadrant(0.10, 0.05) == "Leading")

    # rs_now > 0, declining momentum → Weakening
    check("rs>0 + falling momentum → Weakening", _rrg_quadrant(0.10, 0.15) == "Weakening")

    # rs_now <= 0, improving momentum → Improving
    check("rs<0 + rising momentum → Improving", _rrg_quadrant(-0.05, -0.10) == "Improving")

    # rs_now <= 0, declining momentum → Lagging
    check("rs<0 + falling momentum → Lagging", _rrg_quadrant(-0.05, -0.02) == "Lagging")

    # rs_now exactly 0 → treated as <= 0
    check("rs=0 + improving → Improving", _rrg_quadrant(0.0, -0.05) == "Improving")
    check("rs=0 + declining → Lagging", _rrg_quadrant(0.0, 0.05) == "Lagging")

    # rs_4w_ago is None → classify by rs_now alone
    check("rs>0 + None → Leading", _rrg_quadrant(0.05, None) == "Leading")
    check("rs<0 + None → Lagging", _rrg_quadrant(-0.05, None) == "Lagging")


def test_sectors_registry() -> None:
    print("\n[Unit] SECTORS registry")
    from market_sage.sector_rs import SECTORS, NIFTY50_TICKER

    check("SECTORS has >= 10 entries", len(SECTORS) >= 10, f"got {len(SECTORS)}")
    check("all values start with '^'", all(v.startswith("^") for v in SECTORS.values()))
    check("NIFTY50_TICKER is '^NSEI'", NIFTY50_TICKER == "^NSEI")

    # No duplicate ticker values
    tickers = list(SECTORS.values())
    check("no duplicate tickers", len(tickers) == len(set(tickers)))

    # Key sectors present
    for sector in ["Bank", "IT", "Pharma"]:
        check(f"'{sector}' in SECTORS", sector in SECTORS)


def test_analyze_output_schema_mocked() -> None:
    print("\n[Unit] analyze() output schema (mocked _download_indices)")
    import market_sage.sector_rs as sector_mod

    # Build synthetic: Nifty + 3 sectors, each 90 bars (enough for period=63 + 21 lookback)
    nifty_closes   = [100.0] * 85 + [110.0] * 5  # 90 bars, slight uptrend
    sector_a_closes = [100.0] * 85 + [125.0] * 5  # Leading (outperforming)
    sector_b_closes = [100.0] * 85 + [90.0] * 5   # Lagging  (underperforming)
    sector_c_closes = [100.0] * 90                 # Neutral  (same return as base)

    def _mock_download(tickers, period="6mo"):
        result = {"^NSEI": nifty_closes}
        # Map first 3 sector tickers to synthetic data
        from market_sage.sector_rs import SECTORS
        sector_tickers = list(SECTORS.values())
        if len(sector_tickers) >= 1:
            result[sector_tickers[0]] = sector_a_closes
        if len(sector_tickers) >= 2:
            result[sector_tickers[1]] = sector_b_closes
        if len(sector_tickers) >= 3:
            result[sector_tickers[2]] = sector_c_closes
        return result

    original = sector_mod._download_indices
    sector_mod._download_indices = _mock_download

    try:
        result = sector_mod.analyze(primary_period=63, lookback_period=21)

        check("'sectors' key present", "sectors" in result)
        check("'top_3_sectors' key present", "top_3_sectors" in result)
        check("'avoid_sectors' key present", "avoid_sectors" in result)
        check("'source_date' key present", "source_date" in result)
        check("'period_days' = 63", result.get("period_days") == 63)

        sectors = result.get("sectors", [])
        # At least the sectors with data should be present
        check("sectors list non-empty", len(sectors) > 0)

        # All sectors have required keys
        for s in sectors:
            for key in ["sector", "index", "quadrant", "rank"]:
                check(f"sector '{s.get('sector', '?')}' has key '{key}'", key in s,
                      f"keys={list(s.keys())}")

        # Ranks are sequential starting at 1
        ranks = sorted([s["rank"] for s in sectors if s.get("rank") is not None])
        check("ranks are sequential from 1", ranks == list(range(1, len(ranks) + 1)),
              f"got {ranks}")

        # Quadrant values are valid
        valid_quadrants = {"Leading", "Weakening", "Improving", "Lagging", "Unknown"}
        for s in sectors:
            q = s.get("quadrant")
            check(f"quadrant '{q}' is valid", q in valid_quadrants, f"sector={s.get('sector')}")

    finally:
        sector_mod._download_indices = original


def test_nifty50_missing_graceful() -> None:
    print("\n[Unit] analyze() — graceful when Nifty50 data unavailable")
    import market_sage.sector_rs as sector_mod

    def _mock_no_nifty(tickers, period="6mo"):
        return {}  # No data for any ticker

    original = sector_mod._download_indices
    sector_mod._download_indices = _mock_no_nifty

    try:
        result = sector_mod.analyze(primary_period=63)
        check("error key or empty sectors when no data", "error" in result or result.get("sectors") == [],
              str(result))
        check("no crash — returns dict", isinstance(result, dict))
    finally:
        sector_mod._download_indices = original


# ── Integration tests ─────────────────────────────────────────────────────────

def test_live_sector_rs() -> None:
    print("\n[Live] analyze() — live sector RS (10-20 seconds)")
    from market_sage.sector_rs import analyze

    result = analyze(primary_period=63)

    if "error" in result:
        print(f"       [{SKIP}] Nifty50 data unavailable: {result.get('error')}")
        return

    sectors = result.get("sectors", [])
    check("at least 3 sectors returned", len(sectors) >= 3, f"got {len(sectors)}")

    # Check each sector has valid RS or a no_data error
    for s in sectors:
        if s.get("error") == "no_data":
            continue
        rs = s.get("rs_vs_nifty")
        check(
            f"{s.get('sector','?')}: rs_vs_nifty is float or None",
            rs is None or isinstance(rs, float),
            f"got type={type(rs).__name__} val={rs}",
        )

    valid_quadrants = {"Leading", "Weakening", "Improving", "Lagging", "Unknown"}
    for s in sectors:
        q = s.get("quadrant")
        check(f"{s['sector']}: quadrant valid", q in valid_quadrants, q)

    check("source_date present", bool(result.get("source_date")))
    check("top_3_sectors is list", isinstance(result.get("top_3_sectors"), list))


def test_live_json_output_parseable() -> None:
    print("\n[Live] JSON output is parseable")
    import json
    from market_sage.sector_rs import analyze

    result = analyze(primary_period=63)
    try:
        serialised = json.dumps(result)
        parsed = json.loads(serialised)
        check("result round-trips through JSON", True)
        check("parsed has sectors key", "sectors" in parsed)
    except Exception as exc:
        check("no JSON serialisation error", False, str(exc))


def test_live_ranking_order() -> None:
    print("\n[Live] Sectors are sorted by RS descending")
    from market_sage.sector_rs import analyze

    result = analyze(primary_period=63)
    sectors = [s for s in result.get("sectors", []) if s.get("rs_vs_nifty") is not None]

    if len(sectors) < 2:
        print(f"  [{SKIP}] fewer than 2 sectors with data")
        return

    rs_values = [s["rs_vs_nifty"] for s in sectors]
    sorted_desc = sorted(rs_values, reverse=True)
    check("RS values sorted descending", rs_values == sorted_desc,
          f"got order: {rs_values[:4]}")


# ── Runner ───────────────────────────────────────────────────────────────────

def main() -> None:
    skip_live = os.environ.get("SKIP_LIVE", "").strip() == "1"

    print("=" * 60)
    print("Phase 7 Smoke Tests — ms-sector-rs")
    print("=" * 60)

    # Unit tests (always run)
    test_sector_rs_unit()
    test_rrg_quadrant_unit()
    test_sectors_registry()
    test_analyze_output_schema_mocked()
    test_nifty50_missing_graceful()

    if skip_live:
        print("\n[SKIP_LIVE=1] Skipping live network tests.")
    else:
        print("\n--- Live network tests (yfinance) ---")
        test_live_sector_rs()
        test_live_json_output_parseable()
        test_live_ranking_order()

    print("\n" + "=" * 60)
    if _failures:
        print(f"\033[91mFAILED: {len(_failures)} test(s)\033[0m — {', '.join(_failures)}")
        sys.exit(1)
    else:
        print("\033[92mAll tests passed.\033[0m")


if __name__ == "__main__":
    main()
