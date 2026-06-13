# Market Sage

Stock market analyzer skill for Claude Code. Covers **Indian markets** (NSE/BSE equities, mutual funds, SIP planning, SEBI/RBI policy, forensic accounting & governance screening, and **momentum / swing-trade analysis**) and **US markets** (NYSE/NASDAQ stocks, US ETFs, US mutual funds, 401k/IRA fund selection). Enforces a strict live-data-only mandate — never uses training memory for any financial figure.

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
| 5 | All | Full Indian + US capability (includes Momentum Sage) |

The **Momentum Sage** module (`momentum-sage.md`) is included in preset 5 (All) and can be added to any install via the **Custom** option (module name `momentum`). Its six CLI tools install automatically with the tools project regardless of which skill modules you pick.

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

# Momentum / swing-trade queries (3M–1Y horizon)
/market-sage Is the market in a momentum-friendly phase right now?
/market-sage Which sectors are showing leadership?
/market-sage Score KAYNES for momentum — Stage Analysis + SEPA + composite
/market-sage Screen Nifty Midcap 150 for momentum plays
/market-sage Best entry for CDSL — pullback or breakout? Size it for a ₹5L portfolio at 1% risk

# US markets
/market-sage Analyze NVDA — is it overvalued at current prices?
/market-sage Compare SPY vs QQQ vs VTI for a 30-year retirement account
/market-sage Best Vanguard/Fidelity funds for my Roth IRA
/market-sage Is AAPL a buy at current levels?
/market-sage Analyze my 401k fund options and suggest an allocation
```

## Python CLI Tools

Sixteen CLI tools are available under `~/.claude/market-sage-tools/.venv/`. Claude invokes them automatically during analysis. You can also run them directly:

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

### Indian Momentum Tools

```bash
# Single-stock momentum, RS rank, and volume quality
uv run --project ~/.claude/market-sage-tools ms-momentum-score KAYNES HDFCBANK CDSL --pretty
uv run --project ~/.claude/market-sage-tools ms-rs-rank KAYNES --vs NIFTY500 --pretty
uv run --project ~/.claude/market-sage-tools ms-volume-profile KAYNES --pretty

# Market context: breadth (go/no-go) and sector rotation (RRG)
uv run --project ~/.claude/market-sage-tools ms-breadth --index NIFTY50 --pretty
uv run --project ~/.claude/market-sage-tools ms-sector-rs --period 63 --pretty

# Full-pipeline orchestrator → ranked momentum buy-list with entry/stop/size
uv run --project ~/.claude/market-sage-tools ms-momentum-screen --symbols KAYNES CDSL INFY --min-score 0 --pretty
uv run --project ~/.claude/market-sage-tools ms-momentum-screen --index NIFTYMIDCAP150 --portfolio 500000 --pretty
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
| `ms-momentum-score` | India | **Momentum** — 1M/3M/6M/12M/12-1M returns, annualised volatility, volatility-adjusted momentum (Sharpe-like selector) |
| `ms-rs-rank` | India | **Momentum** — IBD-style RS Rating (1-99 percentile vs universe) + Mansfield RS vs Nifty 50 |
| `ms-breadth` | India | **Momentum** — market breadth go/no-go: % above 200/50 DMA, A/D ratio, 52W H/L counts, Bullish/Neutral/Bearish regime |
| `ms-sector-rs` | India | **Momentum** — sector RS vs Nifty 50 + RRG quadrants (Leading/Improving/Weakening/Lagging) |
| `ms-volume-profile` | India | **Momentum** — OBV (+divergence), CMF, RVOL, 52W anchored VWAP, NR7/NR4 contraction, volume verdict |
| `ms-momentum-screen` | India | **Momentum orchestrator** — 100-pt composite (momentum/RS/SEPA/ADX/volume/fundamental gate), entry setup, ATR position size; ranked buy-list |
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
| `momentum-sage.md` | India | **Momentum / swing-trade analyzer (3M–1Y)** — Weinstein Stage Analysis, Minervini SEPA Template, CAN SLIM, Dual Momentum, IBD RS Rating, market breadth, sector RRG, volume confirmation, ATR position sizing. Five modes (Market Pulse, Sector Scan, Stock Score, Universe Screen, Entry Advisor) |
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

## Momentum Analysis (momentum-sage)

The `momentum-sage.md` module is a specialist sub-skill for **medium-term (3-month to
1-year) swing trading** of NSE/BSE equities. It fuses fundamental quality with price and
volume momentum so you get the upside of a trending stock with a fundamental safety net.
It is invoked through `/market-sage` for any momentum, swing-trade, Stage Analysis, SEPA,
RS Rating, breakout, market-breadth, or sector-rotation query.

### Five analysis modes (auto-detected from your query)

| Mode | Ask it like… | What it does |
|------|--------------|--------------|
| **Market Pulse** | "Is the market momentum-friendly?" | Breadth go/no-go gate (% above 200 DMA, A/D ratio, 52W H/L, Nifty vs 200 DMA) |
| **Sector Scan** | "Which sectors are leading?" | RRG quadrant classification of NSE sectors vs Nifty 50 |
| **Stock Score** | "Score KAYNES for momentum" | Full Stage Analysis + SEPA + 100-point composite for one stock |
| **Universe Screen** | "Screen Nifty Midcap 150" | Batch-rank an index by composite score |
| **Entry Advisor** | "Best entry for CDSL?" | Setup type (pullback/breakout/NR7/extended) + ATR entry, stop, position size |

### The 100-point composite score

Each stock is scored on eight components; **qualify for the buy-list = score ≥ 65 AND the
fundamental gate is not hard-failed** (D/E > 3 or ROE < 0 forces the total to 0):

| Component | Weight | Tool |
|-----------|:------:|------|
| 12-1M price momentum (intra-universe percentile) | 20 | `ms-momentum-score` |
| 6M price momentum (percentile) | 10 | `ms-momentum-score` |
| Volatility-adjusted momentum | 10 | `ms-momentum-score` |
| IBD-style RS Rating | 15 | `ms-rs-rank` |
| SEPA Trend Template (8 conditions) | 15 | `ms-technicals` |
| ADX trend strength | 10 | `ms-technicals` |
| OBV + CMF volume confirmation | 10 | `ms-volume-profile` |
| Fundamental quality gate (ROE/D-E/EPS growth) | 10 | `ms-screener` |

The `ms-momentum-screen` orchestrator computes this end-to-end — it calls the other tools
as in-process Python modules, ranks the universe, and emits entry setups with ATR-based
position sizing. RS Rating and momentum are computed in a single batch download for the
whole universe (not per-symbol), and the IBD RS Rating is injected into SEPA condition 8.

### Frameworks applied

Stan Weinstein **Stage Analysis** (only Stage 2 is buyable) · Mark Minervini **SEPA Trend
Template** · William O'Neil **CAN SLIM** (market direction is non-negotiable) · Gary
Antonacci **Dual Momentum** · IBD **RS Rating** & **Mansfield RS** · **volatility-adjusted
momentum** · **ADX** trend strength · **OBV/CMF/RVOL** volume quality · **NR7** volatility
contraction · **Fibonacci** pullback zones · **ATR-based position sizing**.

### India-specific signals & policies

Delivery % (conviction filter), FII/DII net flow, F&O ban status, and promoter-pledging
trend are read live. **LIC decomposition rule:** LIC holding is never cited as
"institutional confidence" without qualification — its decisions can be politically
directed, so DII is always decomposed into LIC vs private-MF components.

> **Live-data mandate (momentum-specific):** RS Ratings, Stage classifications, and SEPA
> results change *weekly*; Delivery%, FII/DII flow, and F&O ban status change *daily*. The
> skill is forbidden from ever recalling any of these from training memory — every figure
> comes from a live `ms-*` tool call, cited with date and source.

## Market Routing

The skill auto-detects which market is relevant from your query:

- **US indicators**: NYSE/NASDAQ tickers (AAPL, MSFT, NVDA…), SPY/QQQ/VTI, Vanguard/BlackRock/Fidelity/SPDR/Schwab, 401(k)/IRA/Roth IRA, "US stock/ETF/fund"
- **Indian indicators**: NSE/BSE symbols, SIP/ELSS/NPS, SEBI/RBI/AMFI, Indian fund houses (HDFC MF, Axis MF, Nippon India…)
- **Forensic/governance**: "forensic accounting", "financial shenanigans", "earnings quality", "red flag check", "related party transactions", "auditor resignation", "contingent liabilities", "governance deep dive"
- **Momentum/swing-trade**: "momentum", "swing trade", "stage analysis", "SEPA", "CAN SLIM", "RS rating", "relative strength", "market breadth", "sector rotation", "breakout setup", "NR7", "go/no-go market", "dual momentum"

## Updating Tools

If you pull new changes to this repo, re-sync the installed tools:

```bash
cp -r tools/. ~/.claude/market-sage-tools/
uv sync --project ~/.claude/market-sage-tools
```

---

> **Disclaimer:** Educational tool only. Not financial advice. Consult a SEBI-registered investment advisor (India) or SEC-registered RIA (US) before investing.
