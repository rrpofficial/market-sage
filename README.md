# Market Sage

Stock market analyzer skill for Claude Code. Covers both **Indian markets** (NSE/BSE equities, mutual funds, SIP planning, SEBI/RBI policy) and **US markets** (NYSE/NASDAQ stocks, US ETFs, US mutual funds, 401k/IRA fund selection). Enforces a strict live-data-only mandate — never uses training memory for any financial figure.

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
| 2 | MF + Portfolio + Policy | Indian fund investors, portfolio review |
| 3 | US Investor | US stocks, ETFs, 401k/IRA fund selection |
| 4 | All | Full Indian + US capability |

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
/market-sage Analyze NVDA — is it overvalued at current prices?
/market-sage Compare SPY vs QQQ vs VTI for a 30-year retirement account
/market-sage Best Vanguard/Fidelity funds for my Roth IRA
/market-sage Is AAPL a buy at current levels?
/market-sage Analyze my 401k fund options and suggest an allocation
```

## Python CLI Tools

Nine CLI tools are available under `~/.claude/market-sage-tools/.venv/`. Claude invokes them automatically during analysis. You can also run them directly:

### Indian Market Tools

```bash
uv run --project ~/.claude/market-sage-tools ms-quotes HDFCAMC CDSL --pretty
uv run --project ~/.claude/market-sage-tools ms-screener KAYNES --pretty
uv run --project ~/.claude/market-sage-tools ms-technicals KEI --pretty
uv run --project ~/.claude/market-sage-tools ms-portfolio kite_holdings.csv --pretty
uv run --project ~/.claude/market-sage-tools ms-nav "Quant Small Cap" --pretty
uv run --project ~/.claude/market-sage-tools ms-dcf --symbol CDSL --price 1212 --fcf 560 --growth 20 --shares 1.05 --pretty
```

### US Market Tools

```bash
uv run --project ~/.claude/market-sage-tools ms-us-quotes AAPL MSFT NVDA --pretty
uv run --project ~/.claude/market-sage-tools ms-us-technicals NVDA --period 1y --pretty
uv run --project ~/.claude/market-sage-tools ms-us-etf SPY QQQ VTI BND --pretty
uv run --project ~/.claude/market-sage-tools ms-dcf --symbol AAPL --price 195 --fcf 100 --growth 8 --shares 15.4 --discount 10 --terminal 2.5 --pretty
```

## Skill Modules

| File | Market | Contents |
|------|--------|---------|
| `market-sage.md` | Both | Core — data integrity rules, market scope routing, sources, session protocol |
| `stock-analyzer.md` | India | Fundamentals, technicals, IPO, governance, moat — Indian equities |
| `mutual-fund-advisor.md` | India | Fund selection, SIP, ETFs, NAV, SEBI/AMFI categories |
| `portfolio-builder.md` | India | Asset allocation, rebalancing, tax efficiency, income planning |
| `policy-impact-analyzer.md` | India | Budget, RBI, PLI, SEBI, macro impact on sectors |
| `us-stock-analyzer.md` | US | Deep US equity analysis — SEC governance, SaaS/REIT/biopharma frameworks, WACC, DCF |
| `us-fund-advisor.md` | US | US ETF/MF analysis, 3-fund portfolio, 401k/IRA asset location, expense ratio benchmarks |

## Market Routing

The skill auto-detects which market is relevant from your query:

- **US indicators**: NYSE/NASDAQ tickers (AAPL, MSFT, NVDA…), SPY/QQQ/VTI, Vanguard/BlackRock/Fidelity/SPDR/Schwab, 401(k)/IRA/Roth IRA, "US stock/ETF/fund"
- **Indian indicators**: NSE/BSE symbols, SIP/ELSS/NPS, SEBI/RBI/AMFI, Indian fund houses (HDFC MF, Axis MF, Nippon India…)

US queries load `us-stock-analyzer.md` or `us-fund-advisor.md`. Indian queries load the Indian companion files. The skill never mixes US-specific tools or benchmarks into Indian analysis.

## Updating Tools

If you pull new changes to this repo, re-sync the installed tools:

```bash
cp -r tools/. ~/.claude/market-sage-tools/
uv sync --project ~/.claude/market-sage-tools
```

---

> **Disclaimer:** Educational tool only. Not financial advice. Consult a SEBI-registered investment advisor (India) or SEC-registered RIA (US) before investing.
