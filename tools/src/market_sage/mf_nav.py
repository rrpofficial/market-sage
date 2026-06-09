"""
ms-nav QUERY [--scheme-code CODE] [--list-matches] [--pretty]

Fetches current NAV and fund metadata from AMFI India (api.mfapi.in).
QUERY is a partial fund name (case-insensitive substring match).

Examples:
  ms-nav "HDFC Nifty 50"
  ms-nav "Quant Small Cap"
  ms-nav --scheme-code 120716
  ms-nav "Axis Small" --list-matches
"""

from __future__ import annotations

import json
import re
from datetime import date
from typing import Optional

import requests
import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(add_completion=False)
console = Console()

_AMFI_ALL_URL = "https://api.mfapi.in/mf"
_AMFI_SCHEME_URL = "https://api.mfapi.in/mf/{code}"
_TIMEOUT = 10


def _fetch_all_schemes() -> list[dict]:
    try:
        r = requests.get(_AMFI_ALL_URL, timeout=_TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return [{"error": str(e)}]


def _fetch_scheme(code: int) -> dict:
    try:
        r = requests.get(_AMFI_SCHEME_URL.format(code=code), timeout=_TIMEOUT)
        r.raise_for_status()
        data = r.json()
        meta = data.get("meta", {})
        nav_data = data.get("data", [])
        latest = nav_data[0] if nav_data else {}
        prev = nav_data[1] if len(nav_data) > 1 else {}
        return {
            "scheme_code": code,
            "scheme_name": meta.get("scheme_name", ""),
            "fund_house": meta.get("fund_house", ""),
            "scheme_type": meta.get("scheme_type", ""),
            "scheme_category": meta.get("scheme_category", ""),
            "scheme_sub_category": meta.get("scheme_sub_category", ""),
            "nav": float(latest.get("nav", 0)) if latest else None,
            "nav_date": latest.get("date", ""),
            "prev_nav": float(prev.get("nav", 0)) if prev else None,
            "day_change_pct": round(
                (float(latest["nav"]) - float(prev["nav"])) / float(prev["nav"]) * 100, 3
            ) if latest and prev and float(prev["nav"]) else None,
            "source": f"api.mfapi.in/mf/{code}",
            "source_date": date.today().isoformat(),
        }
    except Exception as e:
        return {"scheme_code": code, "error": str(e)}


def search_schemes(query: str) -> list[dict]:
    all_schemes = _fetch_all_schemes()
    if all_schemes and "error" in all_schemes[0]:
        return all_schemes
    q = query.lower()
    return [s for s in all_schemes if q in s.get("schemeName", "").lower()]


def _render_pretty(results: list[dict], list_only: bool = False) -> None:
    if not results:
        console.print("[yellow]No matching funds found.[/yellow]")
        return
    if list_only:
        t = Table(title="Matching Schemes", header_style="bold cyan")
        t.add_column("Scheme Code", justify="right")
        t.add_column("Scheme Name")
        for r in results:
            t.add_row(str(r.get("scheme_code", "")), r.get("scheme_name", ""))
        console.print(t)
        return
    t = Table(title="MF NAV", header_style="bold cyan")
    for col in ["Scheme Code", "Fund House", "Scheme Name", "NAV (₹)", "NAV Date", "Day%"]:
        t.add_column(col)
    for r in results:
        if "error" in r:
            console.print(f"[red]Error {r.get('scheme_code', '')}: {r['error']}[/red]")
            continue
        day = r.get("day_change_pct")
        day_str = (
            f"[green]+{day}%[/green]" if day and day >= 0 else f"[red]{day}%[/red]"
        ) if day is not None else "—"
        t.add_row(
            str(r.get("scheme_code", "")),
            r.get("fund_house", "")[:30],
            r.get("scheme_name", "")[:50],
            f"₹{r['nav']:,.4f}" if r.get("nav") else "—",
            r.get("nav_date", ""),
            day_str,
        )
    console.print(t)


@app.command()
def main(
    query: Optional[str] = typer.Argument(None, help="Partial fund name to search"),
    scheme_code: Optional[int] = typer.Option(None, "--scheme-code", "-c", help="AMFI scheme code for direct fetch"),
    list_matches: bool = typer.Option(False, "--list-matches", help="Only list scheme codes and names (no NAV fetch)"),
    pretty: bool = typer.Option(False, "--pretty", help="Render Rich table instead of JSON"),
) -> None:
    if scheme_code:
        result = _fetch_scheme(scheme_code)
        output = [result]
    elif query:
        matches = search_schemes(query)
        if not matches:
            console.print(f"[yellow]No schemes found matching '{query}'[/yellow]")
            raise typer.Exit(0)
        if list_matches:
            output = [{"scheme_code": s.get("schemeCode"), "scheme_name": s.get("schemeName")} for s in matches[:20]]
        else:
            # Fetch full data for top 5 matches (rate-limit friendly)
            output = [_fetch_scheme(s["schemeCode"]) for s in matches[:5]]
    else:
        console.print("[red]Provide a fund name query or --scheme-code[/red]")
        raise typer.Exit(1)

    if pretty:
        _render_pretty(output, list_only=list_matches)
    else:
        print(json.dumps(output if len(output) > 1 else output[0], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    app()
