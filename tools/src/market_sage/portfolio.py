"""
ms-portfolio FILE.csv [--format kite] [--pretty]

Analyzes a Zerodha Kite holdings CSV (or generic format).
Outputs: position weights, sector allocation, P&L summary,
entry zone guidance, concentration flags, and red flags.

Kite CSV columns:
  Instrument, Qty., Avg. cost, LTP, Invested, Cur. val, P&L, Net chg., Day chg.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from datetime import date
from typing import Optional

import polars as pl
import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(add_completion=False)
console = Console()

# Sector mapping for common NSE stocks
_SECTOR_MAP: dict[str, str] = {
    # Banking / Finance
    "HDFCBANK": "Banking", "ICICIBANK": "Banking", "KOTAKBANK": "Banking",
    "AXISBANK": "Banking", "SBIN": "Banking", "INDUSINDBK": "Banking",
    "BANDHANBNK": "Banking", "FEDERALBNK": "Banking", "IDFCFIRSTB": "Banking",
    "BAJFINANCE": "NBFC/Finance", "BAJAJFINSV": "NBFC/Finance", "CHOLAFIN": "NBFC/Finance",
    "MUTHOOTFIN": "NBFC/Finance", "CDSL": "Capital Markets", "BSE": "Capital Markets",
    "ANGELONE": "Capital Markets", "MCX": "Capital Markets",
    "HDFCAMC": "Wealth/AMC", "NIPPONLIFE": "Wealth/AMC",
    "SBILIFE": "Insurance", "HDFCLIFE": "Insurance", "ICICIlombard": "Insurance",
    "STARHEALTH": "Insurance", "MAXFIN": "Insurance",
    # IT / Tech
    "TCS": "IT Services", "INFY": "IT Services", "WIPRO": "IT Services",
    "HCLTECH": "IT Services", "TECHM": "IT Services", "LTIM": "IT Services",
    "PERSISTENT": "IT Services", "COFORGE": "IT Services",
    "KPITTECH": "Auto Tech/IT", "MPHASIS": "IT Services",
    "MASTEK": "IT Services", "SONATSOFTW": "IT Services",
    # Pharma / Healthcare
    "SUNPHARMA": "Pharma", "DRREDDY": "Pharma", "CIPLA": "Pharma",
    "DIVISLAB": "Pharma", "ABBOTINDIA": "Pharma", "AUROPHARMA": "Pharma",
    "ALKEM": "Pharma", "IPCA": "Pharma", "NATCO": "Pharma",
    "MAXHEALTH": "Healthcare Services", "APOLLOHOSP": "Healthcare Services",
    "FORTIS": "Healthcare Services", "ASTERDM": "Healthcare Services",
    # Consumer / FMCG
    "HINDUNILVR": "FMCG", "ITC": "FMCG", "NESTLEIND": "FMCG",
    "DABUR": "FMCG", "MARICO": "FMCG", "BRITANNIA": "FMCG",
    "TATACONSUM": "FMCG", "EMAMILTD": "FMCG",
    "TITAN": "Consumer Discretionary", "TRENT": "Consumer Retail",
    "DMART": "Consumer Retail", "VMART": "Consumer Retail",
    "VARUNBEV": "Beverages",
    # Auto
    "MARUTI": "Auto", "M&M": "Auto", "TATAMOTORS": "Auto",
    "BAJAJ-AUTO": "Auto", "EICHERMOT": "Auto", "TVSMOTORS": "Auto",
    "HEROMOTOCO": "Auto", "ASHOKLEY": "Auto",
    # Industrials / Capital Goods
    "LT": "Engineering/EPC", "SIEMENS": "Capital Goods", "ABB": "Capital Goods",
    "CGPOWER": "Capital Goods/Power", "BHEL": "Capital Goods",
    "CUMMINSIND": "Capital Goods", "THERMAX": "Capital Goods",
    "VOLTAS": "Consumer Durables",
    # EMS / Electronics
    "DIXON": "EMS/Electronics", "KAYNES": "EMS/Electronics",
    "AMBER": "EMS/Electronics", "SYRMA": "EMS/Electronics",
    # Electrical Cables
    "KEI": "Electrical Cables", "POLYCAB": "Electrical Cables",
    "FINOLEX": "Electrical Cables",
    # Chemicals
    "PIDILITIND": "Specialty Chemicals", "AARTIIND": "Specialty Chemicals",
    "FCL": "Specialty Chemicals", "SUMICHEM": "Specialty Chemicals",
    "PIIND": "Agro Chemicals", "NAVINFLUOR": "Specialty Chemicals",
    "FINEORG": "Specialty Chemicals", "GALAXYSURF": "Specialty Chemicals",
    # Metals / Mining
    "TATASTEEL": "Metals", "JSWSTEEL": "Metals", "HINDALCO": "Metals",
    "VEDL": "Metals", "COALINDIA": "Mining", "NMDC": "Mining",
    # Energy / Oil
    "RELIANCE": "Energy/Petrochemicals", "ONGC": "Oil & Gas",
    "IOC": "Oil & Gas", "BPCL": "Oil & Gas", "GAIL": "Gas",
    "POWERGRID": "Power Utilities", "NTPC": "Power Utilities",
    "ADANIGREEN": "Renewables", "TATAPOWER": "Power",
    # Defence
    "HAL": "Defence", "BEL": "Defence", "SOLARINDS": "Defence",
    "MTAR": "Defence", "DATAPATTNS": "Defence", "PARAS": "Defence",
    # Telecom
    "BHARTIARTL": "Telecom", "INDUS": "Telecom",
    # Cement
    "ULTRACEMCO": "Cement", "SHREECEM": "Cement", "AMBUJACEM": "Cement",
    "ACCLTD": "Cement",
    # Gold/Sovereign
    "SGBOC28VII-GB": "Sovereign Gold Bond",
    "GOLDBEES": "Gold ETF", "SGOLD": "Gold ETF",
}

_DEFAULT_SECTOR = "Others"


def _sector(symbol: str) -> str:
    return _SECTOR_MAP.get(symbol.upper().replace(" ", ""), _DEFAULT_SECTOR)


def _parse_kite_csv(path: Path) -> pl.DataFrame:
    df = pl.read_csv(path, infer_schema_length=100)
    # Kite CSV has trailing empty column and quoted headers — normalise
    df = df.rename({c: c.strip().strip('"') for c in df.columns})
    # Drop unnamed trailing columns
    df = df.select([c for c in df.columns if c and not c.startswith("Unnamed")])
    # Rename to standard names
    rename_map = {
        "Instrument": "symbol",
        "Qty.": "qty",
        "Avg. cost": "avg_cost",
        "LTP": "ltp",
        "Invested": "invested",
        "Cur. val": "cur_val",
        "P&L": "pnl",
        "Net chg.": "net_chg_pct",
        "Day chg.": "day_chg_pct",
    }
    existing = {k: v for k, v in rename_map.items() if k in df.columns}
    df = df.rename(existing)
    # Cast numeric columns
    for col in ["qty", "avg_cost", "ltp", "invested", "cur_val", "pnl", "net_chg_pct", "day_chg_pct"]:
        if col in df.columns:
            df = df.with_columns(
                pl.col(col).cast(pl.Float64, strict=False)
            )
    return df.drop_nulls(subset=["symbol"])


def analyze(df: pl.DataFrame) -> dict:
    total_val = df["cur_val"].sum()
    total_invested = df["invested"].sum()
    total_pnl = df["pnl"].sum()
    total_pnl_pct = (total_pnl / total_invested * 100) if total_invested else 0.0

    # Per-position analysis
    positions = (
        df.with_columns([
            (pl.col("cur_val") / total_val * 100).alias("weight_pct"),
            (pl.col("pnl") / pl.col("invested") * 100).alias("pnl_pct"),
            pl.col("symbol").map_elements(_sector, return_dtype=pl.Utf8).alias("sector"),
            ((pl.col("ltp") - pl.col("avg_cost")) / pl.col("avg_cost") * 100).alias("price_vs_avg_pct"),
        ])
        .sort("cur_val", descending=True)
    )

    # Entry zone guidance (buy zone = ltp * 0.93, strong buy = ltp * 0.85)
    positions = positions.with_columns([
        (pl.col("ltp") * 0.93).round(0).alias("buy_zone_upper"),
        (pl.col("ltp") * 0.85).round(0).alias("strong_buy"),
        (pl.col("ltp") * 1.10).round(0).alias("avoid_above"),
    ])

    # Sector allocation
    sector_alloc = (
        positions.group_by("sector")
        .agg([
            pl.col("cur_val").sum().alias("value"),
            pl.col("symbol").count().alias("stocks"),
        ])
        .with_columns((pl.col("value") / total_val * 100).round(1).alias("weight_pct"))
        .sort("value", descending=True)
    )

    # Red flags
    flags: list[str] = []
    # Concentration: any position > 15% of portfolio
    heavy = positions.filter(pl.col("weight_pct") > 15).select(["symbol", "weight_pct"])
    for row in heavy.iter_rows(named=True):
        flags.append(f"HIGH CONCENTRATION: {row['symbol']} is {row['weight_pct']:.1f}% of portfolio")
    # Losers > -15%
    losers = positions.filter(pl.col("pnl_pct") < -15).select(["symbol", "pnl_pct"])
    for row in losers.iter_rows(named=True):
        flags.append(f"SIGNIFICANT LOSS: {row['symbol']} down {row['pnl_pct']:.1f}% from avg cost")
    # Tiny positions < 1% — not compounding
    tiny = positions.filter(pl.col("weight_pct") < 1.0).select(["symbol", "weight_pct", "cur_val"])
    for row in tiny.iter_rows(named=True):
        flags.append(
            f"NEGLIGIBLE POSITION: {row['symbol']} is only {row['weight_pct']:.1f}% (₹{row['cur_val']:,.0f}) — too small to compound"
        )
    # Single sector > 30%
    heavy_sectors = sector_alloc.filter(pl.col("weight_pct") > 30)
    for row in heavy_sectors.iter_rows(named=True):
        flags.append(f"SECTOR CONCENTRATION: {row['sector']} is {row['weight_pct']:.1f}% of portfolio")

    return {
        "source_date": date.today().isoformat(),
        "summary": {
            "total_invested": round(total_invested, 2),
            "total_current_value": round(total_val, 2),
            "total_pnl": round(total_pnl, 2),
            "total_pnl_pct": round(total_pnl_pct, 1),
            "num_positions": len(df),
        },
        "positions": positions.select([
            "symbol", "sector", "qty", "avg_cost", "ltp",
            "invested", "cur_val", "weight_pct", "pnl", "pnl_pct",
            "buy_zone_upper", "strong_buy", "avoid_above",
        ]).to_dicts(),
        "sector_allocation": sector_alloc.to_dicts(),
        "flags": flags,
    }


def _render_pretty(result: dict) -> None:
    s = result["summary"]
    console.rule("[bold cyan]Portfolio Analysis[/bold cyan]")
    console.print(
        f"Invested: [bold]₹{s['total_invested']:,.0f}[/bold]  "
        f"Current: [bold]₹{s['total_current_value']:,.0f}[/bold]  "
        f"P&L: [bold green]₹{s['total_pnl']:,.0f} ({s['total_pnl_pct']:.1f}%)[/bold green]\n"
    )

    t = Table(title="Positions", header_style="bold cyan")
    for col in ["Symbol", "Sector", "Weight%", "LTP", "Avg Cost", "P&L%", "Buy Zone ≤"]:
        t.add_column(col, justify="right")
    for p in result["positions"]:
        pnl_style = "green" if p["pnl_pct"] >= 0 else "red"
        t.add_row(
            p["symbol"], p["sector"],
            f"{p['weight_pct']:.1f}%",
            f"₹{p['ltp']:,.2f}",
            f"₹{p['avg_cost']:,.2f}",
            f"[{pnl_style}]{p['pnl_pct']:.1f}%[/{pnl_style}]",
            f"₹{p['buy_zone_upper']:,.0f}",
        )
    console.print(t)

    t2 = Table(title="Sector Allocation", header_style="bold cyan")
    for col in ["Sector", "Stocks", "Value", "Weight%"]:
        t2.add_column(col, justify="right")
    for s in result["sector_allocation"]:
        t2.add_row(s["sector"], str(s["stocks"]), f"₹{s['value']:,.0f}", f"{s['weight_pct']:.1f}%")
    console.print(t2)

    if result["flags"]:
        console.print("\n[bold red]⚠ Flags:[/bold red]")
        for f in result["flags"]:
            console.print(f"  • {f}")


@app.command()
def main(
    file: Path = typer.Argument(..., help="Path to Kite holdings CSV"),
    pretty: bool = typer.Option(False, "--pretty", help="Render Rich tables instead of JSON"),
) -> None:
    if not file.exists():
        console.print(f"[red]File not found: {file}[/red]")
        raise typer.Exit(1)
    df = _parse_kite_csv(file)
    result = analyze(df)
    if pretty:
        _render_pretty(result)
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    app()
