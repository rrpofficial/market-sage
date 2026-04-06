#!/bin/bash
# Market Sage — Indian Stock Market Analyzer
# Claude Code Skill Installer
#
# Usage: ./install.sh [--global | --project /path/to/project]
# Default: installs globally to ~/.claude/skills/

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

SKILL_FILES=(
    "market-sage.md"
    "stock-analyzer.md"
    "mutual-fund-advisor.md"
    "policy-impact-analyzer.md"
    "portfolio-builder.md"
)

# Parse arguments
INSTALL_DIR="$HOME/.claude/skills"
if [ "$1" = "--project" ] && [ -n "$2" ]; then
    INSTALL_DIR="$2/.claude/skills"
elif [ "$1" = "--global" ]; then
    INSTALL_DIR="$HOME/.claude/skills"
elif [ -n "$1" ]; then
    echo "Usage: ./install.sh [--global | --project /path/to/project]"
    echo ""
    echo "  --global              Install to ~/.claude/skills/ (default)"
    echo "  --project <path>      Install to <path>/.claude/skills/"
    exit 1
fi

echo "Market Sage — Indian Stock Market Analyzer"
echo "==========================================="
echo ""
echo "Installing to: $INSTALL_DIR"
echo ""

# Create directory
mkdir -p "$INSTALL_DIR"

# Verify source files exist
MISSING=0
for file in "${SKILL_FILES[@]}"; do
    if [ ! -f "$SCRIPT_DIR/$file" ]; then
        echo "ERROR: Missing file: $file"
        MISSING=1
    fi
done

if [ "$MISSING" -eq 1 ]; then
    echo "Some skill files are missing. Ensure all files are in: $SCRIPT_DIR"
    exit 1
fi

# Copy files
for file in "${SKILL_FILES[@]}"; do
    cp "$SCRIPT_DIR/$file" "$INSTALL_DIR/$file"
    echo "  Installed: $file"
done

echo ""
echo "Installation complete."
echo ""
echo "To use, start Claude Code and try:"
echo '  "Analyze Reliance Industries stock"'
echo '  "Build a portfolio for 10 lakhs with moderate risk"'
echo '  "Compare HDFC Bank vs ICICI Bank"'
echo '  "How will the budget affect IT stocks?"'
echo '  "Best mutual funds for 10-year SIP"'
echo ""
echo "DISCLAIMER: This is an educational tool, NOT financial advice."
echo "Consult a SEBI-registered advisor before investing."
