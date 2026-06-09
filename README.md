# Market Sage

Stock market analyzer skill for Claude Code. Covers **Indian markets** (NSE/BSE equities, mutual funds, SIP planning, SEBI/RBI policy, forensic accounting & governance screening) and **US markets** (NYSE/NASDAQ stocks, US ETFs, US mutual funds, 401k/IRA fund selection). Enforces a strict live-data-only mandate — never uses training memory for any financial figure.

## Prerequisites

- [Claude Code](https://claude.ai/code) CLI installed and authenticated
- [uv](https://docs.astral.sh/uv/getting-started/installation/) — Python package manager

## Installation

```bash
./install.sh
```

Follow the prompts to select modules. Recommended presets:

| Preset | Modules | Best for |
|--------|---------|----------|
| 1 | Stock + Policy | Indian stock picking, IPO analysis |
| 2 | Stock + Forensic + Policy | Indian stock analysis with forensic accounting screen |
| 3 | MF + Portfolio + Policy | Indian fund investors, portfolio review |
| 4 | US Investor | US stocks, ETFs, 401k/IRA fund selection |
| 5 | All | Full Indian + US capability |

The installer:
- Copies skill files to `~/.claude/skills/`
- Registers `/market-sage` as a slash command in `~/.claude/commands/`
- Sets up Python tools in `~/.claude/market-sage-tools/.venv/` via `uv sync`

## Usage

In any Claude Code session:

```
/market-sage Analyze CDSL stock
/market-sage Review my portfolio — attached is my Kite holdings CSV
/market-sage Compare SBI Life vs HDFC Life
/market-sage Best mid-cap funds for 15-year SIP
/market-sage How does the PLI scheme affect Dixon Electronics?

# Forensic / governance queries
/market-sage Run a forensic accounting check on Brightcom Group — any red flags?
/market-sage What is the governance quality of Zee Entertainment? Check auditor, RPTs, contingent liabilities.
/market-sage Do a Financial Shenanigans screen on Adani Enterprises

# US markets
/market-sage Analyze NVDA — is it overvalued at current prices?
/market-sage Compare SPY vs QQQ vs VTI for a 30-year retirement account
/market-sage Best Vanguard/Fidelity funds for my Roth IRA
/market-sage Is AAPL a buy at current levels?
/market-sage Analyze my 401k fund options and suggest an allocation
```

## Python CLI Tools

Ten CLI tools are available under `~/.claude/market-sage-tools/.venv/`. Claude invokes them automatically during analysis. You can also run them directly:

### Indian Market Tools

```bash
uv run --project ~/.claude/market-sage-tools ms-quotes HDFCAMC CDSL --pretty
uv run --project ~/.claude/market-sage-tools ms-screener KAYNES --pretty
uv run --project ~/.claude/market-sage-tools ms-technicals KEI --pretty
uv run --project ~/.claude/market-sage-tools ms-portfolio kite_holdings.csv --pretty
uv run --project ~/.claude/market-sage-tools ms-nav "Quant Small Cap" --pretty
uv run --project ~/.claude/market-sage-tools ms-dcf --symbol CDSL --price 1212 --fcf 560 --growth 20 --shares 1.05 --pretty

# Forensic accounting screen (new)
uv run --project ~/.claude/market-sage-tools ms-forensic CDSL --years 5 --pretty
uv run --project ~/.claude/market-sage-tools ms-forensic BRIGHTCOM --pretty       # high-risk example
uv run --project ~/.claude/market-sage-tools ms-forensic ZOMATO --years 7
```

### US Market Tools

```bash
uv run --project ~/.claude/market-sage-tools ms-us-quotes AAPL MSFT NVDA --pretty
uv run --project ~/.claude/market-sage-tools ms-us-technicals NVDA --period 1y --pretty
uv run --project ~/.claude/market-sage-tools ms-us-etf SPY QQQ VTI BND --pretty
uv run --project ~/.claude/market-sage-tools ms-dcf --symbol AAPL --price 195 --fcf 100 --growth 8 --shares 15.4 --discount 10 --terminal 2.5 --pretty
```

### Tool Reference

| Tool | Market | What it does |
|------|--------|-------------|
| `ms-quotes` | India | Live price (₹), day%, 52W H/L, MCap, PE/PB from yfinance |
| `ms-screener` | India | Screener.in fundamentals: P/E, ROE, ROCE, revenue, PAT, shareholding, peers |
| `ms-technicals` | India | DMA 20/50/200, RSI, MACD, Bollinger Bands, ATR, support/resistance, verdict |
| `ms-portfolio` | India | Zerodha Kite CSV → weights, sectors, concentration flags, entry zones |
| `ms-nav` | India | AMFI NAV lookup by fund name or scheme code |
| `ms-dcf` | Both | DCF, Graham Number, PE-based, Reverse DCF (India: 13% discount / 5% terminal; US: 10% / 2.5%) |
| `ms-forensic` | India | **Forensic accounting screen** — DSO divergence, DIO-margin decoupling, CWIP aging, CFO/PAT (O'Glove test), DPO inflation; outputs preliminary Manipulation Risk Score |
| `ms-us-quotes` | US | Price ($), 52W H/L, MCap ($B), P/E, Fwd P/E, EV/EBITDA, margins, ROE, analyst target, insider %, short ratio |
| `ms-us-technicals` | US | Same technical analysis as ms-technicals for US tickers |
| `ms-us-etf` | US | US ETF/fund: AUM, expense ratio, NAV, YTD/1Y/3Y/5Y returns, category, quality checklist |

## Skill Modules

| File | Market | Contents |
|------|--------|---------|
| `market-sage.md` | Both | Core — data integrity rules, market scope routing, sources, session protocol |
| `stock-analyzer.md` | India | Fundamentals, technicals, IPO, governance, moat — Indian equities (8-step framework) |
| `stock-governance-quality-framework.md` | India | **Forensic accounting & governance framework** — Schilit's Financial Shenanigans + O'Glove's Quality of Earnings. 12-check screen across 4 buckets: earnings manipulation, cash flow misdirection, metric distortion, governance hard filters. Outputs Manipulation Risk Score (MRS) 🟢/🟡/🟠/🔴/🚫 |
| `mutual-fund-advisor.md` | India | Fund selection, SIP, ETFs, NAV, SEBI/AMFI categories |
| `portfolio-builder.md` | India | Asset allocation, rebalancing, tax efficiency, income planning |
| `policy-impact-analyzer.md` | India | Budget, RBI, PLI, SEBI, macro impact on sectors |
| `us-stock-analyzer.md` | US | Deep US equity analysis — SEC governance, SaaS/REIT/biopharma frameworks, WACC, DCF |
| `us-fund-advisor.md` | US | US ETF/MF analysis, 3-fund portfolio, 401k/IRA asset location, expense ratio benchmarks |

## Forensic Accounting Framework

The `stock-governance-quality-framework.md` module implements a forensic screen based on Howard Schilit's *Financial Shenanigans* (4th ed.) and Thornton O'Glove's *Quality of Earnings*. It's invoked when:

- You ask for a governance deep-dive, red flag check, or earnings quality screen
- `stock-analyzer.md` returns a **Weak** or **Avoid** governance rating — it escalates automatically
- A company has: active SEBI orders, promoter pledge >10%, recent auditor change, acquisition-driven growth, or unexplained margin expansion

### What it checks

| Section | Check | Auto-computed by `ms-forensic`? |
|---------|-------|---------------------------------|
| Earnings Manipulation | 1.1 DSO-to-Revenue Divergence | ✅ Yes |
| Earnings Manipulation | 1.2 Unbilled Revenue / Contract Assets | ❌ Manual (Annual Report Notes) |
| Earnings Manipulation | 1.3 DIO-Gross Margin Decoupling | ✅ Yes |
| Earnings Manipulation | 1.4 Expense Capitalization / CWIP Aging | ✅ Yes (CWIP component) |
| Cash Flow Quality | 2.1 CFO vs Net Profit — O'Glove Test | ✅ Yes (annual + rolling 3Y) |
| Cash Flow Quality | 2.2 AP Inflation / DPO Trend | ✅ Yes |
| Cash Flow Quality | 2.3 Classification Arbitrage | ❌ Manual (CFO breakdown) |
| Metric Distortion | 3.1 Non-GAAP Variance | ❌ Manual (investor presentations) |
| Metric Distortion | 3.2 M&A Goodwill Spring-Loading | ❌ Manual (acquisition disclosures) |
| Governance Hard Filters | 4.1 Related Party Transaction Gate | ❌ Manual (Annual Report Notes) |
| Governance Hard Filters | 4.2 Auditor Integrity | ❌ Manual (NSE/BSE filings) |
| Governance Hard Filters | 4.3 Contingent Liabilities Burden | ❌ Manual (Annual Report Notes) |

### Manipulation Risk Score (MRS)

The framework produces a single MRS rating:

| Rating | Meaning | Effect on stock verdict |
|--------|---------|------------------------|
| 🟢 GREEN | No quantitative red flags | Governance scores 8-10/10 |
| 🟡 AMBER | 1-2 caution flags | Governance scores 5-7/10 |
| 🟠 ORANGE | Any Red flag OR 3+ Amber | Governance scores 2-4/10; total score **capped at 6/10** |
| 🔴 RED | 2+ Red flags | Verdict forced to **AVOID** |
| 🚫 HARD REJECT | Binary trigger (auditor resignation, CL > Net Worth, RPT "not arm's length") | **AVOID — DO NOT INVEST** regardless of financials |

### Hard Reject triggers (automatic AVOID)

Any of these forces an immediate AVOID regardless of how good the financial metrics look:

1. Auditor mid-term resignation with vague reason ("preoccupation of time")
2. Auditor adverse opinion or disclaimer of opinion
3. Auditor qualifies RPTs as "not fully arm's length"
4. Contingent liabilities exceed total Net Worth

## Market Routing

The skill auto-detects which market is relevant from your query:

- **US indicators**: NYSE/NASDAQ tickers (AAPL, MSFT, NVDA…), SPY/QQQ/VTI, Vanguard/BlackRock/Fidelity/SPDR/Schwab, 401(k)/IRA/Roth IRA, "US stock/ETF/fund"
- **Indian indicators**: NSE/BSE symbols, SIP/ELSS/NPS, SEBI/RBI/AMFI, Indian fund houses (HDFC MF, Axis MF, Nippon India…)
- **Forensic/governance**: "forensic accounting", "financial shenanigans", "earnings quality", "red flag check", "related party transactions", "auditor resignation", "contingent liabilities", "governance deep dive"

## Updating Tools

If you pull new changes to this repo, re-sync the installed tools:

```bash
cp -r tools/. ~/.claude/market-sage-tools/
uv sync --project ~/.claude/market-sage-tools
```

---

> **Disclaimer:** Educational tool only. Not financial advice. Consult a SEBI-registered investment advisor (India) or SEC-registered RIA (US) before investing.
