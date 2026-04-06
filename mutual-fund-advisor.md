---
name: mutual-fund-advisor
description: |
  Analyzes and recommends Indian mutual funds. Evaluates performance, risk metrics,
  portfolio quality, costs, and fund manager track record. Provides SIP planning,
  fund comparison, and goal-based fund selection.
triggers:
  - mutual fund recommendation
  - SIP plan
  - fund comparison
  - ELSS tax saving
  - index fund
  - debt fund
  - best mutual fund
  - fund portfolio
---

# Mutual Fund Advisor — Fund Analysis & Selection

## Activation

When the user asks about mutual fund selection, comparison, SIP planning, or fund analysis.

## Step 1: Fetch Data

1. **WebSearch**: `"{Fund Name} value research online"` — for ratings, returns, risk metrics
2. **WebSearch**: `"{Fund Name} moneycontrol mutual fund"` — for portfolio, AUM, expense ratio
3. **WebSearch**: `"best {category} mutual funds India {current year}"` — for category screening
4. **WebSearch**: `"{Fund Name} factsheet PDF"` — for latest portfolio and attribution
5. **WebFetch**: Value Research or Moneycontrol fund page for structured data

**Critical**: Always use **Direct Plan** data (not Regular). Direct plans have lower expense ratios and higher returns. If user holds Regular plans, flag the cost difference.

## Step 2: Understand User Context

Before recommending, clarify:
- **Goal**: What is this money for? (Retirement, child education, house, wealth creation)
- **Horizon**: When do they need the money? (<3Y, 3-5Y, 5-10Y, 10Y+)
- **Risk tolerance**: Can they tolerate 30-40% drawdowns? (Conservative / Moderate / Aggressive)
- **Existing portfolio**: What do they already own? (Avoid overlap)
- **Tax situation**: Are they in 30% bracket? (Tax-saving relevance)
- **Investment mode**: SIP or Lumpsum?

If user hasn't provided this, **ask before recommending**.

## Step 3: Fund Category Selection

### By Investment Horizon

| Horizon | Equity Allocation | Recommended Categories |
|---------|-------------------|----------------------|
| <1 year | 0% | Liquid, Overnight, Ultra-short |
| 1-3 years | 0-20% | Short Duration, Corporate Bond, Conservative Hybrid |
| 3-5 years | 30-50% | Balanced Advantage, Aggressive Hybrid, Large Cap |
| 5-7 years | 50-70% | Large Cap, Flexi Cap, Large & Mid Cap |
| 7-10 years | 60-80% | Flexi Cap, Mid Cap, Large & Mid Cap |
| 10+ years | 70-100% | Mid Cap, Small Cap, Flexi Cap, Index (Nifty/Nifty Next 50) |

### Category Descriptions

**Equity Funds**:
- **Large Cap**: Top 100 by market cap. Lower risk, moderate returns. Core holding.
- **Mid Cap**: 101-250 by market cap. Higher growth, higher volatility.
- **Small Cap**: 251+ by market cap. Highest risk-reward. Only for 10Y+ horizon.
- **Flexi Cap**: Fund manager picks across market caps. Flexibility is the edge.
- **Large & Mid Cap**: Min 35% each in large and mid. Balanced growth.
- **Focused Fund**: Max 30 stocks. High conviction, concentrated risk.
- **Index Fund / ETF**: Passive, low cost. Nifty 50, Nifty Next 50, Nifty Midcap 150.
- **ELSS**: 3-year lock-in, tax deduction under 80C. Equity-oriented.
- **Sectoral/Thematic**: Avoid unless user has specific sector conviction.

**Debt Funds**:
- **Liquid**: <91 day papers. Emergency fund parking.
- **Ultra Short**: 3-6 month horizon. Better than savings account.
- **Short Duration**: 1-3 year horizon. Moderate credit risk.
- **Corporate Bond**: AA+ and above. 3-5 year horizon.
- **Gilt**: Government securities. Interest rate sensitive, zero credit risk.
- **Dynamic Bond**: Fund manager manages duration actively.

**Hybrid Funds**:
- **Conservative Hybrid**: 10-25% equity. For very conservative investors.
- **Balanced Advantage / Dynamic Asset Allocation**: Auto-adjusts equity/debt. Good for beginners.
- **Aggressive Hybrid**: 65-80% equity. Equity taxation benefit.

## Step 4: Fund Evaluation Framework

### 4.1 Performance Analysis

| Period | Fund Return | Category Avg | Benchmark | Alpha | Assessment |
|--------|-------------|--------------|-----------|-------|------------|
| 1 Year | | | | | |
| 3 Year (CAGR) | | | | | |
| 5 Year (CAGR) | | | | | |
| 7 Year (CAGR) | | | | | |
| 10 Year (CAGR) | | | | | |
| Since Inception | | | | | |

**Assessment criteria**:
- Consistently beats benchmark across periods = Strong
- Beats in 3Y/5Y but not 1Y = Acceptable (short-term underperformance normal)
- Underperforms benchmark across multiple periods = Avoid (consider index fund instead)

**Rolling returns** (more reliable than point-to-point):
- 3Y rolling return (min/max/avg over last 10 years)
- 5Y rolling return (min/max/avg)
- % of times beating benchmark in rolling windows

### 4.2 Risk Metrics

| Metric | Fund | Category Avg | Benchmark | Assessment |
|--------|------|--------------|-----------|------------|
| Std Deviation (3Y annualized) | | | | Lower = better |
| Sharpe Ratio (3Y) | | | | >1 Good, >1.5 Excellent |
| Sortino Ratio | | | | Higher = better |
| Max Drawdown | | | | Smaller = better |
| Beta | | | | <1 = less volatile |
| Alpha (Jensen's) | | | | >0 = value added |
| Information Ratio | | | | >0.5 = skilled manager |
| Capture Ratio (Up/Down) | | | | High up, Low down = ideal |

### 4.3 Portfolio Quality

| Aspect | Detail |
|--------|--------|
| Total holdings | (>40 = well diversified, <25 = concentrated) |
| Top 10 concentration (%) | (>50% = concentrated risk) |
| Top sector allocation | |
| Top 3 sectors (%) | (>60% = sector concentration) |
| Large/Mid/Small cap split | |
| Equity % (for hybrid) | |
| Portfolio P/E | |
| Portfolio P/B | |
| Average market cap | |
| Portfolio turnover (%) | (<50% = buy-and-hold, >100% = active churning) |
| Overlap with Nifty 50 (%) | (High overlap = expensive index fund) |

### 4.4 Cost Analysis

| Cost Component | Fund | Category Avg | Impact |
|----------------|------|--------------|--------|
| Expense Ratio (Direct) | | | |
| Expense Ratio (Regular) | | | |
| Cost difference (Direct vs Regular) | | | Over 20 years at 12% CAGR |
| Exit Load | | | |
| Exit Load Period | | | |

**Cost impact calculation**: Show the user how expense ratio compounds.
Example: ₹10,000/month SIP for 20 years at 12% gross:
- At 0.5% expense ratio: ₹___
- At 1.0% expense ratio: ₹___
- At 1.5% expense ratio: ₹___
- Difference: ₹___ (this is what higher cost eats)

### 4.5 Fund Manager Assessment

| Aspect | Detail |
|--------|--------|
| Fund Manager Name | |
| Tenure on this fund | (<2 years = unproven) |
| Other funds managed | |
| Track record across funds | |
| Investment style | Growth / Value / Blend |
| Style consistency | (Style drift = red flag) |

### 4.6 AMC (Fund House) Assessment

| Aspect | Detail |
|--------|--------|
| AMC Name | |
| Total AUM | |
| Reputation / Track Record | |
| Key strengths (categories) | |
| Any regulatory issues | |

## Step 5: Fund Comparison Template

When comparing 2-3 funds:

| Parameter | Fund A | Fund B | Fund C | Winner |
|-----------|--------|--------|--------|--------|
| 3Y CAGR | | | | |
| 5Y CAGR | | | | |
| Sharpe Ratio | | | | |
| Max Drawdown | | | | |
| Expense Ratio | | | | |
| AUM | | | | |
| Manager Tenure | | | | |
| Top 10 Conc. (%) | | | | |
| Benchmark Alpha | | | | |
| Consistency | | | | |
| **Verdict** | | | | |

## Step 6: SIP Planning

### SIP Calculator Output

For any SIP recommendation, show:

| Parameter | Value |
|-----------|-------|
| Monthly SIP | ₹___ |
| Duration | ___ years |
| Total Invested | ₹___ |
| Expected Corpus (at 10% CAGR) | ₹___ |
| Expected Corpus (at 12% CAGR) | ₹___ |
| Expected Corpus (at 14% CAGR) | ₹___ |

**SIP step-up**: If SIP increases by 10% annually:
| Year | Monthly SIP | Cumulative Invested | Projected Corpus |
|------|-------------|--------------------|-----------------:|

### SIP vs Lumpsum Decision

| Scenario | Recommendation | Why |
|----------|---------------|-----|
| Market P/E < 18 (cheap) | Lumpsum preferred | Buying at discount |
| Market P/E 18-22 (fair) | SIP preferred | Average out |
| Market P/E > 22 (expensive) | SIP strongly preferred | Avoid buying peak |
| Large amount (>₹5L in equity) | Split: 30% lump + 70% STP over 6-12 months | Risk management |
| Regular income, monthly surplus | SIP | Discipline, averaging |

## Step 7: Fund Red Flags (Auto-Check)

Check and warn for ANY of these:

- [ ] Consistent underperformance vs benchmark for 3+ years
- [ ] Expense ratio >1.5% (equity direct) or >0.75% (debt direct)
- [ ] Fund manager changed in last 12 months
- [ ] AUM <₹100 Cr (liquidity risk) or >₹30,000 Cr for mid/small cap (size drag)
- [ ] Portfolio turnover >150% (excessive churning)
- [ ] Style drift (large cap fund buying mid/small caps significantly)
- [ ] High overlap with another fund in portfolio (>50% common stocks)
- [ ] Exit load applies for the user's expected horizon
- [ ] AMC has had regulatory issues
- [ ] Concentrated bets: single stock >10% or single sector >35%

## Step 8: Recommendation Output

### For Single Fund Analysis

**Fund**: {Name}
**Category**: {Category}
**Verdict**: INVEST / AVOID / CONDITIONAL

**Strengths**:
1. ...
2. ...

**Concerns**:
1. ...
2. ...

**Suitable for**: [Investor type, horizon, risk level]
**Minimum SIP**: ₹___/month for ___ years
**Monitor**: [What to watch quarterly]

### For Portfolio Recommendation

Present a complete fund portfolio:

| Fund Name | Category | Allocation % | Monthly SIP | Role |
|-----------|----------|-------------|-------------|------|
| | | | ₹___ | Core |
| | | | ₹___ | Growth |
| | | | ₹___ | Stability |
| | | | ₹___ | Tactical |
| **Total** | | **100%** | **₹___** | |

**Portfolio characteristics**:
- Weighted expense ratio: ___%
- Expected equity allocation: ___%
- Number of underlying stocks (approx): ___
- Overlap analysis: Low / Medium / High
- Category diversification: Good / Needs improvement

## Index Fund vs Active Fund Decision

Present this framework when relevant:

| Factor | Index Fund | Active Fund |
|--------|-----------|-------------|
| Cost | 0.1-0.3% | 0.5-1.5% |
| Manager risk | None | Present |
| Alpha generation | Zero (tracks index) | Positive or negative |
| Suitable when | No strong view, want simplicity | Clear alpha evidence |
| Indian context | Large cap: Index often wins | Mid/Small: Active can add value |

**Default recommendation**: For large cap allocation, prefer Nifty 50 / Nifty Next 50 index funds unless an active fund has demonstrated consistent alpha over 7+ years.
