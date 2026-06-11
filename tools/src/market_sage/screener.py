"""
ms-screener SYMBOL [SYMBOL ...] [--standalone] [--pretty]

Fetches fundamentals from Screener.in: key ratios, quarterly results,
annual financials (10Y), shareholding pattern (with DII decomposed into
LIC vs other DIIs), promoter pledging, and peer names.
Outputs JSON by default; --pretty renders Rich tables.
"""

from __future__ import annotations

import json
import re
import sys
import time
from typing import Optional

import requests
import typer
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table

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
_TIMEOUT = 15
_RATE_LIMIT_SLEEP = 1.5  # seconds between requests for multiple symbols


def _get(url: str) -> BeautifulSoup | None:
    try:
        r = requests.get(url, headers=_HEADERS, timeout=_TIMEOUT)
        if r.status_code == 200:
            return BeautifulSoup(r.text, "lxml")
        return None
    except Exception:
        return None


def _get_json(url: str) -> dict | None:
    try:
        headers = {**_HEADERS, "X-Requested-With": "XMLHttpRequest"}
        r = requests.get(url, headers=headers, timeout=_TIMEOUT)
        if r.status_code == 200:
            return r.json()
        return None
    except Exception:
        return None


def _text(el) -> str:
    return el.get_text(strip=True) if el else ""


def _parse_number(s: str) -> float | None:
    s = s.replace(",", "").replace("₹", "").replace("%", "").replace("Cr", "").strip()
    s = s.replace("−", "-")
    try:
        return float(s)
    except ValueError:
        return None


def _parse_top_ratios(soup: BeautifulSoup) -> dict:
    ratios: dict = {}
    section = soup.find(id="top-ratios")
    if not section:
        return ratios
    for li in section.find_all("li"):
        name_el = li.find("span", class_="name")
        val_el = li.find("span", class_="number") or li.find("span", class_="value")
        if not val_el:
            val_el = li.find("span", attrs={"class": lambda c: c and "number" in c})
        if name_el and val_el:
            key = _text(name_el).lower().replace(" ", "_").replace(".", "").replace("/", "_")
            raw = _text(val_el)
            ratios[key] = _parse_number(raw) if _parse_number(raw) is not None else raw
    return ratios


def _parse_data_table(section) -> dict[str, list]:
    """Returns {col_header: [row_values ...]} where first col is row labels."""
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
    rows: dict[str, list] = {h: [] for h in headers}
    for tr in tbody.find_all("tr"):
        cells = [_text(td) for td in tr.find_all(["td", "th"])]
        for i, h in enumerate(headers):
            rows[h].append(cells[i] if i < len(cells) else "")
    return rows


def _parse_quarterly(soup: BeautifulSoup) -> dict:
    section = soup.find(id="quarters")
    return _parse_data_table(section)


def _parse_annual(soup: BeautifulSoup) -> dict:
    section = soup.find(id="profit-loss")
    return _parse_data_table(section)


def _parse_balance_sheet(soup: BeautifulSoup) -> dict:
    section = soup.find(id="balance-sheet")
    return _parse_data_table(section)


def _parse_ratios_section(soup: BeautifulSoup) -> dict:
    section = soup.find(id="ratios")
    return _parse_data_table(section)


def _parse_shareholding(soup: BeautifulSoup) -> dict:
    section = soup.find(id="shareholding")
    if not section:
        return {}
    result: dict = {}
    for table in section.find_all("table"):
        caption = table.find("caption") or table.find("thead")
        label = _text(caption).lower() if caption else "pattern"
        rows = _parse_data_table(table)
        if rows:
            result[label] = rows
    return result


def _parse_promoter_pledging(soup: BeautifulSoup) -> dict:
    """Promoter pledge % and QoQ trend.

    Primary: an explicit pledge row inside the shareholding tables (only present
    for some accounts/pages; kept for forward-compatibility). Fallback: screener.in's
    auto-generated analysis text ("Promoters have pledged X% of their holding"),
    which is in the static HTML but carries no quarterly history.
    """
    section = soup.find(id="shareholding")
    if section:
        for tr in section.find_all("tr"):
            cells = [_text(c) for c in tr.find_all(["td", "th"])]
            if cells and "pledg" in cells[0].lower():
                vals = [v for v in (_parse_number(c) for c in cells[1:]) if v is not None]
                if vals:
                    latest = vals[-1]
                    prev = vals[-2] if len(vals) >= 2 else None
                    qoq = round(latest - prev, 2) if prev is not None else None
                    if qoq is None:
                        trend = "unknown"
                    elif qoq < -1:
                        trend = "falling"
                    elif qoq > 1:
                        trend = "rising"
                    else:
                        trend = "stable"
                    return {
                        "pledging_available": True,
                        "source": "shareholding_table",
                        "latest_pct": latest,
                        "prev_pct": prev,
                        "qoq_change": qoq,
                        "trend": trend,
                    }

    m = re.search(r"[Pp]romoters have pledged\s+([\d.]+)%", soup.get_text(" ", strip=True))
    if m:
        return {
            "pledging_available": True,
            "source": "analysis_text",
            "latest_pct": float(m.group(1)),
            "prev_pct": None,
            "qoq_change": None,
            "trend": "unknown",
        }
    return {"pledging_available": False}


_LIC_NAME_PATTERNS = ("life insurance corporation", "lici ")


def _latest_dii_total(soup: BeautifulSoup) -> float | None:
    """Most recent quarterly DII holding % from the shareholding pattern table."""
    quarterly = soup.find(id="quarterly-shp") or soup.find(id="shareholding")
    if not quarterly:
        return None
    for tr in quarterly.find_all("tr"):
        cells = [_text(c) for c in tr.find_all(["td", "th"])]
        if cells and cells[0].lower().startswith("dii"):
            vals = [v for v in (_parse_number(c) for c in cells[1:]) if v is not None]
            return vals[-1] if vals else None
    return None


def _parse_dii_split(soup: BeautifulSoup) -> dict:
    """Decompose DII holding into LIC vs other DIIs via screener.in's investors API.

    LIC's investment decisions can be politically directed; it must never be cited
    as institutional-confidence evidence without this decomposition.
    """
    out = {
        "dii_total_pct": _latest_dii_total(soup),
        "lic_holding_pct": None,
        "private_mf_holding_pct": None,
        "dii_split_available": False,
        "dii_note": None,
    }

    id_el = soup.find(attrs={"data-company-id": True})
    if not id_el:
        return out
    company_id = id_el["data-company-id"]
    data = _get_json(f"https://www.screener.in/api/3/{company_id}/investors/domestic_institutions/quarterly/")
    if not data:
        return out

    lic_pct = 0.0
    lic_found = False
    for name, row in data.items():
        if not isinstance(row, dict):
            continue
        lname = name.lower()
        if any(p in lname for p in _LIC_NAME_PATTERNS):
            vals = [v for v in (_parse_number(str(x)) for q, x in row.items() if q != "setAttributes") if v is not None]
            if vals:
                lic_pct += vals[-1]
                lic_found = True

    if lic_found:
        out["lic_holding_pct"] = round(lic_pct, 2)
        if out["dii_total_pct"] is not None:
            out["private_mf_holding_pct"] = round(out["dii_total_pct"] - lic_pct, 2)
        out["dii_split_available"] = True
        out["dii_note"] = (
            "LIC holding decomposed — treat LIC separately from private MF conviction. "
            "private_mf_holding_pct = total DII minus LIC (includes non-LIC insurers/pension funds)."
        )
    else:
        out["dii_note"] = "LIC not listed separately among disclosed DII holders (holders below 1% are not disclosed)."
    return out


def _parse_peers(soup: BeautifulSoup) -> list[str]:
    section = soup.find(id="peers")
    if not section:
        return []
    peers = []
    for a in section.find_all("a", href=True):
        href = a["href"]
        if "/company/" in href:
            name = _text(a)
            if name:
                peers.append(name)
    return list(dict.fromkeys(peers))  # deduplicate preserving order


def fetch_symbol(symbol: str, standalone: bool = False) -> dict:
    variant = "standalone" if standalone else "consolidated"
    url = f"https://www.screener.in/company/{symbol.upper()}/{variant}/"
    soup = _get(url)

    if soup is None and not standalone:
        url = f"https://www.screener.in/company/{symbol.upper()}/"
        soup = _get(url)

    if soup is None:
        return {"symbol": symbol, "error": "fetch_failed", "url": url}

    # Check for login wall or 404
    if soup.find("form", id="login-form") or "Page not found" in soup.get_text():
        return {"symbol": symbol, "error": "not_found_or_login_required", "url": url}

    return {
        "symbol": symbol.upper(),
        "source": url,
        "source_date": _today(),
        "top_ratios": _parse_top_ratios(soup),
        "quarterly_results": _parse_quarterly(soup),
        "annual_pl": _parse_annual(soup),
        "balance_sheet": _parse_balance_sheet(soup),
        "key_ratios_history": _parse_ratios_section(soup),
        "shareholding": {**_parse_shareholding(soup), **_parse_dii_split(soup)},
        "promoter_pledging": _parse_promoter_pledging(soup),
        "peers": _parse_peers(soup),
    }


def _today() -> str:
    from datetime import date
    return date.today().isoformat()


def _render_pretty(data: dict) -> None:
    if "error" in data:
        console.print(f"[red]Error for {data['symbol']}: {data['error']}[/red]")
        return

    console.rule(f"[bold cyan]{data['symbol']} — Screener.in[/bold cyan]")
    console.print(f"[dim]Source: {data['source']} | Date: {data['source_date']}[/dim]\n")

    ratios = data.get("top_ratios", {})
    if ratios:
        t = Table(title="Key Ratios", show_header=True)
        t.add_column("Metric", style="cyan")
        t.add_column("Value", justify="right")
        for k, v in ratios.items():
            t.add_row(k.replace("_", " ").title(), str(v))
        console.print(t)

    qtr = data.get("quarterly_results", {})
    if qtr:
        headers = list(qtr.keys())
        n_rows = len(qtr[headers[0]]) if headers else 0
        t = Table(title="Quarterly Results (last 4)", show_header=True)
        for h in headers[:5]:
            t.add_column(h, justify="right")
        for i in range(min(4, n_rows)):
            t.add_row(*[str(qtr[h][i]) if i < len(qtr[h]) else "" for h in headers[:5]])
        console.print(t)

    pledge = data.get("promoter_pledging", {})
    if pledge.get("pledging_available"):
        trend = pledge.get("trend", "unknown")
        arrow = {"rising": "[red]▲ rising[/red]", "falling": "[green]▼ falling[/green]",
                 "stable": "stable"}.get(trend, "[dim]trend n/a[/dim]")
        qoq = f" (QoQ {pledge['qoq_change']:+.2f}pp)" if pledge.get("qoq_change") is not None else ""
        console.print(f"\n[bold]Promoter Pledge:[/bold] {pledge['latest_pct']}% — {arrow}{qoq}")
    elif pledge:
        console.print("\n[dim]Promoter pledge: no pledging detected / not disclosed[/dim]")

    sh = data.get("shareholding", {})
    if sh.get("dii_split_available"):
        console.print(
            f"[bold]DII Split:[/bold] Total {sh['dii_total_pct']}%  |  "
            f"LIC {sh['lic_holding_pct']}%  |  non-LIC DII {sh['private_mf_holding_pct']}%"
        )
        console.print(f"[dim]{sh['dii_note']}[/dim]")
    elif sh.get("dii_total_pct") is not None:
        console.print(f"[bold]DII Total:[/bold] {sh['dii_total_pct']}%  [dim]({sh.get('dii_note', 'LIC split unavailable')})[/dim]")

    peers = data.get("peers", [])
    if peers:
        console.print(f"\n[bold]Peers:[/bold] {', '.join(peers[:6])}")


@app.command()
def main(
    symbols: list[str] = typer.Argument(..., help="NSE symbol(s), e.g. KAYNES CDSL"),
    standalone: bool = typer.Option(False, "--standalone", help="Fetch standalone instead of consolidated"),
    pretty: bool = typer.Option(False, "--pretty", help="Render Rich tables instead of JSON"),
) -> None:
    results = []
    for i, sym in enumerate(symbols):
        if i > 0:
            time.sleep(_RATE_LIMIT_SLEEP)
        data = fetch_symbol(sym, standalone=standalone)
        results.append(data)
        if pretty:
            _render_pretty(data)

    if not pretty:
        print(json.dumps(results if len(results) > 1 else results[0], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    app()
