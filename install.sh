#!/bin/bash
# Market Sage — Indian & US Stock Market Analyzer
# Claude Code Skill Installer
#
# Usage:
#   ./install.sh                        — interactive, choose modules
#   ./install.sh --all                  — install all modules
#   ./install.sh --minimal              — install only core + stock analyzer (~1050 lines)
#   ./install.sh --modules "stock mf"  — install specific modules by name
#   ./install.sh --project /path        — install to a project instead of globally
#
# Module names: stock, mf (mutual funds), policy, portfolio, us-stock, us-fund
#
# Context footprint by combination:
#   core only                               ~400 lines
#   core + stock + policy                   ~1500 lines (Indian stock analysts)
#   core + mf + portfolio                   ~1200 lines (Indian fund/portfolio investors)
#   core + mf + portfolio + policy          ~1500 lines (Indian fund investors with policy context)
#   core + us-stock                         ~1000 lines (US stock analysts)
#   core + us-fund                          ~700 lines (US ETF/fund investors)
#   core + us-stock + us-fund               ~1300 lines (full US coverage)
#   all modules                             ~3600 lines (full install — all markets)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# File map
CORE_FILE="market-sage.md"
declare -A MODULE_FILES=(
  [stock]="stock-analyzer.md"
  [mf]="mutual-fund-advisor.md"
  [policy]="policy-impact-analyzer.md"
  [portfolio]="portfolio-builder.md"
  [us-stock]="us-stock-analyzer.md"
  [us-fund]="us-fund-advisor.md"
)
declare -A MODULE_LABELS=(
  [stock]="Stock Analyzer (IN)   (Indian: fundamentals, technical, IPO, governance) — ~750 lines"
  [mf]="Fund Advisor (IN)      (Indian: funds, ETFs, SIP, international)           — ~500 lines"
  [policy]="Policy Analyzer (IN) (Indian: budget, RBI, PLI, macro impact)            — ~270 lines"
  [portfolio]="Portfolio Builder (IN)(Indian: asset allocation, review, tax, income)   — ~520 lines"
  [us-stock]="US Stock Analyzer    (US: NYSE/NASDAQ stocks, SEC, sector frameworks)   — ~600 lines"
  [us-fund]="US Fund Advisor      (US: ETFs, MFs, 401k/IRA, 3-fund strategy)          — ~500 lines"
)

# Parse arguments
INSTALL_DIR="$HOME/.claude/skills"
INSTALL_MODE="interactive"
SELECTED_MODULES=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --all)
      INSTALL_MODE="all"
      shift ;;
    --minimal)
      INSTALL_MODE="minimal"  # core + stock + policy
      shift ;;
    --modules)
      INSTALL_MODE="manual"
      IFS=' ' read -ra SELECTED_MODULES <<< "$2"
      shift 2 ;;
    --project)
      INSTALL_DIR="$2/.claude/skills"
      shift 2 ;;
    --global)
      INSTALL_DIR="$HOME/.claude/skills"
      shift ;;
    --help|-h)
      sed -n '2,20p' "$0" | sed 's/^# \?//'
      exit 0 ;;
    *)
      echo "Unknown option: $1. Run with --help for usage."
      exit 1 ;;
  esac
done

echo ""
echo "Market Sage — Indian & US Stock Market Analyzer"
echo "================================================"
echo ""

# Verify core file exists
if [ ! -f "$SCRIPT_DIR/$CORE_FILE" ]; then
  echo "ERROR: Core file '$CORE_FILE' not found in $SCRIPT_DIR"
  exit 1
fi

# Interactive mode — let user choose modules
if [ "$INSTALL_MODE" = "interactive" ]; then
  echo "Choose modules to install. More modules = richer analysis but more context consumed."
  echo "Each module adds lines to Claude's context window for EVERY conversation."
  echo ""
  echo "Available modules:"
  echo ""
  for key in stock mf policy portfolio us-stock us-fund; do
    echo "  [$key] ${MODULE_LABELS[$key]}"
  done
  echo ""
  echo "Presets:"
  echo "  [1] Indian stock analyst — core + stock + policy (~1500 lines)"
  echo "      (Policy is essential: budget capex, PLI schemes, RBI rate direction)"
  echo ""
  echo "  [2] Indian fund investor — core + mf + portfolio + policy (~1500 lines)"
  echo "      (Policy context needed for sector rotation and fund category impact)"
  echo ""
  echo "  [3] US investor          — core + us-stock + us-fund (~1300 lines)"
  echo "      (Full US market coverage: stocks, ETFs, MFs, 401k/IRA)"
  echo ""
  echo "  [4] Full install (both markets) — all modules (~3600 lines)"
  echo "      (For users who analyse Indian AND US stocks, funds, and portfolios)"
  echo ""
  echo "  [5] Custom               — pick specific modules"
  echo ""
  read -rp "Enter preset [1-5] or press Enter for full install: " choice

  case "$choice" in
    1)
      SELECTED_MODULES=(stock policy) ;;
    2)
      SELECTED_MODULES=(mf portfolio policy) ;;
    3)
      SELECTED_MODULES=(us-stock us-fund) ;;
    4|"")
      INSTALL_MODE="all" ;;
    5)
      echo ""
      echo "Enter module names separated by spaces (stock mf policy portfolio us-stock us-fund):"
      echo "NOTE: For Indian stocks, policy is strongly recommended. For US, us-fund adds ETF/401k context."
      read -rp "> " custom_input
      IFS=' ' read -ra SELECTED_MODULES <<< "$custom_input"
      INSTALL_MODE="manual" ;;
    *)
      echo "Invalid choice. Defaulting to full install."
      INSTALL_MODE="all" ;;
  esac
fi

# Build final list of files to install
FILES_TO_INSTALL=("$CORE_FILE")
TOTAL_LINES=299  # core file lines

if [ "$INSTALL_MODE" = "all" ]; then
  for key in stock mf policy portfolio us-stock us-fund; do
    FILES_TO_INSTALL+=("${MODULE_FILES[$key]}")
  done
  TOTAL_LINES=3600
elif [ "$INSTALL_MODE" = "minimal" ]; then
  # core + stock + policy: policy is required for proper long-term stock analysis
  FILES_TO_INSTALL+=("${MODULE_FILES[stock]}" "${MODULE_FILES[policy]}")
  TOTAL_LINES=1500
else
  # Manual or interactive with custom selection
  for mod in "${SELECTED_MODULES[@]}"; do
    if [ -n "${MODULE_FILES[$mod]+_}" ]; then
      FILES_TO_INSTALL+=("${MODULE_FILES[$mod]}")
    else
      echo "WARNING: Unknown module '$mod' — skipping."
    fi
  done
fi

# Verify all selected files exist
echo ""
echo "Files to install:"
MISSING=0
for file in "${FILES_TO_INSTALL[@]}"; do
  if [ ! -f "$SCRIPT_DIR/$file" ]; then
    echo "  ERROR: $file — NOT FOUND"
    MISSING=1
  else
    size=$(wc -l < "$SCRIPT_DIR/$file")
    echo "  $file ($size lines)"
  fi
done

if [ "$MISSING" -eq 1 ]; then
  echo ""
  echo "Some files are missing from: $SCRIPT_DIR"
  echo "Ensure all Market Sage files are present."
  exit 1
fi

echo ""
echo "Install location: $INSTALL_DIR"
echo ""
read -rp "Proceed? [Y/n]: " confirm
if [[ "$confirm" =~ ^[Nn] ]]; then
  echo "Installation cancelled."
  exit 0
fi

# Create directory and copy skill content files
mkdir -p "$INSTALL_DIR"
for file in "${FILES_TO_INSTALL[@]}"; do
  cp "$SCRIPT_DIR/$file" "$INSTALL_DIR/$file"
  echo "  Installed: $file"
done

# Create the slash command registration file in ~/.claude/commands/
# Skills in ~/.claude/skills/ are NOT auto-loaded by Claude Code — only files in
# ~/.claude/commands/ with user-invocable: true are registered as slash commands.
COMMANDS_DIR="${INSTALL_DIR%/skills}/commands"
mkdir -p "$COMMANDS_DIR"
cat > "$COMMANDS_DIR/market-sage.md" << 'CMDEOF'
---
name: market-sage
description: >
  Comprehensive stock market analyzer covering Indian and US markets. For Indian
  markets: fundamental, technical, and valuation analysis of NSE/BSE equities,
  mutual funds, SIP planning, SEBI/RBI policy impact, IPO analysis, and portfolio
  construction. For US markets: deep analysis of NYSE/NASDAQ stocks, US ETFs,
  US mutual funds (Vanguard/Fidelity/BlackRock/SPDR), 401k/IRA fund selection,
  and sector-specific US equity frameworks. Strict live-data-only mandate — never
  uses training knowledge for any financial figure. All numbers fetched live and
  cited with date and source.
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

**Always read (required):**
- `~/.claude/skills/market-sage.md` — DATA INTEGRITY MANDATE, market scope detection, core principles, data sources

**For Indian market queries:**
- Indian stock / IPO / technical / governance → `~/.claude/skills/stock-analyzer.md`
- Indian mutual fund / SIP / ETF / NAV → `~/.claude/skills/mutual-fund-advisor.md`
- Indian portfolio construction / review / rebalancing → `~/.claude/skills/portfolio-builder.md`
- Indian budget / RBI / PLI / SEBI / macro impact → `~/.claude/skills/policy-impact-analyzer.md`

**For US market queries:**
- US stock / equity / IPO / governance / sector analysis → `~/.claude/skills/us-stock-analyzer.md`
- US ETF / US mutual fund / 401k / IRA / Roth / fund comparison → `~/.claude/skills/us-fund-advisor.md`

If the query spans multiple types, read all relevant companion files before proceeding.

---

## Step 3 — Follow All Instructions From the Loaded Files

### ⛔ DATA INTEGRITY MANDATE — NON-NEGOTIABLE

You are **strictly forbidden** from using LLM training knowledge for any quantitative financial figure, including:

- Stock prices (any market), 52-week high/low
- P/E, P/B, EV/EBITDA, Forward P/E, or any valuation multiple
- Revenue, net profit, EBITDA, EPS, free cash flow, operating margin
- ROE, ROCE, ROIC, debt/equity, current ratio, interest coverage
- Market cap, enterprise value
- Promoter / FII / DII / MF shareholding % or insider / institutional %
- Dividend yield, dividend amounts, payout ratios
- NAV, fund returns (1Y/3Y/5Y CAGR), Sharpe ratio, max drawdown, AUM, expense ratio
- Any analyst price target, consensus rating, or broker estimate

**For every number you write:**
1. Run WebSearch to locate the live source
2. Run WebFetch OR the appropriate CLI tool to extract the current figure
3. Cite the source URL and fetch date inline

**If a fetch fails:** write `[FETCH REQUIRED — verify at {URL}]` and continue. Never estimate or recall from training.

---

## Live Data Sources

### Indian Market
| Source | URL Pattern | Use For |
|--------|-------------|---------|
| Screener.in | `screener.in/company/{SYMBOL}/consolidated/` | Financials, ratios, 10Y history, shareholding |
| NSE India | `nseindia.com/get-quotes/equity?symbol={SYMBOL}` | Live price, corporate actions, filings |
| Value Research | `valueresearchonline.com/funds/` | MF ratings, returns, portfolio |
| AMFI | `amfiindia.com` | Official NAV data |
| SCORES 2.0 | `scores.sebi.gov.in` | SEBI investor complaints |

### US Market
| Source | URL Pattern | Use For |
|--------|-------------|---------|
| Yahoo Finance | `finance.yahoo.com/quote/{TICKER}` | Price, fundamentals, analyst data |
| Macrotrends | `macrotrends.net/stocks/charts/{TICKER}` | 10-20 year financial history |
| SEC EDGAR | `sec.gov/cgi-bin/browse-edgar?CIK={TICKER}` | 10-K, 10-Q, DEF 14A proxy, Form 4 |
| ETF.com | `etf.com/{TICKER}` | ETF tracking error, bid-ask, liquidity |
| FRED | `fred.stlouisfed.org` | US macro: rates, CPI, GDP |

---

## Python CLI Tools

Tools are installed at \`~/.claude/market-sage-tools/.venv\`.
Invoke via \`uv run --project ~/.claude/market-sage-tools <tool> [args]\`.

### Indian Market Tools
| Tool | Invocation | What it does |
|------|-----------|--------------|
| ms-quotes | \`ms-quotes SYMBOL [SYMBOL ...] [--pretty]\` | LTP (₹), 52W H/L, MCap (₹Cr), PE/PB via yfinance (.NS) |
| ms-screener | \`ms-screener SYMBOL [--standalone] [--pretty]\` | Screener.in: P/E, ROE, ROCE, revenue, PAT, shareholding, peers |
| ms-portfolio | \`ms-portfolio FILE.csv [--pretty]\` | Zerodha Kite CSV → weights, sectors, flags, entry zones |
| ms-technicals | \`ms-technicals SYMBOL [--period 1y] [--pretty]\` | DMA 20/50/200, RSI, MACD, Bollinger, S/R, verdict |
| ms-dcf | \`ms-dcf --symbol X --price P --fcf F --growth G [--shares S] [--eps E] [--book B] [--pe-fair PE] [--pretty]\` | DCF, Graham Number, PE-based, Reverse DCF (India defaults: --discount 13 --terminal 5) |
| ms-nav | \`ms-nav QUERY [--scheme-code CODE] [--list-matches] [--pretty]\` | AMFI NAV lookup by fund name or scheme code |

### US Market Tools
| Tool | Invocation | What it does |
|------|-----------|--------------|
| ms-us-quotes | \`ms-us-quotes TICKER [TICKER ...] [--pretty]\` | Price ($), 52W H/L, MCap ($B), P/E, Fwd P/E, EV/EBITDA, margins, ROE, analyst target, insider %, short ratio |
| ms-us-technicals | \`ms-us-technicals TICKER [--period 1y] [--pretty]\` | DMA 20/50/200, RSI, MACD, Bollinger, S/R, verdict (no .NS suffix) |
| ms-us-etf | \`ms-us-etf TICKER [TICKER ...] [--pretty]\` | AUM ($B), expense ratio, NAV, YTD/1Y/3Y/5Y returns, category, fund family, quality checklist |
| ms-dcf (US) | \`ms-dcf --symbol TICKER --price P --fcf F --growth G [--shares S] --discount 10 --terminal 2.5 [--pretty]\` | Same DCF engine; use --discount 10 --terminal 2.5 for US companies |

**Invocation shorthand** (after installing, the venv prefix is needed):
\`uv run --project ~/.claude/market-sage-tools ms-us-quotes AAPL MSFT --pretty\`

**When to use each (US)**:
- Start every US stock analysis with \`ms-us-quotes\` — gets price, fundamentals, analyst data, insider/short in one call
- Use \`ms-us-technicals\` for US entry/exit timing
- Use \`ms-us-etf\` for any US ETF or mutual fund analysis
- Use \`ms-dcf --discount 10 --terminal 2.5\` for US valuation
- For SEC filings (10-K, proxy, Form 4): use WebSearch + WebFetch on EDGAR directly
CMDEOF
echo "  Registered: $COMMANDS_DIR/market-sage.md (slash command)"

# Install Python CLI tools into a project-local venv at ~/.claude/market-sage-tools/
TOOLS_SRC="$SCRIPT_DIR/tools"
TOOLS_DEST="$HOME/.claude/market-sage-tools"
if [ -d "$TOOLS_SRC" ] && [ -f "$TOOLS_SRC/pyproject.toml" ]; then
  echo ""
  echo "Installing Python CLI tools (project-local venv, not global)..."
  if command -v uv &>/dev/null; then
    mkdir -p "$TOOLS_DEST"
    cp -r "$TOOLS_SRC/." "$TOOLS_DEST/"
    uv sync --project "$TOOLS_DEST" 2>&1 | tail -3
    echo "  Installed: ~/.claude/market-sage-tools/.venv"
    echo "    Indian tools: ms-quotes, ms-screener, ms-portfolio, ms-dcf, ms-technicals, ms-nav"
    echo "    US tools:     ms-us-quotes, ms-us-technicals, ms-us-etf"
  else
    echo "  WARNING: uv not found. Install uv first: curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "  Then run: mkdir -p ~/.claude/market-sage-tools && cp -r $TOOLS_SRC/. ~/.claude/market-sage-tools/ && uv sync --project ~/.claude/market-sage-tools"
  fi
fi

echo ""
echo "Done. ${#FILES_TO_INSTALL[@]} file(s) installed to: $INSTALL_DIR"
echo ""
echo "To add more modules later, re-run this script and choose additional modules."
echo "To remove a module, delete its .md file from: $INSTALL_DIR"
echo ""
echo "Example queries to try:"
echo ""
echo "  Indian markets:"
echo '  "Analyze Reliance Industries stock"'
echo '  "Quick analysis of TCS"'
echo '  "Build a portfolio for ₹10 lakhs with moderate risk"'
echo '  "Compare HDFC Bank vs ICICI Bank"'
echo '  "Best mutual funds for 10-year SIP"'
echo '  "How will the defence budget affect HAL and BEL?"'
echo ""
echo "  US markets:"
echo '  "Analyze Apple stock (AAPL)"'
echo '  "Compare SPY vs QQQ vs VTI ETF"'
echo '  "Best funds for my Roth IRA"'
echo '  "Quick analysis of NVIDIA"'
echo '  "Build a 3-fund US portfolio for retirement"'
echo '  "Is Microsoft fairly valued right now?"'
echo ""
echo "DISCLAIMER: Educational tool only. NOT financial advice."
echo "Consult a SEBI-registered advisor before investing."
