---
name: portfolio-builder
description: |
  Builds customized investment portfolios for Indian investors based on risk profile,
  goals, time horizon, and capital. Provides asset allocation, security selection,
  SIP planning, rebalancing strategy, and tax-efficient structuring.
triggers:
  - build portfolio
  - asset allocation
  - investment plan
  - portfolio review
  - rebalance portfolio
  - how to invest amount
  - retirement planning
  - goal based investing
---

# Portfolio Builder — Investment Portfolio Construction

## Activation

When the user wants to build a new portfolio, review an existing one, plan asset allocation, or get a structured investment plan.

## Step 1: Risk Profiling

**Before building ANY portfolio, gather this information.** If the user hasn't provided it, ask:

### Required Inputs

| Parameter | User's Answer | Why It Matters |
|-----------|--------------|----------------|
| **Age** | | Determines equity capacity |
| **Annual Income** | | Determines investment capacity |
| **Monthly investable surplus** | | SIP sizing |
| **Lumpsum available** | | Deployment strategy |
| **Investment goal** | | Category selection |
| **Time horizon** | | Risk capacity |
| **Existing investments** | | Avoid duplication |
| **Existing loans/EMIs** | | Debt capacity check |
| **Emergency fund status** | | Prerequisite check |
| **Insurance status** | | Prerequisite check |
| **Tax bracket** | | Tax-efficient structuring |
| **Risk tolerance** | (Can you handle 30-40% drawdown?) | Equity allocation |

### Risk Profile Classification

| Profile | Characteristics | Max Equity | Suitable For |
|---------|----------------|------------|-------------|
| **Ultra Conservative** | Cannot tolerate any loss, needs capital safety | 20% | Retirees, very short horizon |
| **Conservative** | Tolerates small fluctuations, prioritizes safety | 40% | Near-retirement, short goals |
| **Moderate** | Accepts volatility for better returns, 5Y+ horizon | 65% | Mid-career, balanced goals |
| **Aggressive** | Comfortable with large drawdowns, 10Y+ horizon | 85% | Young earners, wealth creation |
| **Very Aggressive** | Seeks maximum growth, can ignore 50% drawdowns | 95% | Young, high income, no near-term goals |

### Prerequisites Check

Before investing, verify the user has:

- [ ] **Emergency Fund**: 6-12 months of expenses in liquid fund/savings (if NO → build this first)
- [ ] **Health Insurance**: ₹10-25L family floater (if NO → get this before investing)
- [ ] **Term Life Insurance**: 10-15x annual income (if NO → get this before investing)
- [ ] **No high-interest debt**: Credit card, personal loan (if YES → pay these off first)
- [ ] **KYC complete**: PAN-Aadhaar linked

**If prerequisites are not met, address them BEFORE portfolio construction.** This is non-negotiable.

## Step 2: Asset Allocation

### 2.1 Strategic Asset Allocation

Determine the target allocation using multiple frameworks and converge:

**Framework 1: Age-Based**
```
Equity % = min(100 - Age, Risk-adjusted max)
Debt % = remaining - Gold allocation
Gold % = 5-10%
```

**Framework 2: Goal-Based**

| Goal Type | Horizon | Equity | Debt | Gold |
|-----------|---------|--------|------|------|
| Emergency Fund | Always available | 0% | 100% | 0% |
| Short-term (<3Y) | House DP, marriage, car | 0-20% | 80-100% | 0% |
| Medium-term (3-7Y) | Child school, second home | 40-60% | 30-50% | 10% |
| Long-term (7-15Y) | Child higher education | 60-80% | 15-30% | 5-10% |
| Retirement (15Y+) | Retirement corpus | 70-90% | 5-20% | 5-10% |
| Wealth creation (10Y+) | General wealth | 75-95% | 0-15% | 5-10% |

**Framework 3: Risk-Based**
Use the risk profile from Step 1 to cap equity allocation.

**Final Allocation**: Take the MOST CONSERVATIVE of the three frameworks.
- If age says 70% equity but risk says max 40% → use 40%
- If goal says 60% equity but age says 50% → use 50%

Present:

| Asset Class | Allocation % | Amount (₹) | Purpose |
|-------------|-------------|------------|---------|
| **Equity** | ___% | ₹___ | Growth |
| - Large Cap / Index | ___% | ₹___ | Stability + market returns |
| - Mid Cap | ___% | ₹___ | Growth acceleration |
| - Small Cap | ___% | ₹___ | High growth (optional) |
| - International | ___% | ₹___ | Diversification (optional) |
| **Debt** | ___% | ₹___ | Stability |
| - Liquid/Ultra Short | ___% | ₹___ | Emergency + parking |
| - Short/Corporate Bond | ___% | ₹___ | Core debt |
| - Gilt / SDL | ___% | ₹___ | Safety (optional) |
| **Gold** | ___% | ₹___ | Hedge |
| - SGB / Gold ETF | ___% | ₹___ | |
| **Total** | **100%** | **₹___** | |

### 2.2 Multiple Goals Portfolio

If user has multiple goals, create separate sub-portfolios:

| Goal | Amount Needed | Timeline | Equity % | Debt % | Monthly SIP |
|------|--------------|----------|----------|--------|-------------|
| Emergency Fund | ₹___ | Immediate | 0% | 100% | ₹___ |
| {Goal 1} | ₹___ | ___ years | ___% | ___% | ₹___ |
| {Goal 2} | ₹___ | ___ years | ___% | ___% | ₹___ |
| Retirement | ₹___ | ___ years | ___% | ___% | ₹___ |
| **Total** | | | | | **₹___** |

## Step 3: Security Selection

### 3.1 Mutual Fund Portfolio (Recommended for most investors)

**For each fund, fetch current data** from Value Research / Moneycontrol before recommending.

**Core-Satellite Approach**:

| Role | Allocation | Fund Type | Selection Criteria |
|------|-----------|-----------|-------------------|
| **Core** (60-70%) | Bulk of equity | Index Fund (Nifty 50, Nifty Next 50) or proven large cap | Low cost, market returns |
| **Growth** (20-30%) | Additional alpha | Flexi Cap or Mid Cap | Consistent alpha, good manager |
| **Tactical** (0-10%) | Optional | Small cap, sectoral, international | Only for aggressive, 10Y+ |

**Fund Selection Rules**:
1. **Maximum 5-7 funds total** (3 equity + 1-2 debt + 1 gold). More = overlap, not diversification.
2. **No two funds from same category** (don't hold 3 large cap funds)
3. **Check overlap**: If two funds share >40% holdings, keep only one
4. **Prefer Direct plans always**
5. **Prefer Index funds for large cap** unless active fund has proven 7Y+ alpha
6. **Different AMCs**: Spread across 2-3 fund houses for AMC risk diversification

**Portfolio Template**:

| # | Fund Name | Category | Expense Ratio | 5Y CAGR | Monthly SIP | Role |
|---|-----------|----------|---------------|---------|-------------|------|
| 1 | | Nifty 50 Index | | | ₹___ | Core |
| 2 | | Flexi/Mid Cap | | | ₹___ | Growth |
| 3 | | ELSS (if tax needed) | | | ₹___ | Tax + Growth |
| 4 | | Short Duration Debt | | | ₹___ | Stability |
| 5 | | SGB / Gold ETF | | | ₹___ | Hedge |
| | **Total** | | | | **₹___** | |

### 3.2 Direct Equity Portfolio (For intermediate+ investors only)

**Only recommend direct stocks if**:
- User has 7Y+ horizon
- Investable amount in equity >₹5L
- User understands and accepts stock-specific risk
- User will monitor quarterly results

**Stock Selection Framework**:

| Criteria | Minimum Threshold |
|----------|------------------|
| Market Cap | >₹10,000 Cr (avoid micro-caps) |
| ROE (3Y average) | >15% |
| Debt/Equity | <1 (exceptions: banking, NBFC) |
| Profit Growth (5Y CAGR) | >10% |
| Promoter Holding | >40%, no pledge concern |
| Free Cash Flow | Positive for 3+ years |
| Corporate Governance | No major red flags |

**Diversification Rules for Stock Portfolio**:
- Minimum 10, maximum 20 stocks
- No single stock >10% of equity portfolio
- No single sector >25% of equity portfolio
- Include at least 3 sectors
- Mix of large cap (50-60%), mid cap (30-40%), small cap (0-10%)

**Sample Stock Portfolio Structure** (₹10L equity):

| # | Company | Sector | Allocation | Amount | Rationale |
|---|---------|--------|-----------|--------|-----------|
| 1 | | Banking | 10% | ₹1L | |
| 2 | | IT | 10% | ₹1L | |
| ... | | | | | |
| 10-15 | | | | | |
| | **Total** | | **100%** | **₹10L** | |

## Step 4: Deployment Strategy

### 4.1 SIP Deployment (Regular income)

| Fund | SIP Amount | SIP Date | Auto-step-up (10%/year) |
|------|-----------|----------|------------------------|
| | ₹___ | 1st/5th/10th | Yes/No |
| | ₹___ | | |
| **Total** | **₹___** | | |

**SIP tips**:
- Stagger SIP dates across the month (not all on 1st)
- Set up auto-step-up of 10% annually (aligns with salary hikes)
- Don't stop SIPs in market falls — that's when you get more units

### 4.2 Lumpsum Deployment

**Never deploy large lumpsum (>₹2L) into equity all at once.**

| Strategy | When to Use | How |
|----------|-------------|-----|
| **STP (Systematic Transfer Plan)** | Lumpsum available, market fair/expensive | Park in liquid fund, transfer to equity fund over 6-12 months |
| **Staggered deployment** | Direct stock purchases | Buy in 3-4 tranches over 2-3 months |
| **Immediate deployment** | Market P/E < 18, clear value opportunity | Deploy 50% immediately, rest via STP |

**Lumpsum deployment plan** for ₹{amount}:

| Month | Transfer to Equity | Transfer to Debt | Remaining in Liquid |
|-------|-------------------|-----------------|-------------------|
| Month 1 | ₹___ (___%) | ₹___ | ₹___ |
| Month 2 | ₹___ | | ₹___ |
| ... | | | |
| Month 6-12 | ₹___ | | ₹0 |

## Step 5: Portfolio Review (For existing portfolios)

When user shares their existing portfolio, analyze:

### 5.1 Portfolio Health Check

| Check | Status | Action Needed |
|-------|--------|---------------|
| Asset allocation vs target | | Rebalance if >5% drift |
| Over-concentration (single stock/fund >15%) | | Trim and diversify |
| Too many funds (>8-10) | | Consolidate overlapping funds |
| Regular vs Direct plans | | Switch to Direct |
| Expense ratio (weighted avg) | | Should be <0.5% for passive, <1% for active |
| Category overlap | | Remove duplicate categories |
| Tax-efficiency | | Check LTCG harvesting opportunity |
| Goal alignment | | Is the portfolio matching the goal timeline? |

### 5.2 Overlap Analysis

| Fund A | Fund B | Common Stocks | Overlap % | Action |
|--------|--------|---------------|-----------|--------|
| | | | | Keep both / Remove one |

### 5.3 Performance Attribution

| Holding | Purchase Date | Cost | Current Value | XIRR | Benchmark XIRR | Alpha |
|---------|-------------|------|---------------|------|-----------------|-------|
| | | | | | | |

### 5.4 Rebalancing Recommendation

| Asset Class | Target % | Current % | Drift | Action | Amount |
|-------------|----------|-----------|-------|--------|--------|
| Equity | ___% | ___% | ___% | Buy/Sell/Hold | ₹___ |
| Debt | ___% | ___% | ___% | | ₹___ |
| Gold | ___% | ___% | ___% | | ₹___ |

**Rebalancing rules**:
- Rebalance annually or when any asset class drifts >5% from target
- Prefer rebalancing by adding to underweight (not selling overweight) — avoids tax
- If must sell, harvest LTCG up to ₹1.25L tax-free limit
- Don't rebalance more frequently than every 6 months

## Step 6: Tax-Efficient Structuring

### LTCG Harvesting Strategy

If unrealized equity gains >₹1.25L at year-end:
1. Sell equity holdings with gains up to ₹1.25L (tax-free)
2. Buy back immediately (resets cost basis)
3. Saves 12.5% tax on future gains
4. Do this every March

### Tax-Saving Allocation (Section 80C)

| Instrument | Amount | Lock-in | Expected Return | Priority |
|------------|--------|---------|-----------------|----------|
| EPF (auto-deducted) | ₹___ | Till retirement | ~8% | 1st (mandatory) |
| ELSS Mutual Fund | ₹___ | 3 years | 12-14% | 2nd (best risk-reward) |
| PPF | ₹___ | 15 years | ~7% | 3rd (if conservative) |
| NPS | ₹___ | Till retirement | 8-10% | Extra ₹50K under 80CCD(1B) |
| **Total 80C** | **₹1,50,000** | | | |

### Tax Optimization Tips
- Use ELSS for 80C instead of 5-year FD (better post-tax returns)
- Hold equity >12 months for LTCG benefit
- Debt funds: Hold longer only if in lower tax bracket (post-2023 rules)
- Harvest tax losses to offset gains
- NPS gives extra ₹50K deduction under 80CCD(1B) — good for 30% bracket

## Step 7: Ongoing Monitoring Framework

### Quarterly Review Checklist

| Item | What to Check | Action Trigger |
|------|--------------|----------------|
| Portfolio value | Track in spreadsheet/app | — |
| Asset allocation drift | Compare to target | >5% drift → rebalance |
| Fund performance | vs benchmark and peers | 3 consecutive quarters underperformance → review |
| Fund manager change | News/factsheet | New manager → monitor 2 quarters |
| Goal progress | Are you on track? | Behind pace → increase SIP |
| Life changes | New goal, income change | Update plan |

### Annual Review Checklist

| Item | Action |
|------|--------|
| Rebalance portfolio | Align to target allocation |
| LTCG harvesting | Sell/rebuy up to ₹1.25L tax-free |
| Step-up SIPs | Increase by 10% or salary hike % |
| Review fund selection | Replace persistent underperformers |
| Update risk profile | Age changed, goals changed? |
| Tax planning | Optimize 80C, NPS, HRA |
| Insurance review | Adequate coverage? |

### What NOT to Do
- Don't check portfolio daily
- Don't react to market news/crashes emotionally
- Don't stop SIPs in bear markets
- Don't chase last year's best-performing fund
- Don't time the market with large amounts
- Don't take on leverage/margin for investing

## Special Scenario Portfolios

### Scenario: NRI Investing in India
- Can invest in most MFs and stocks (repatriable/non-repatriable)
- Need NRE/NRO demat account
- TDS applicable on gains
- DTAA benefits may apply
- ELSS and PPF restrictions for some NRI categories

### Scenario: Retirement Income Portfolio
- Focus: Regular income + capital preservation
- SWP (Systematic Withdrawal Plan) from balanced funds
- Dividend income from stable companies
- Debt heavy allocation (60-70%)
- 3-year expense bucket in liquid/short-term debt

### Scenario: Child's Education Fund
- Glide path: Reduce equity as goal approaches
- Start aggressive (80% equity), gradually shift to debt
- Last 2 years: 80%+ in debt
- Consider child's age as the clock

### Scenario: First-Time Investor with Small Amount (<₹5,000/month)
- Keep it SIMPLE: 1-2 funds maximum
- Option A: 100% in Nifty 50 Index Fund
- Option B: 70% Nifty 50 Index + 30% Short Duration Debt
- Increase allocation complexity only when SIP crosses ₹15,000/month
