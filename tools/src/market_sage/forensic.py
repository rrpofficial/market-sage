"""
ms-forensic SYMBOL [--years N] [--standalone] [--pretty]

Forensic accounting screen based on Howard Schilit's Financial Shenanigans
and Thornton O'Glove's Quality of Earnings. Computes quantitative early-warning
metrics directly from Screener.in data for all checks that can be derived from
structured financial statements.

Computable checks (auto-scored):
  1.1  DSO-to-Revenue Divergence     — debtor days vs revenue growth
  1.3  DIO-Gross Margin Decoupling   — inventory days vs operating margin
  1.4  CWIP Aging                    — capital work-in-progress as % of fixed assets
  2.1  CFO vs Net Profit (O'Glove)   — annual + rolling 3Y CFO/PAT ratio
  2.2  DPO Inflation                 — days payable outstanding trend
  2.x  CapEx / Revenue trend         — supporting signal for check 1.4

Manual checks required (not computable from Screener.in):
  1.2  Unbilled Revenue / Contract Assets — in Annual Report Notes
  2.3  Cash Flow Classification Arbitrage — requires detailed CFO breakdown
  3.1  Non-GAAP Variance              — requires investor presentations
  3.2  M&A Goodwill Spring-Loading    — requires acquisition disclosures
  4.1  Related Party Transactions     — in Annual Report Notes
  4.2  Auditor Integrity              — NSE/BSE filing history
  4.3  Contingent Liabilities         — in Annual Report Notes

Usage:
  ms-forensic CDSL --pretty
  ms-forensic ZOMATO --years 5 --pretty
  ms-forensic BRIGHTCOM --pretty          # high-fraud-risk example
  ms-forensic HDFCAMC --years 7
"""

from __future__ import annotations

import json
import time
from datetime import date
from typing import Optional

import requests
import typer
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from rich.text import Text

app = typer.Typer(add_completion=False)
console = Console()

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml",
    "Referer": "https://www.screener.in/",
}
_TIMEOUT = 20


# ── Low-level fetch & parse helpers ───────────────────────────────────────────

def _get(url: str) -> BeautifulSoup | None:
    try:
        r = requests.get(url, headers=_HEADERS, timeout=_TIMEOUT)
        return BeautifulSoup(r.text, "lxml") if r.status_code == 200 else None
    except Exception:
        return None


def _text(el) -> str:
    return el.get_text(strip=True) if el else ""


def _parse_number(s: str) -> float | None:
    """Parse Screener.in number strings: handles ₹, %, Cr, commas, − (minus sign)."""
    if not s:
        return None
    s = s.replace(",", "").replace("₹", "").replace("%", "").replace("Cr", "").strip()
    s = s.replace("−", "-").replace("–", "-")  # en-dash → minus
    try:
        return float(s)
    except ValueError:
        return None


def _parse_data_table(section) -> dict[str, list[str]]:
    """Returns {col_header: [row_values]} where the first col ('') holds row labels."""
    if not section:
        return {}
    table = section.find("table")
    if not table:
        return {}
    thead = table.find("thead")
    tbody = table.find("tbody")
    if not thead or not tbody:
        return {}
    headers = [_text(th) for th in thead.find_all("th")]
    rows: dict[str, list[str]] = {h: [] for h in headers}
    for tr in tbody.find_all("tr"):
        cells = [_text(td) for td in tr.find_all(["td", "th"])]
        for i, h in enumerate(headers):
            rows[h].append(cells[i] if i < len(cells) else "")
    return rows


# ── Time-series extraction helpers ────────────────────────────────────────────

def _year_cols(table: dict[str, list[str]]) -> list[str]:
    """Return all column keys that look like fiscal years (not the row-label col)."""
    return [k for k in table if k.strip() not in ("", "TTM")]


def _find_row(table: dict[str, list[str]], *keywords: str) -> int | None:
    """Find the row index whose label contains ALL given keywords (case-insensitive)."""
    labels = table.get("", [])
    kw_lower = [k.lower() for k in keywords]
    for i, label in enumerate(labels):
        lab = label.lower()
        if all(k in lab for k in kw_lower):
            return i
    return None


def _find_row_any(table: dict[str, list[str]], *keywords: str) -> int | None:
    """Find the row index whose label contains ANY of the given keywords."""
    labels = table.get("", [])
    kw_lower = [k.lower() for k in keywords]
    for i, label in enumerate(labels):
        lab = label.lower()
        if any(k in lab for k in kw_lower):
            return i
    return None


def _series(table: dict[str, list[str]], row_idx: int, years: list[str]) -> list[float | None]:
    """Extract the numeric series for a given row across the specified year columns."""
    result = []
    for yr in years:
        col = table.get(yr, [])
        val = col[row_idx] if row_idx < len(col) else ""
        result.append(_parse_number(val))
    return result


# ── Screener.in section parsers ───────────────────────────────────────────────

def _fetch_screener(symbol: str, standalone: bool = False) -> BeautifulSoup | None:
    variant = "standalone" if standalone else "consolidated"
    soup = _get(f"https://www.screener.in/company/{symbol.upper()}/{variant}/")
    if soup is None and not standalone:
        soup = _get(f"https://www.screener.in/company/{symbol.upper()}/")
    return soup


def _parse_section(soup: BeautifulSoup, section_id: str) -> dict[str, list[str]]:
    section = soup.find(id=section_id)
    return _parse_data_table(section)


# ── Core forensic calculation ─────────────────────────────────────────────────

def _yoy_change(series: list[float | None]) -> list[float | None]:
    """Compute YoY % change for a series. Index 0 is always None (no prior year)."""
    result: list[float | None] = [None]
    for i in range(1, len(series)):
        prev, curr = series[i - 1], series[i]
        if prev and curr and prev != 0:
            result.append(round((curr - prev) / abs(prev) * 100, 1))
        else:
            result.append(None)
    return result


def _rolling_ratio(numerator: list[float | None], denominator: list[float | None], window: int = 3) -> list[float | None]:
    """Rolling sum ratio over `window` periods."""
    result: list[float | None] = [None] * len(numerator)
    for i in range(window - 1, len(numerator)):
        num_vals = numerator[i - window + 1: i + 1]
        den_vals = denominator[i - window + 1: i + 1]
        if all(v is not None for v in num_vals) and all(v is not None for v in den_vals):
            s_num = sum(num_vals)  # type: ignore[arg-type]
            s_den = sum(den_vals)  # type: ignore[arg-type]
            result[i] = round(s_num / s_den, 2) if s_den != 0 else None
        else:
            result[i] = None
    return result


# ── Flag evaluators ───────────────────────────────────────────────────────────

_GREEN = "GREEN"
_AMBER = "AMBER"
_RED = "RED"
_INSUFFICIENT = "INSUFFICIENT_DATA"


def _flag_dso_divergence(dso: list[float | None], rev: list[float | None], years: list[str]) -> list[dict]:
    """Check 1.1 — DSO growing faster than revenue (per-year flags)."""
    flags = []
    dso_yoy = _yoy_change(dso)
    rev_yoy = _yoy_change(rev)
    for i in range(1, len(years)):
        d, r = dso_yoy[i], rev_yoy[i]
        if d is None or r is None:
            continue
        divergence = d - r
        yr = years[i]
        if d > 0 and (r <= 0):
            flags.append({"year": yr, "dso_yoy": d, "rev_yoy": r, "status": _RED,
                           "detail": f"DSO grew {d:+.1f}% while revenue {r:+.1f}% (flat/declining)"})
        elif divergence > 20:
            flags.append({"year": yr, "dso_yoy": d, "rev_yoy": r, "status": _RED,
                           "detail": f"DSO outpaced revenue by {divergence:.1f}pp (threshold: >20pp)"})
        elif divergence > 15:
            flags.append({"year": yr, "dso_yoy": d, "rev_yoy": r, "status": _AMBER,
                           "detail": f"DSO outpaced revenue by {divergence:.1f}pp (threshold: >15pp)"})
    return flags


def _flag_dio_margin(dio: list[float | None], opm: list[float | None], rev: list[float | None], years: list[str]) -> list[dict]:
    """Check 1.3 — DIO rising while operating margin stays flat/expands."""
    flags = []
    dio_yoy = _yoy_change(dio)
    opm_chg = _yoy_change(opm)
    rev_yoy = _yoy_change(rev)
    for i in range(1, len(years)):
        d, m, r = dio_yoy[i], opm_chg[i], rev_yoy[i]
        if d is None:
            continue
        yr = years[i]
        if d > 30 and m is not None and m >= 0 and r is not None and r <= 0:
            flags.append({"year": yr, "dio_yoy": d, "opm_change_pp": m, "status": _RED,
                           "detail": f"DIO +{d:.1f}%, margin {m:+.1f}pp while revenue {r:+.1f}% — over-production signal"})
        elif d > 20 and m is not None and m >= -1:
            flags.append({"year": yr, "dio_yoy": d, "opm_change_pp": m, "status": _AMBER,
                           "detail": f"DIO +{d:.1f}% while margin held ({m:+.1f}pp) — overhead capitalisation possible"})
    return flags


def _flag_cwip(cwip: list[float | None], fixed: list[float | None], years: list[str]) -> list[dict]:
    """Check 1.4 partial — CWIP as % of (CWIP + Net Fixed Assets)."""
    flags = []
    amber_streak = 0
    for i, yr in enumerate(years):
        c, f = cwip[i], fixed[i]
        if c is None or f is None:
            continue
        base = c + f
        if base <= 0:
            continue
        ratio = c / base * 100
        if ratio > 35:
            flags.append({"year": yr, "cwip_pct": round(ratio, 1), "status": _RED,
                           "detail": f"CWIP is {ratio:.1f}% of fixed assets — chronically stalled project spend"})
            amber_streak += 1
        elif ratio > 25:
            flags.append({"year": yr, "cwip_pct": round(ratio, 1), "status": _AMBER,
                           "detail": f"CWIP is {ratio:.1f}% of fixed assets — elevated, monitor conversion"})
            amber_streak += 1
        else:
            amber_streak = 0
    # Sequential CWIP growth
    cwip_yoy = _yoy_change(cwip)
    consec_growth = 0
    for i in range(1, len(years)):
        if cwip_yoy[i] is not None and cwip_yoy[i] > 0:  # type: ignore[operator]
            consec_growth += 1
        else:
            consec_growth = 0
        if consec_growth >= 3:
            flags.append({"year": years[i], "cwip_yoy": cwip_yoy[i], "status": _AMBER,
                           "detail": f"CWIP growing for {consec_growth}+ consecutive years — not converting to productive assets"})
            break
    return flags


def _flag_cfo_pat(cfo: list[float | None], pat: list[float | None], years: list[str]) -> tuple[list[dict], float | None]:
    """Check 2.1 — CFO vs Net Profit (annual + rolling 3Y)."""
    flags = []
    annual_ratios: list[float | None] = []
    for i, yr in enumerate(years):
        c, p = cfo[i], pat[i]
        if c is None or p is None or p == 0:
            annual_ratios.append(None)
            continue
        ratio = round(c / p, 2)
        annual_ratios.append(ratio)
        if c < 0 and p > 0:
            flags.append({"year": yr, "cfo_cr": c, "pat_cr": p, "ratio": ratio, "status": _RED,
                           "detail": f"CFO negative (₹{c:.0f}Cr) while PAT positive (₹{p:.0f}Cr) — cash burning business"})
        elif ratio < 0.8:
            flags.append({"year": yr, "ratio": ratio, "status": _AMBER,
                           "detail": f"Annual CFO/PAT = {ratio} (threshold: <0.8)"})

    # Consecutive annual < 0.8
    consec_low = 0
    for i, r in enumerate(annual_ratios):
        if r is not None and r < 0.8:
            consec_low += 1
            if consec_low >= 2:
                flags.append({"year": years[i], "ratio": r, "status": _AMBER,
                               "detail": f"CFO/PAT below 0.8 for {consec_low}+ consecutive years"})
        else:
            consec_low = 0

    # Rolling 3Y
    rolling = _rolling_ratio(cfo, pat, window=3)
    r3y: float | None = None
    for i in range(len(years) - 1, -1, -1):
        if rolling[i] is not None:
            r3y = rolling[i]
            break
    if r3y is not None and r3y < 0.8:
        flags.append({"period": f"Rolling 3Y ending {years[-1]}", "ratio": r3y, "status": _RED,
                       "detail": f"Rolling 3Y CFO/PAT = {r3y} — O'Glove hard rule: cumulative earnings quality failure (threshold: <0.8)"})

    return flags, r3y


def _flag_dpo(dpo: list[float | None], years: list[str]) -> list[dict]:
    """Check 2.2 — DPO inflation (AP days expanding unusually)."""
    flags = []
    dpo_yoy = _yoy_change(dpo)
    for i in range(1, len(years)):
        d = dpo_yoy[i]
        if d is None:
            continue
        yr = years[i]
        if d > 30:
            flags.append({"year": yr, "dpo_yoy": d, "status": _RED,
                           "detail": f"DPO grew {d:+.1f}% — investigate reverse factoring / vendor financing"})
        elif d > 20:
            flags.append({"year": yr, "dpo_yoy": d, "status": _AMBER,
                           "detail": f"DPO grew {d:+.1f}% — possible AP inflation boosting CFO"})
    return flags


# ── Overall preliminary MRS ───────────────────────────────────────────────────

def _preliminary_mrs(all_flags: list[dict]) -> str:
    reds = sum(1 for f in all_flags if f.get("status") == _RED)
    ambers = sum(1 for f in all_flags if f.get("status") == _AMBER)
    if reds >= 2:
        return "🔴 RED — Multiple Red flags: HIGH probability of earnings manipulation. DO NOT proceed without manual Section 4 checks."
    if reds == 1:
        return "🟠 ORANGE — Single Red flag detected: SIGNIFICANT concern. Manual forensic review required before investing."
    if ambers >= 3:
        return "🟠 ORANGE — 3+ Amber flags: Significant pattern of caution signals across multiple checks."
    if ambers >= 1:
        return "🟡 AMBER — Caution flags detected. Investigate flagged areas. Complete Section 4 manual checks."
    return "🟢 GREEN (quantitative checks only) — No red flags in computable metrics. Complete Section 4 manual checks before final MRS."


# ── Main analysis function ────────────────────────────────────────────────────

def run_forensic(symbol: str, n_years: int = 5, standalone: bool = False) -> dict:
    soup = _fetch_screener(symbol, standalone)
    if soup is None:
        return {"symbol": symbol.upper(), "error": "fetch_failed", "source": "screener.in"}
    if soup.find("form", id="login-form") or "Page not found" in soup.get_text():
        return {"symbol": symbol.upper(), "error": "not_found_or_login_required", "source": "screener.in"}

    pl_table = _parse_section(soup, "profit-loss")
    bs_table = _parse_section(soup, "balance-sheet")
    cf_table = _parse_section(soup, "cash-flow")
    ratios_table = _parse_section(soup, "ratios")

    # Select year columns (most recent n_years from ratios; ratios table has the most consistent year headers)
    all_year_cols = _year_cols(ratios_table) or _year_cols(pl_table)
    year_cols = all_year_cols[-n_years:] if len(all_year_cols) >= n_years else all_year_cols
    n = len(year_cols)

    def _s(table: dict, row_idx: int | None) -> list[float | None]:
        if row_idx is None:
            return [None] * n
        return _series(table, row_idx, year_cols)

    # ── P&L rows ──────────────────────────────────────────────────────────────
    rev_idx = _find_row_any(pl_table, "sales", "revenue")
    pat_idx = _find_row_any(pl_table, "net profit", "profit after tax", "pat")
    opm_idx = _find_row_any(pl_table, "opm", "operating profit margin", "opm %")

    revenue = _s(pl_table, rev_idx)
    pat = _s(pl_table, pat_idx)
    opm = _s(pl_table, opm_idx)

    # ── Balance sheet rows ────────────────────────────────────────────────────
    fixed_idx = _find_row_any(bs_table, "fixed assets", "tangible assets", "property, plant")
    cwip_idx = _find_row_any(bs_table, "capital work", "cwip", "work-in-progress", "work in progress")
    goodwill_idx = _find_row_any(bs_table, "goodwill")

    fixed_assets = _s(bs_table, fixed_idx)
    cwip = _s(bs_table, cwip_idx)
    goodwill = _s(bs_table, goodwill_idx)

    # ── Cash flow rows ────────────────────────────────────────────────────────
    cfo_idx = _find_row_any(cf_table, "operating activity", "operating activities", "cash from operations")
    capex_idx = _find_row_any(cf_table, "capital expenditure", "purchase of fixed", "purchase of property",
                               "investing activity", "investing activities")

    cfo = _s(cf_table, cfo_idx)
    capex_raw = _s(cf_table, capex_idx)
    # CapEx is typically a cash outflow (negative in CFI). Normalise to positive.
    capex = [abs(v) if v is not None else None for v in capex_raw]

    # ── Key ratios rows ───────────────────────────────────────────────────────
    dso_idx = _find_row_any(ratios_table, "debtor days", "days sales", "receivable days")
    dio_idx = _find_row_any(ratios_table, "inventory days", "inventory turnover", "days inventory")
    dpo_idx = _find_row_any(ratios_table, "days payable", "payable days", "creditor days")

    dso = _s(ratios_table, dso_idx)
    dio = _s(ratios_table, dio_idx)
    dpo = _s(ratios_table, dpo_idx)

    # If OPM not in P&L, try ratios table
    if all(v is None for v in opm):
        opm_r_idx = _find_row_any(ratios_table, "opm", "operating margin")
        opm = _s(ratios_table, opm_r_idx)

    # ── Forensic flag computation ─────────────────────────────────────────────
    dso_flags = _flag_dso_divergence(dso, revenue, year_cols)
    dio_flags = _flag_dio_margin(dio, opm, revenue, year_cols)
    cwip_flags = _flag_cwip(cwip, fixed_assets, year_cols)
    cfo_flags, rolling_3y_cfo_pat = _flag_cfo_pat(cfo, pat, year_cols)
    dpo_flags = _flag_dpo(dpo, year_cols)

    all_flags = dso_flags + dio_flags + cwip_flags + cfo_flags + dpo_flags

    # CapEx / Revenue — supplementary signal
    capex_rev_pct: list[float | None] = []
    for c, r in zip(capex, revenue):
        if c is not None and r is not None and r > 0:
            capex_rev_pct.append(round(c / r * 100, 1))
        else:
            capex_rev_pct.append(None)

    # Annual CFO/PAT for display
    annual_cfo_pat: list[float | None] = []
    for c, p in zip(cfo, pat):
        if c is not None and p is not None and p != 0:
            annual_cfo_pat.append(round(c / p, 2))
        else:
            annual_cfo_pat.append(None)

    check_status: dict[str, str] = {
        "1.1 DSO-Revenue Divergence": _RED if any(f["status"] == _RED for f in dso_flags) else _AMBER if dso_flags else (_GREEN if any(v is not None for v in dso) else _INSUFFICIENT),
        "1.3 DIO-Margin Decoupling": _RED if any(f["status"] == _RED for f in dio_flags) else _AMBER if dio_flags else (_GREEN if any(v is not None for v in dio) else _INSUFFICIENT),
        "1.4 CWIP Aging": _RED if any(f["status"] == _RED for f in cwip_flags) else _AMBER if cwip_flags else (_GREEN if any(v is not None for v in cwip) else _INSUFFICIENT),
        "2.1 CFO vs Net Profit": _RED if any(f["status"] == _RED for f in cfo_flags) else _AMBER if cfo_flags else (_GREEN if any(v is not None for v in cfo) else _INSUFFICIENT),
        "2.2 DPO Inflation": _RED if any(f["status"] == _RED for f in dpo_flags) else _AMBER if dpo_flags else (_GREEN if any(v is not None for v in dpo) else _INSUFFICIENT),
    }

    manual_required = [
        "1.2 Unbilled Revenue / Contract Assets — fetch from Annual Report Notes",
        "2.3 Cash Flow Classification Arbitrage — review CFO breakdown in Annual Report",
        "3.1 Non-GAAP Variance — compare statutory vs investor presentation PAT",
        "3.2 M&A Goodwill Spring-Loading — review post-acquisition disclosures",
        "4.1 Related Party Transactions — Notes to Accounts (Annual Report)",
        "4.2 Auditor Integrity — NSE/BSE corporate announcements, audit fee notes",
        "4.3 Contingent Liabilities — Notes to Accounts (Annual Report)",
    ]

    return {
        "symbol": symbol.upper(),
        "source": "screener.in (consolidated)",
        "source_date": date.today().isoformat(),
        "years_analysed": year_cols,
        "raw_data": {
            "revenue_cr": revenue,
            "net_profit_cr": pat,
            "cfo_cr": cfo,
            "capex_cr": capex,
            "dso_days": dso,
            "dio_days": dio,
            "dpo_days": dpo,
            "opm_pct": opm,
            "cwip_cr": cwip,
            "net_fixed_assets_cr": fixed_assets,
            "goodwill_cr": goodwill if any(v is not None for v in goodwill) else None,
        },
        "forensic_ratios": {
            "annual_cfo_pat": annual_cfo_pat,
            "rolling_3y_cfo_pat": rolling_3y_cfo_pat,
            "dso_yoy_change_pct": _yoy_change(dso),
            "revenue_growth_pct": _yoy_change(revenue),
            "dio_yoy_change_pct": _yoy_change(dio),
            "opm_change_pp": _yoy_change(opm),
            "dpo_yoy_change_pct": _yoy_change(dpo),
            "capex_revenue_pct": capex_rev_pct,
        },
        "flags": all_flags,
        "check_status": check_status,
        "preliminary_mrs": _preliminary_mrs(all_flags),
        "manual_checks_required": manual_required,
        "data_coverage_notes": _coverage_notes(dso, dio, dpo, cfo, cwip),
    }


def _coverage_notes(dso, dio, dpo, cfo, cwip) -> list[str]:
    notes = []
    if all(v is None for v in dso):
        notes.append("DSO (Debtor Days) not found in Screener.in ratios — verify manually from balance sheet")
    if all(v is None for v in dio):
        notes.append("DIO (Inventory Days) not found — may be a services/financial company (non-applicable)")
    if all(v is None for v in dpo):
        notes.append("DPO (Days Payable) not found — verify from balance sheet trade payables and COGS")
    if all(v is None for v in cfo):
        notes.append("CFO not found in cash flow section — verify manually; this is the most critical metric")
    if all(v is None for v in cwip):
        notes.append("CWIP not found in balance sheet — may be a services/asset-light company (non-applicable)")
    return notes


# ── Rich pretty-printer ───────────────────────────────────────────────────────

_STATUS_STYLE = {_GREEN: "green", _AMBER: "yellow", _RED: "red", _INSUFFICIENT: "dim"}


def _status_cell(status: str) -> Text:
    icons = {_GREEN: "✅ GREEN", _AMBER: "⚠  AMBER", _RED: "🔴 RED", _INSUFFICIENT: "— N/A"}
    return Text(icons.get(status, status), style=_STATUS_STYLE.get(status, ""))


def _fmt(val: float | None, decimals: int = 1, suffix: str = "") -> str:
    if val is None:
        return "—"
    return f"{val:,.{decimals}f}{suffix}"


def _render_pretty(data: dict) -> None:
    if "error" in data:
        console.print(f"[red]Error: {data['error']} — {data['symbol']}[/red]")
        return

    yrs = data["years_analysed"]
    rd = data["raw_data"]
    fr = data["forensic_ratios"]

    console.rule(f"[bold cyan]Forensic Screen — {data['symbol']}[/bold cyan]")
    console.print(f"[dim]Source: {data['source']} | Date: {data['source_date']} | Years: {', '.join(yrs)}[/dim]\n")

    # ── Raw data table ──────────────────────────────────────────────────────
    t = Table(title="Raw Financial Data", show_header=True, header_style="bold")
    t.add_column("Metric", style="cyan", min_width=28)
    for y in yrs:
        t.add_column(y, justify="right", min_width=10)

    rows_raw = [
        ("Revenue (₹Cr)", rd["revenue_cr"]),
        ("Net Profit (₹Cr)", rd["net_profit_cr"]),
        ("CFO (₹Cr)", rd["cfo_cr"]),
        ("CapEx (₹Cr)", rd["capex_cr"]),
        ("DSO (days)", rd["dso_days"]),
        ("DIO (days)", rd["dio_days"]),
        ("DPO (days)", rd["dpo_days"]),
        ("OPM (%)", rd["opm_pct"]),
        ("CWIP (₹Cr)", rd["cwip_cr"]),
        ("Net Fixed Assets (₹Cr)", rd["net_fixed_assets_cr"]),
    ]
    if rd.get("goodwill_cr") and any(v is not None for v in rd["goodwill_cr"]):
        rows_raw.append(("Goodwill (₹Cr)", rd["goodwill_cr"]))

    for label, vals in rows_raw:
        t.add_row(label, *[_fmt(v) for v in vals])
    console.print(t)

    # ── Forensic ratios table ───────────────────────────────────────────────
    t2 = Table(title="Forensic Ratios (YoY)", show_header=True, header_style="bold")
    t2.add_column("Ratio", style="cyan", min_width=28)
    for y in yrs:
        t2.add_column(y, justify="right", min_width=10)

    rows_fr = [
        ("CFO / Net Profit (annual)", fr["annual_cfo_pat"]),
        ("Revenue Growth %", fr["revenue_growth_pct"]),
        ("DSO YoY Change %", fr["dso_yoy_change_pct"]),
        ("DIO YoY Change %", fr["dio_yoy_change_pct"]),
        ("OPM Change (pp)", fr["opm_change_pp"]),
        ("DPO YoY Change %", fr["dpo_yoy_change_pct"]),
        ("CapEx / Revenue %", fr["capex_revenue_pct"]),
    ]
    for label, vals in rows_fr:
        t2.add_row(label, *[_fmt(v) for v in vals])

    r3y = data["forensic_ratios"]["rolling_3y_cfo_pat"]
    t2.add_row("[bold]Rolling 3Y CFO/PAT[/bold]", *["—"] * (len(yrs) - 1), f"[bold]{_fmt(r3y, 2)}[/bold]")
    console.print(t2)

    # ── Check status summary ────────────────────────────────────────────────
    t3 = Table(title="Computable Check Status", show_header=True, header_style="bold")
    t3.add_column("Check", style="cyan", min_width=35)
    t3.add_column("Status", min_width=14)
    for check, status in data["check_status"].items():
        t3.add_row(check, _status_cell(status))
    console.print(t3)

    # ── Flags detail ────────────────────────────────────────────────────────
    if data["flags"]:
        t4 = Table(title="Flag Details", show_header=True, header_style="bold red")
        t4.add_column("Year/Period", min_width=18)
        t4.add_column("Status", min_width=10)
        t4.add_column("Detail")
        for f in data["flags"]:
            yr = f.get("year") or f.get("period", "—")
            st = f.get("status", "")
            t4.add_row(str(yr), _status_cell(st), f.get("detail", ""))
        console.print(t4)

    # ── MRS preliminary ─────────────────────────────────────────────────────
    console.print()
    console.rule("[bold]Preliminary MRS (quantitative checks only)[/bold]")
    mrs_style = "red" if "RED" in data["preliminary_mrs"] else "yellow" if "AMBER" in data["preliminary_mrs"] or "ORANGE" in data["preliminary_mrs"] else "green"
    console.print(f"[{mrs_style}]{data['preliminary_mrs']}[/{mrs_style}]")

    # ── Manual checks reminder ──────────────────────────────────────────────
    console.print()
    console.print("[bold dim]Manual checks still required for full MRS:[/bold dim]")
    for m in data["manual_checks_required"]:
        console.print(f"  [dim]• {m}[/dim]")

    if data["data_coverage_notes"]:
        console.print()
        console.print("[bold dim]Data coverage notes:[/bold dim]")
        for n in data["data_coverage_notes"]:
            console.print(f"  [yellow]⚠ {n}[/yellow]")


# ── CLI entry point ───────────────────────────────────────────────────────────

@app.command()
def main(
    symbol: str = typer.Argument(..., help="NSE symbol, e.g. CDSL, ZOMATO, BRIGHTCOM"),
    years: int = typer.Option(5, "--years", "-y", help="Number of fiscal years to analyse (default 5, max 10)"),
    standalone: bool = typer.Option(False, "--standalone", help="Use standalone financials instead of consolidated"),
    pretty: bool = typer.Option(False, "--pretty", help="Render Rich tables instead of JSON"),
) -> None:
    years = min(max(years, 2), 10)
    data = run_forensic(symbol, n_years=years, standalone=standalone)
    if pretty:
        _render_pretty(data)
    else:
        print(json.dumps(data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    app()
