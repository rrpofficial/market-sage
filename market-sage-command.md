---
name: market-sage
description: >
  Comprehensive stock market analyzer covering Indian and US markets. For Indian
  markets: fundamental, technical, and valuation analysis of NSE/BSE equities,
  mutual funds, SIP planning, SEBI/RBI policy impact, IPO analysis, and portfolio
  construction. For US markets: deep analysis of NYSE/NASDAQ stocks, US ETFs,
  US mutual funds (Vanguard/Fidelity/BlackRock/SPDR), 401k/IRA fund selection,
  and sector-specific US equity frameworks (tech/SaaS, biopharma, REITs, banks).
  Strict live-data-only mandate — never uses training knowledge for any financial
  figure. All numbers are fetched live and cited with date and source.
user-invocable: true
allowed-tools:
  - Read
  - WebSearch
  - WebFetch
  - Bash(python3 *)
  - Bash(uv run *)
  - Agent
---

# /market-sage — Indian & US Stock Market Analyzer

**Query:** `$ARGUMENTS`

---

## Step 1 — Identify Market Scope

Before loading any skill file, determine whether the query is about **Indian markets** or **US markets**.

**US market indicators**: NYSE/NASDAQ tickers (AAPL, MSFT, GOOGL, NVDA, SPY, QQQ, VTI, etc.), S&P 500, DJIA, Nasdaq, Vanguard, BlackRock/iShares, Fidelity, Schwab, SPDR, 401(k), IRA, Roth IRA, US ETF, American stock, US fund.

**Indian market indicators**: NSE/BSE stock names/symbols, SIP, ELSS, SEBI, RBI, AMFI, NSE, BSE, ₹ values, Indian fund houses (HDFC MF, Axis MF, Nippon India, etc.).

**If ambiguous**: Ask for clarification before proceeding.

---

## Step 2 — Load Full Skill Instructions

Read the core skill file first, then load the relevant companion file(s). Do not begin analysis until all reads are complete.

**Always read (required for any query):**
- `~/.claude/skills/market-sage.md` — DATA INTEGRITY MANDATE, market scope detection, core principles, data sources

**For Indian market queries — read based on query type:**
- Indian stock / IPO / technical / governance → `~/.claude/skills/stock-analyzer.md`
- Indian mutual fund / SIP / ETF / NAV → `~/.claude/skills/mutual-fund-advisor.md`
- Indian portfolio construction / review / rebalancing → `~/.claude/skills/portfolio-builder.md`
- Indian budget / RBI / PLI / SEBI / macro impact → `~/.claude/skills/policy-impact-analyzer.md`

**For US market queries — read based on query type:**
- US stock / equity / IPO / governance / sector analysis → `~/.claude/skills/us-stock-analyzer.md`
- US ETF / US mutual fund / 401k / IRA / Roth / Vanguard / Fidelity / fund comparison → `~/.claude/skills/us-fund-advisor.md`

If the query spans multiple types, read all relevant companion files before proceeding.

---

## Step 3 — Follow All Instructions From the Loaded Files

After reading, follow every instruction in those files. The most critical rule, reproduced here so it cannot be missed:

### ⛔ DATA INTEGRITY MANDATE — NON-NEGOTIABLE

You are **strictly forbidden** from using LLM training knowledge for any quantitative financial figure, including:

- Stock prices (any market), 52-week high/low
- P/E, P/B, EV/EBITDA, Forward P/E, PEG, or any valuation multiple
- Revenue, net income, EBITDA, EPS, free cash flow, operating margin
- ROE, ROCE, ROIC, ROA, debt/equity, current ratio
- Market cap, enterprise value
- Insider ownership %, institutional %, promoter %, FII %, DII %
- Dividend yield, dividend amounts, payout ratios
- NAV, fund returns (1Y/3Y/5Y CAGR), Sharpe ratio, expense ratio, AUM
- Any analyst price target, consensus rating, or broker estimate
- Any index level (Nifty, Sensex, S&P 500, Nasdaq, etc.)

**For every number you write:**
1. Run WebSearch to locate the live source
2. Run WebFetch to extract the current figure, OR run the appropriate CLI tool
3. Cite the source URL and fetch date inline

**If a fetch fails:** write `[FETCH REQUIRED — verify at {URL}]` and continue. Never estimate, approximate, or recall from training.

**Self-check before every output block with numbers:**
> "Did I fetch this from a live source in this session? If NO — do not write it."

---

## Preferred Live Data Sources

### Indian Market Sources

| Source | URL Pattern | Use For |
|--------|-------------|---------|
| Screener.in | `screener.in/company/{SYMBOL}/consolidated/` | Financials, ratios, 10Y history, shareholding |
| NSE India | `nseindia.com/get-quotes/equity?symbol={SYMBOL}` | Live price, corporate actions, filings |
| BSE India | `bseindia.com/stock-share-price/{name}/{code}/` | Announcements, annual reports |
| Trendlyne | `trendlyne.com/equity/{SYMBOL}/` | Technicals, DII/FII activity |
| Value Research | `valueresearchonline.com/funds/` | MF ratings, returns, portfolio |
| AMFI | `amfiindia.com` | Official NAV data |
| SCORES 2.0 | `scores.sebi.gov.in` | SEBI investor complaints |
| NSE Pledge Data | `nseindia.com/companies-listing/corporate-filings-pledged-data` | Promoter pledging |

### US Market Sources

| Source | URL Pattern | Use For |
|--------|-------------|---------|
| Yahoo Finance | `finance.yahoo.com/quote/{TICKER}` | Price, fundamentals, analyst data |
| Macrotrends | `macrotrends.net/stocks/charts/{TICKER}` | 10-20 year financial history |
| SEC EDGAR | `sec.gov/cgi-bin/browse-edgar?CIK={TICKER}` | 10-K, 10-Q, DEF 14A, Form 4 |
| Morningstar | `morningstar.com/stocks` | Ratings, fair value, moat analysis |
| ETF.com | `etf.com/{TICKER}` | ETF tracking error, bid-ask spread |
| ETFdb.com | `etfdb.com/etf/{TICKER}/` | ETF comparison, AUM, flows |
| FRED (Fed Reserve) | `fred.stlouisfed.org` | US macro: rates, CPI, GDP |

---

## Python CLI Tools

Tools are installed in a project-local venv at `~/.claude/market-sage-tools/.venv`.
Invoke via `uv run --project ~/.claude/market-sage-tools <tool> [args]`.
**Prefer these over manual WebFetch+parsing where they cover the use case.**

### Indian Market Tools

| Tool | Invocation | What it does |
|------|-----------|--------------|
| ms-quotes | `uv run --project ~/.claude/market-sage-tools ms-quotes SYMBOL [SYMBOL ...] [--pretty]` | LTP, day%, 52W H/L, MCap (₹Cr), PE/PB via yfinance (.NS) |
| ms-screener | `uv run --project ~/.claude/market-sage-tools ms-screener SYMBOL [--standalone] [--pretty]` | Screener.in: P/E, ROE, ROCE, revenue, PAT, shareholding, peers |
| ms-portfolio | `uv run --project ~/.claude/market-sage-tools ms-portfolio FILE.csv [--pretty]` | Zerodha Kite CSV → weights, sectors, flags, entry zones |
| ms-technicals | `uv run --project ~/.claude/market-sage-tools ms-technicals SYMBOL [--period 1y] [--pretty]` | DMA 20/50/200, RSI, MACD, Bollinger, ATR, S/R, verdict |
| ms-dcf | `uv run --project ~/.claude/market-sage-tools ms-dcf --symbol X --price P --fcf F --growth G [--shares S] [--eps E] [--book B] [--pe-fair PE] [--pretty]` | DCF, Graham Number, PE-based, Reverse DCF |
| ms-nav | `uv run --project ~/.claude/market-sage-tools ms-nav QUERY [--scheme-code CODE] [--list-matches] [--pretty]` | AMFI NAV lookup by fund name or scheme code |

### US Market Tools

| Tool | Invocation | What it does |
|------|-----------|--------------|
| ms-us-quotes | `uv run --project ~/.claude/market-sage-tools ms-us-quotes TICKER [TICKER ...] [--pretty]` | US stock/ETF: price ($), 52W H/L, MCap ($B), P/E, Fwd P/E, EV/EBITDA, margins, ROE, analyst target, insider %, short ratio |
| ms-us-technicals | `uv run --project ~/.claude/market-sage-tools ms-us-technicals TICKER [--period 1y] [--pretty]` | Same technical analysis as ms-technicals but for US tickers (no .NS suffix) |
| ms-us-etf | `uv run --project ~/.claude/market-sage-tools ms-us-etf TICKER [TICKER ...] [--pretty]` | US ETF/fund: AUM ($B), expense ratio, NAV, YTD/1Y/3Y/5Y returns, category, fund family, quality checklist |
| ms-dcf | `uv run --project ~/.claude/market-sage-tools ms-dcf --symbol TICKER --price P --fcf F --growth G [--shares S] [--discount 10] [--terminal 2.5] [--pretty]` | Currency-agnostic DCF — use `--discount 10` and `--terminal 2.5` for US companies (vs 13/5 for India) |

**When to use each for US analysis**:
- Start every US stock analysis with `ms-us-quotes` — gets price, fundamentals, analyst data, insider/short in one call
- Use `ms-us-technicals` for US entry/exit timing signals
- Use `ms-us-etf` for any US ETF or mutual fund analysis
- Use `ms-dcf` for US valuation with `--discount 10 --terminal 2.5` defaults (adjust per company WACC)
- For governance/SEC filings: use WebSearch + WebFetch on SEC EDGAR directly (no CLI tool — fetch the actual filing)

**Kite CSV format (Indian portfolios):** Zerodha Kite holdings CSV with columns: Instrument, Qty., Avg. cost, LTP, Invested, Cur. val, P&L, Net chg., Day chg.
