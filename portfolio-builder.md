---
name: portfolio-builder
description: |
  Builds customized investment portfolios for Indian investors. Covers risk profiling,
  goal-based asset allocation, fund/stock selection, SIP planning, lumpsum deployment,
  tax-efficient structuring, international diversification, dividend income portfolios,
  and rebalancing strategy. Recommends free portfolio tracking tools.
triggers:
  - build portfolio
  - asset allocation
  - investment plan
  - portfolio review
  - rebalance portfolio
  - how to invest amount
  - retirement planning
  - goal based investing
  - dividend portfolio
  - international diversification
  - NRI investing
---

# Portfolio Builder — Investment Portfolio Construction

## Activation

When the user wants to build a new portfolio, review an existing one, create an investment plan, or get structured guidance on asset allocation.

## Step 1: Risk Profiling

**Before building ANY portfolio, gather this information.** Ask if not provided.

### Required Inputs

| Parameter | User's Answer | Why It Matters |
|-----------|--------------|----------------|
| Age | | Equity capacity (100-age rule baseline) |
| Annual income | | Investment capacity, tax bracket |
| Monthly investable surplus | | SIP sizing |
| Lumpsum available (₹) | | Deployment strategy |
| Investment goal(s) | | Category and horizon selection |
| Time horizon per goal | | Equity vs debt ratio |
| Existing investments | | Avoid duplication, identify gaps |
| Existing loans/EMIs | | Debt repayment vs investment trade-off |
| Emergency fund status | | Pre-requisite check |
| Insurance status | | Pre-requisite check |
| Tax bracket (%) | | ELSS, NPS, debt fund relevance |
| Risk tolerance | Can you hold without selling through a 40% fall? | Equity allocation cap |

### Risk Profile Classification

| Profile | Who It Fits | Max Equity | Behavioural Test |
|---------|------------|------------|------------------|
| Ultra Conservative | Retirees, very short horizon | 20% | Cannot tolerate any drawdown |
| Conservative | Near-retirement, short goals | 40% | Can tolerate 10-15% drawdown |
| Moderate | Mid-career, 5Y+ horizon | 65% | Can tolerate 25-30% drawdown |
| Aggressive | Young earner, 10Y+ horizon | 85% | Can tolerate 40-50% drawdown |
| Very Aggressive | Young, high income, no near-term needs | 95% | Can tolerate 50%+ drawdown and ignore it |

### Pre-requisites Check (Non-Negotiable)

Verify before ANY portfolio is built:

- [ ] **Emergency Fund**: 6-12 months of expenses in Liquid fund or savings. If NO → build this first before investing anywhere.
- [ ] **Health Insurance**: ₹10-25L family floater. If NO → priority over all investing.
- [ ] **Term Life Insurance**: 10-15x annual income if dependents. If NO → buy before investing.
- [ ] **No high-interest debt**: Credit card (36-48% p.a.) or personal loan (14-24%). If YES → pay these off first; guaranteed return beats any investment.
- [ ] **KYC complete**: PAN-Aadhaar linked, bank account ready for investing.

If any pre-requisite is missing, address it first. Do not skip this.

## Step 2: Asset Allocation

### 2.1 Strategic Asset Allocation — Use All Three Frameworks, Take Most Conservative

**Framework 1: Age-Based**
```
Equity % = min(110 - Age, Risk-adjusted max)
Debt %   = Remaining after Gold
Gold %   = 5-10%

Examples:
Age 25 → 85% equity, 10% debt, 5% gold
Age 35 → 75% equity, 15% debt, 10% gold
Age 45 → 65% equity, 25% debt, 10% gold
Age 55 → 55% equity, 35% debt, 10% gold
Age 65 → 40% equity, 50% debt, 10% gold
```

**Framework 2: Goal-Based**

| Goal | Horizon | Equity | Debt | Gold | Rationale |
|------|---------|--------|------|------|-----------|
| Emergency fund | Always liquid | 0% | 100% | 0% | Capital safety paramount |
| Short-term goal | <3 years | 0-20% | 80-100% | 0% | Cannot afford drawdown before goal |
| Medium-term goal | 3-7 years | 40-60% | 30-50% | 10% | Balance growth and safety |
| Long-term goal | 7-15 years | 60-80% | 15-30% | 5-10% | Growth-oriented |
| Retirement (15Y+) | 15+ years | 70-90% | 5-20% | 5-10% | Maximum compounding time |
| Wealth creation | 10Y+ | 75-95% | 0-15% | 5-10% | Aggressive growth |

**Framework 3: Risk-Based**
Use the maximum equity % from risk profile in Step 1.

**Final Rule**: Take the MOST CONSERVATIVE output of the three frameworks.
- If age says 75% but risk tolerance says 40% → use 40%
- If goal says 70% but age says 55% → use 55%

### 2.2 Detailed Allocation Table

| Asset Class | Sub-category | Allocation % | Amount (₹) | Purpose |
|-------------|-------------|-------------|------------|---------|
| **Equity** | | ___% | ₹___ | Long-term growth |
| | Large Cap / Index | ___% | ₹___ | Core — stability, market returns |
| | Mid Cap | ___% | ₹___ | Growth acceleration |
| | Small Cap | ___% | ₹___ | High growth (optional, 10Y+ only) |
| | International | ___% | ₹___ | Global diversification (5-15%) |
| **Debt** | | ___% | ₹___ | Stability, income |
| | Liquid / Ultra Short | ___% | ₹___ | Emergency + short-term parking |
| | Short / Corporate Bond | ___% | ₹___ | Core debt holding |
| | Gilt / SDL | ___% | ₹___ | Safety (optional) |
| **Gold** | | ___% | ₹___ | Inflation hedge, crisis protection |
| | SGB (Sovereign Gold Bond) | ___% | ₹___ | Long-term gold (2.5% interest + no LTCG) |
| | Gold ETF | ___% | ₹___ | Tactical / liquid gold |
| **Total** | | **100%** | **₹___** | |

### 2.3 Multiple Goals — Separate Sub-Portfolios

If user has multiple goals, build separate buckets:

| Goal | Target Corpus | Timeline | Equity% | Monthly SIP | Lumpsum |
|------|--------------|----------|---------|-------------|---------|
| Emergency fund | ₹___ (6M expenses) | Immediate | 0% | — | ₹___ (park in liquid) |
| {Goal 1} | ₹___ | ___ years | ___% | ₹___ | ₹___ |
| {Goal 2} | ₹___ | ___ years | ___% | ₹___ | ₹___ |
| Retirement | ₹___ | ___ years | ___% | ₹___ | ₹___ |
| **Total monthly** | | | | **₹___** | **₹___** |

## Step 3: Security Selection

### 3.1 Mutual Fund Portfolio (Recommended for most investors)

**Fetch current data before recommending any fund** from Value Research / Moneycontrol.

**Core-Satellite Approach**:

| Role | % of Equity | Fund Type | Criteria |
|------|------------|-----------|----------|
| **Core** (50-60%) | Stable base | Nifty 50 Index / Nifty Next 50 Index | Low cost, passive, market returns |
| **Growth** (25-35%) | Alpha generation | Flexi Cap or Mid Cap active fund | 7Y+ consistent benchmark alpha |
| **Tactical** (0-10%) | Optional upside | Small cap / Sectoral / International | Only for aggressive, 10Y+ horizon |

**Fund Selection Rules**:
1. Maximum 5-7 funds total. More = overlap, not diversification.
2. No two funds from same category.
3. Check overlap — if two funds share >40% holdings, keep only one.
4. Always choose Direct plans. Never Regular plans.
5. Default to index funds for large cap unless active fund shows 7Y+ verified alpha.
6. Spread across 2-3 AMCs for AMC-level risk diversification.
7. Verify AMC governance is clean (see mutual-fund-advisor.md Step 3).

**Portfolio Template**:

| # | Fund Name | Category | Expense Ratio | 5Y CAGR | Monthly SIP | Role |
|---|-----------|----------|---------------|---------|-------------|------|
| 1 | {Nifty 50 Index Fund} | Index | ~0.1% | | ₹___ | Core equity |
| 2 | {Flexi Cap / Mid Cap} | Active equity | ~0.7% | | ₹___ | Growth |
| 3 | {ELSS — if 80C needed} | Tax-saving equity | ~0.8% | | ₹___ | Tax + equity |
| 4 | {Short Duration Debt} | Debt | ~0.3% | | ₹___ | Stability |
| 5 | {SGB or Gold ETF} | Gold | ~0% / ~0.5% | | ₹___ | Hedge |
| 6 | {US Index FOF — optional} | International | ~0.5% | | ₹___ | Global diversification |
| | **Total** | | **Wtd avg: ___%** | | **₹___** | |

### 3.2 Direct Equity Portfolio (Intermediate+ investors only)

Recommend direct stocks only if:
- User has 7Y+ horizon
- Equity investable amount >₹5L
- User understands stock-specific risk and will monitor quarterly results
- Corporate governance check will be done on every stock (see stock-analyzer.md)

**Minimum Stock Selection Criteria**:

| Criterion | Minimum Bar |
|-----------|------------|
| Market Cap | >₹10,000 Cr (avoid micro-caps) |
| ROE (3Y average) | >15% |
| Debt/Equity | <1 (except banking/NBFC) |
| Profit Growth (5Y CAGR) | >10% |
| Promoter Holding | >40%, no pledge concern |
| Free Cash Flow | Positive for 3+ consecutive years |
| Corporate Governance | No major red flags (run full governance check) |

**Diversification Rules**:
- 10-20 stocks. Fewer = concentration risk. More = index fund in disguise.
- Single stock cap: 10% of equity portfolio max
- Single sector cap: 25% of equity portfolio max
- Minimum 3 different sectors
- Mix: 50-60% large cap, 30-40% mid cap, 0-10% small cap

## Step 4: International Diversification

### Why Include International Exposure

| Reason | Detail |
|--------|--------|
| Geographic diversification | India = ~3% of global markets. Too concentrated in one country. |
| Currency hedge | INR has historically depreciated ~3-4% annually vs USD. USD assets appreciate in INR terms. |
| Access to global leaders | Apple, Microsoft, Alphabet, NVIDIA — not available in India |
| Cycle diversification | India and US economic cycles don't perfectly correlate |
| **Limit**: 10-15% of equity | Beyond this, complexity rises without proportionate benefit |

### Implementation Options (India Route — No LRS Needed)

| Option | Example Funds | Pros | Cons |
|--------|--------------|------|------|
| US S&P 500 FOF | Motilal S&P 500 Direct, Franklin US Feeder | Broad US exposure, passive | FOF cost layering ~0.5-0.8% total |
| Nasdaq 100 FOF/ETF | Motilal Nasdaq 100 ETF, Mirae US Equity ETF | Tech-heavy, high growth | Concentrated in tech, high volatility |
| Global Diversified | Parag Parikh Flexi Cap (partial int'l), Edelweiss Greater China | Multi-country | Manager-dependent |

### LRS Route (Direct Overseas Investment)
- Allowed up to $250,000/year per individual
- TCS of 20% on remittances >₹7L/year (claimable against tax)
- Suitable for: Large portfolios (>₹1Cr equity) where 10-15% international = ₹10-15L+
- **For most retail investors: Domestic international funds are simpler and sufficient**

### SEBI Cap Warning
Always check before recommending: SEBI caps total industry international MF investment at $7B. When hit, AMCs pause fresh inflows. WebSearch: `"SEBI overseas investment limit mutual fund {current year}"` before recommending international funds.

### International Allocation by Portfolio Size

| Portfolio Size (Equity) | International % | Instrument |
|-------------------------|----------------|------------|
| <₹5L | 0% | Focus on India first |
| ₹5-25L | 5% | 1 US index fund |
| ₹25-100L | 5-10% | US index + consider Nasdaq or global |
| >₹1Cr | 10-15% | Mix of US, global, LRS for some |

## Step 5: Deployment Strategy

### 5.1 SIP Deployment

| Fund | Monthly SIP (₹) | SIP Date | Step-up % (annual) |
|------|----------------|----------|-------------------|
| | | 5th | 10% |
| | | 10th | 10% |
| | | 15th | 10% |
| **Total** | **₹___** | | |

**Tips**:
- Stagger SIP dates across the month (not all on 1st) — smooths buying price
- Set up annual step-up of 10% (or match salary increment %)
- Automate — remove the emotional decision every month
- **Never stop SIPs in market crashes** — that's when you accumulate units cheapest

### 5.2 Lumpsum Deployment

Never invest large lumpsum (>₹2L) into equity all at once.

| Scenario | Strategy | How |
|----------|----------|-----|
| Market P/E <18 (cheap) | Deploy 50% immediately + balance via STP over 3 months | Cheap market — be aggressive |
| Market P/E 18-22 (fair) | STP over 6 months | Systematic, no FOMO |
| Market P/E >22 (expensive) | STP over 9-12 months | Caution — overvalued market |
| Any large amount | Park in Liquid Fund → STP to equity fund | Clean deployment mechanism |

**STP Schedule** (example for ₹10L over 6 months):

| Month | Transfer to Equity | Remaining in Liquid |
|-------|-------------------|-------------------|
| 1 | ₹2,00,000 | ₹8,00,000 |
| 2 | ₹2,00,000 | ₹6,00,000 |
| 3 | ₹1,50,000 | ₹4,50,000 |
| 4 | ₹1,50,000 | ₹3,00,000 |
| 5 | ₹1,50,000 | ₹1,50,000 |
| 6 | ₹1,50,000 | ₹0 |

## Step 6: Portfolio Review (For Existing Portfolios)

When user shares existing portfolio, systematically audit:

### 6.1 Portfolio Health Check

| Check | Status | Action |
|-------|--------|--------|
| Asset allocation vs target | | Rebalance if drift >5% |
| Any single holding >15% | | Trim and diversify |
| More than 8-10 funds | | Consolidate — identify overlapping |
| Regular vs Direct plans | | Switch all to Direct plans |
| Weighted expense ratio | | Should be <0.5% for passive-heavy, <0.9% for active |
| Category duplication | | Remove duplicate categories |
| LTCG harvesting opportunity | | Sell/rebuy up to ₹1.25L gains tax-free |
| Goal alignment | | Does portfolio timeline match goal? |
| International exposure | | Is there any? Is 5-15% appropriate? |

### 6.2 Overlap Analysis

| Fund A | Fund B | Common Stocks | Overlap % | Decision |
|--------|--------|---------------|-----------|----------|
| | | | | Keep / Remove one |

Use Morningstar India's X-ray tool or Value Research portfolio comparison.

### 6.3 Performance Attribution

| Holding | Entry Date | Cost (₹) | Current Value (₹) | XIRR (%) | Benchmark XIRR (%) | Alpha |
|---------|-----------|----------|-------------------|----------|---------------------|-------|
| | | | | | | |

### 6.4 Rebalancing Recommendation

| Asset Class | Target % | Current % | Drift | Action | Amount (₹) |
|-------------|----------|-----------|-------|--------|------------|
| Equity | | | | Buy/Sell/Hold | |
| Debt | | | | | |
| Gold | | | | | |
| International | | | | | |

**Rebalancing rules**:
- Trigger: Annual or when any asset class drifts >5% from target
- Prefer buying underweight assets over selling overweight (avoids triggering capital gains)
- If selling is necessary, harvest LTCG up to ₹1.25L tax-free first
- Minimum rebalancing interval: 6 months (avoid over-tinkering)

## Step 7: Dividend Income Portfolio

### Who Should Build a Dividend Portfolio
- Retired investors needing regular income
- Investors with significant corpus seeking passive income alongside capital growth
- High-income earners with preference for income (though dividend is now taxed at slab — consider tax efficiency)

### Dividend Portfolio Framework

**Step 1 — Check dividend sustainability** (most important, often ignored):

| Stock Criterion | Threshold | Why |
|----------------|-----------|-----|
| Consecutive dividend years | >10 years | Consistency matters more than high current yield |
| Payout Ratio (%) | 20-60% | <20% = room to grow; >80% = risky, may not be sustainable |
| FCF Payout Ratio (Div/FCF) | <70% | Dividend funded by cash, not borrowings |
| Dividend Growth (5Y CAGR) | >8% | Dividend growing > inflation = real income growth |
| Debt/Equity | <0.5 for dividend purity | High debt + high dividend = unsustainable |
| Revenue stability | Non-cyclical preferred | Cyclical businesses cut dividends at worst times |
| Ever cut/skipped dividend? | Investigate context | Pandemic cut = forgivable; financial distress cut = red flag |

**Step 2 — Build the income table**:

| Stock | Current Yield (%) | 5Y Dividend CAGR (%) | Payout Ratio (%) | FCF Yield (%) | Sustainability | Position % |
|-------|------------------|---------------------|-----------------|---------------|----------------|------------|
| | | | | | High/Med/Low | |

**Step 3 — Dividend tax consideration**:

Dividends are taxed at the investor's slab rate (up to 30% + cess for highest bracket).
- For a 30% bracket investor: ₹100 dividend = ₹70 post-tax
- Post-tax dividend yield from a 3% gross yield stock = 3% × 0.7 = **2.1%**
- Compare with: Liquid fund ~7% × 0.7 = 4.9% post-tax
- **Verdict**: Pure dividend plays are tax-inefficient for high-bracket investors. Prefer:
  - Growth + buyback stocks (capital gains taxed at 12.5% LTCG, not slab rate)
  - Dividend portfolio for retired investors in lower tax brackets

**Step 4 — Best sectors for dividend reliability in India**:

| Sector | Why Reliable | Examples (not recommendations — verify independently) |
|--------|-------------|-----------------------------------------------------|
| IT Services | Cash-generative, capital-light, regular dividends + buybacks | TCS, Infosys, HCL Tech, Wipro |
| FMCG | Stable cash flows, consistent payer | HUL, Nestle, Dabur, Britannia |
| Power Utilities | Regulated returns, government-backed | Power Grid, NTPC, NHPC |
| Coal / Mining PSU | Government mandated payout policy | Coal India |
| Oil & Gas PSU | High dividend but commodity-cyclical | ONGC, IOC (be cautious on cycle) |

**Avoid for pure dividend income**: Banks (need capital retention for RBI norms), small caps, high-growth companies (they should reinvest, not distribute)

### Sample Dividend Portfolio (Moderate, ₹20L)

This is a structure illustration — run full analysis on each stock before using:

| Category | Allocation | Target Yield | Expected Annual Income |
|----------|-----------|--------------|----------------------|
| IT Services (2-3 stocks) | 30% = ₹6L | ~2.5% | ~₹15,000 |
| FMCG (2 stocks) | 25% = ₹5L | ~1.5% | ~₹7,500 |
| Utilities (2 stocks) | 25% = ₹5L | ~4.5% | ~₹22,500 |
| PSU Dividend payer (1-2) | 20% = ₹4L | ~5% | ~₹20,000 |
| **Total** | **100% = ₹20L** | **~3.2%** | **~₹65,000/yr** |

Note: ₹65,000/yr from ₹20L = 3.25% yield. After 30% tax = ~2.3% net yield. This is supplementary income, not a replacement for growth investing. For most investors, SWP (Systematic Withdrawal Plan) from a balanced fund is more tax-efficient.

### SWP (Systematic Withdrawal Plan) — Better Alternative to Dividend Portfolio

For retirement income, SWP from a balanced/hybrid fund is generally superior:
- **Tax efficiency**: Gains component of SWP withdrawal taxed at LTCG rate (12.5%), not slab rate
- **Flexibility**: Control the amount and frequency
- **Growth**: Remaining corpus keeps compounding
- **Setup**: Invest in Balanced Advantage Fund → Set monthly SWP of ₹___ per month

## Step 8: Tax-Efficient Structuring

### LTCG Harvesting (Do every March)

1. Identify equity holdings with unrealized LTCG
2. Sell units with gains up to ₹1.25L (zero tax)
3. Immediately buy back the same fund/stock
4. Resets cost basis — saves 12.5% tax on future gains
5. Repeat every financial year

**Example**: ₹1.25L gain harvested every year × 12.5% = ₹15,625 saved per year. Over 15 years at 10% discount rate = ~₹1.3L+ in present value savings.

### 80C Optimization

| Instrument | Priority | Amount | Return | Lock-in | Notes |
|------------|---------|--------|--------|---------|-------|
| EPF (mandatory) | 1st | Auto-deducted | ~8.25% | Till retirement | Tax-free on maturity |
| ELSS Mutual Fund | 2nd | Up to ₹1.5L total with EPF | 12-14% expected | 3 years | Best risk-return in 80C |
| PPF | 3rd | Up to ₹1.5L combined | ~7.1% | 15 years | Good for conservative investors |
| **Total 80C** | | **₹1,50,000** | | | |

### Additional Deductions

| Section | Instrument | Deduction | Notes |
|---------|-----------|-----------|-------|
| 80CCD(1B) | NPS | ₹50,000 extra | Over and above 80C limit. Good for 30% bracket. |
| 80D | Health Insurance premium | ₹25K self + ₹25K parents (₹50K if senior) | Essential coverage anyway |
| 24(b) | Home loan interest | Up to ₹2L | If applicable |

## Step 9: Portfolio Tracking Tools

Recommend based on user's situation:

| Tool | Free? | Best For | URL |
|------|-------|----------|-----|
| **Kuvera** | Yes | MF tracking, direct plan investing, goal planning, tax reports | kuvera.in |
| **INDMoney** | Yes | All-in-one: Stocks + MF + FD + NPS + US stocks, net worth tracking | indmoney.com |
| **Value Research Portfolio** | Yes | MF portfolio tracker with overlap analysis, rolling returns | valueresearchonline.com |
| **Groww** | Yes | Simple MF and stock tracking, SIP management | groww.in |
| **Zerodha Console** | Zerodha users | Holdings, P&L, tax P&L report, detailed analytics | console.zerodha.com |
| **Wisesheets (Google Sheets add-in)** | Free add-in | Custom stock monitoring, auto-update live Indian stock prices in sheets | wisesheets.io |
| **Simply Wall St** | Freemium | Visual portfolio analysis, snowflake quality diagrams | simplywall.st |
| **Tickertape Portfolio** | Free | Stock + MF combined tracking, rebalancing alerts | tickertape.in |
| **Excel/Google Sheets (DIY)** | Free | Full control, custom metrics, XIRR calculations | Build manually |

**Recommended setup for most investors**:
1. **Kuvera** for MF investing and tracking (Direct plans, goal mapping)
2. **INDMoney** for consolidated net worth view across all assets
3. **Zerodha Console / Tickertape** for stock portfolio tracking

## Step 10: Ongoing Monitoring Framework

### Quarterly Checklist

| Item | What to Check | Action Trigger |
|------|--------------|----------------|
| Portfolio value and XIRR | Track vs benchmark | Investigate if XIRR <benchmark for 4 quarters |
| Asset allocation drift | Compare to target | Drift >5% → rebalance |
| SIP continuity | All SIPs running? | Set payment failure alerts |
| Fund manager changes | AMC announcements | New manager → monitor 2 quarters |
| Goal progress | On track for corpus? | Behind pace → increase SIP |

### Annual Checklist

| Item | Action |
|------|--------|
| Full rebalance | Align to target allocation |
| LTCG harvesting | Execute by March 31 |
| Step-up SIPs | Increase by 10% or salary increment % |
| Fund review | Replace funds with 3Y+ consistent underperformance vs benchmark |
| Risk profile update | Age changed? New goal? |
| Tax planning | 80C, 80D, 80CCD(1B), HRA fully utilized? |
| Insurance review | Coverage still adequate? |
| International allocation | SEBI limit check for international funds |

### What NOT to Do
- Don't check portfolio daily (noise kills discipline)
- Don't stop SIPs in market crashes (buy more units at lower NAV)
- Don't chase last year's top fund (performance reverts)
- Don't invest money needed in <3 years in equity
- Don't use leverage or margin for long-term investing
- Don't over-diversify (8-10 positions total is enough)

## Special Scenarios

### NRI Investing in India

| Aspect | Detail |
|--------|--------|
| Demat account | NRE or NRO demat required (through NRI-enabled broker) |
| MF investing | Most MFs allowed for NRIs; US/Canada-based NRIs restricted by some AMCs |
| TDS on gains | Capital gains TDS applies (unlike residents who self-assess) |
| DTAA benefit | Double Taxation Avoidance Agreement may reduce tax |
| ELSS | Allowed for NRIs (useful for 80C if filing India taxes) |
| PPF | **Not allowed** for NRIs (cannot open new PPF, existing can continue) |
| Repatriation | NRE investments freely repatriable; NRO has limits |
| Recommended | Use NRE account for investments planned to be repatriated |

### Retirement Income Portfolio (Post-Retirement)

Structure as three buckets:

| Bucket | Horizon | Allocation | Instrument | Purpose |
|--------|---------|-----------|------------|---------|
| Bucket 1: Immediate | 0-2 years | 15-20% | Liquid fund, Short duration debt | Living expenses, no market risk |
| Bucket 2: Medium | 2-7 years | 40-45% | Conservative Hybrid, Balanced Advantage | Refill Bucket 1, some growth |
| Bucket 3: Long | 7+ years | 35-40% | Equity Index fund, Flexi Cap | Inflation protection, legacy |

Use SWP from Bucket 2 to fund monthly expenses. Replenish Bucket 1 annually from Bucket 2. Replenish Bucket 2 from Bucket 3 every 3-4 years when equity does well.

### Child Education Fund — Glide Path

| Phase | Years to Goal | Equity % | Debt % | Action |
|-------|--------------|----------|--------|--------|
| Early | 10+ years away | 80% | 20% | Aggressive growth, maximize compounding |
| Mid | 5-10 years away | 60% | 40% | Moderate growth, start capital protection |
| Late | 2-5 years away | 40% | 60% | Shift to stability |
| Final | 0-2 years away | 10-20% | 80-90% | Capital safety paramount |

Auto-rebalance every 2 years or when entering next phase.

### First-Time Investor (<₹5,000/month)

Keep it extremely simple:
- Option A: **100% Nifty 50 Index Fund Direct** — lowest cost, broad market, no decisions needed
- Option B: **70% Nifty 50 Index + 30% Short Duration Debt** — some stability
- Add complexity (second fund, mid cap, gold) ONLY when monthly SIP crosses ₹15,000
- Platform: Kuvera or Groww for direct plan SIP
