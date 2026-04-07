#!/bin/bash
# Market Sage — Indian Stock Market Analyzer
# Claude Code Skill Installer
#
# Usage:
#   ./install.sh                        — interactive, choose modules
#   ./install.sh --all                  — install all modules
#   ./install.sh --minimal              — install only core + stock analyzer (~1050 lines)
#   ./install.sh --modules "stock mf"  — install specific modules by name
#   ./install.sh --project /path        — install to a project instead of globally
#
# Module names: stock, mf (mutual funds), policy, portfolio
#
# Context footprint by combination:
#   core only                      ~300 lines
#   core + stock + policy          ~1380 lines (recommended for stock analysts — policy is essential for long-term analysis)
#   core + mf + portfolio          ~1100 lines (recommended for fund/portfolio investors)
#   core + mf + portfolio + policy ~1370 lines (fund investors who want budget/RBI context)
#   all modules                    ~2400 lines (full install — highest capability)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# File map
CORE_FILE="market-sage.md"
declare -A MODULE_FILES=(
  [stock]="stock-analyzer.md"
  [mf]="mutual-fund-advisor.md"
  [policy]="policy-impact-analyzer.md"
  [portfolio]="portfolio-builder.md"
)
declare -A MODULE_LABELS=(
  [stock]="Stock Analyzer     (fundamentals, technical, IPO, governance) — 743 lines"
  [mf]="Mutual Fund Advisor (funds, ETFs, SIP, international)          — 478 lines"
  [policy]="Policy Analyzer    (budget, RBI, PLI, macro impact)           — 268 lines"
  [portfolio]="Portfolio Builder  (asset allocation, review, tax, income)    — 521 lines"
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
echo "Market Sage — Indian Stock Market Analyzer"
echo "==========================================="
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
  for key in stock mf policy portfolio; do
    echo "  [$key] ${MODULE_LABELS[$key]}"
  done
  echo ""
  echo "Presets:"
  echo "  [1] Stock analyst      — core + stock + policy (~1380 lines)"
  echo "      (Policy is essential: budget capex, PLI schemes, sector regulation and RBI"
  echo "       rate direction all directly affect long-term stock fundamentals)"
  echo ""
  echo "  [2] Fund investor      — core + mf + portfolio + policy (~1370 lines)"
  echo "      (Policy context needed for sector rotation and rate impact on fund categories)"
  echo ""
  echo "  [3] Full install       — all modules (~2400 lines)"
  echo "      (For users who analyse stocks, funds, AND build portfolios)"
  echo ""
  echo "  [4] Custom             — pick specific modules"
  echo ""
  read -rp "Enter preset [1-4] or press Enter for full install: " choice

  case "$choice" in
    1)
      SELECTED_MODULES=(stock policy) ;;
    2)
      SELECTED_MODULES=(mf portfolio policy) ;;
    3|"")
      INSTALL_MODE="all" ;;
    4)
      echo ""
      echo "Enter module names separated by spaces (stock mf policy portfolio):"
      echo "NOTE: policy is strongly recommended alongside stock for long-term analysis."
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
  for key in stock mf policy portfolio; do
    FILES_TO_INSTALL+=("${MODULE_FILES[$key]}")
  done
  TOTAL_LINES=2300
elif [ "$INSTALL_MODE" = "minimal" ]; then
  # core + stock + policy: policy is required for proper long-term stock analysis
  FILES_TO_INSTALL+=("${MODULE_FILES[stock]}" "${MODULE_FILES[policy]}")
  TOTAL_LINES=1380
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

# Create directory and copy files
mkdir -p "$INSTALL_DIR"
for file in "${FILES_TO_INSTALL[@]}"; do
  cp "$SCRIPT_DIR/$file" "$INSTALL_DIR/$file"
  echo "  Installed: $file"
done

echo ""
echo "Done. ${#FILES_TO_INSTALL[@]} file(s) installed to: $INSTALL_DIR"
echo ""
echo "To add more modules later, re-run this script and choose additional modules."
echo "To remove a module, delete its .md file from: $INSTALL_DIR"
echo ""
echo "Example queries to try:"
echo '  "Analyze Reliance Industries stock"'
echo '  "Quick analysis of TCS"'
echo '  "Build a portfolio for ₹10 lakhs with moderate risk"'
echo '  "Compare HDFC Bank vs ICICI Bank"'
echo '  "Best mutual funds for 10-year SIP"'
echo '  "How will the defence budget affect HAL and BEL?"'
echo ""
echo "DISCLAIMER: Educational tool only. NOT financial advice."
echo "Consult a SEBI-registered advisor before investing."
