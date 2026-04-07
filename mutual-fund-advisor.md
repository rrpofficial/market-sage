---
name: mutual-fund-advisor
description: |
  Analyzes and recommends Indian mutual funds and ETFs. Evaluates performance, risk
  metrics, portfolio quality, costs, AMC governance, and fund manager track record.
  Covers international funds, ETF-specific evaluation, and SIP planning. Provides
  goal-based fund selection with critical AMC governance checks.
triggers:
  - mutual fund recommendation
  - SIP plan
  - fund comparison
  - ELSS tax saving
  - index fund
  - debt fund
  - best mutual fund
  - fund portfolio
  - ETF India
  - international fund
  - AMC analysis
---

# Mutual Fund Advisor — Fund Analysis, ETF & International Funds

## Activation

When user asks about mutual fund selection, comparison, SIP planning, ETF evaluation, international fund analysis, or fund portfolio construction.

## Step 1: Fetch Data (with Fallback Chain)

Use this priority sequence. If one source is blocked, move to the next:

**Primary chain** (try in order):
1. **Value Research**: WebSearch `"{Fund Name} value research online"` → WebFetch the fund page
2. **Moneycontrol MF**: WebSearch `"{Fund Name} moneycontrol mutual fund"` → WebFetch
3. **Morningstar India**: WebSearch `"{Fund Name} morningstar india"` → WebFetch
4. **Groww**: WebSearch `"{Fund Name} groww mutual fund"` → WebFetch
5. **Kuvera**: WebSearch `"{Fund Name} kuvera fund"` → WebFetch

**Always fetch separately**:
- **AMC governance**: WebSearch `"{AMC name} SEBI penalty action site:sebi.gov.in"` + WebSearch `"{AMC name} front running SEBI"`
- **Fund factsheet**: WebSearch `"{Fund Name} factsheet {latest month year}"` for current portfolio
- **Category comparison**: WebSearch `"best {category} mutual fund India {current year} direct plan"`

**If ALL sources fail** — present the data checklist:
```
I can't fetch live fund data. Please provide from Value Research (valueresearchonline.com):
□ 1Y, 3Y, 5Y, 10Y returns (Direct Plan CAGR)
□ Benchmark returns for same periods
□ Sharpe Ratio, Sortino Ratio, Max Drawdown
□ Expense Ratio (Direct Plan)
□ AUM (₹ Cr)
□ Fund Manager name and tenure
□ Top 10 holdings and their %
□ Portfolio P/E, P/B
□ Portfolio turnover %
```

**Critical**: Always use **Direct Plan** data (not Regular). If user holds Regular plans, flag the cost difference and recommend switching.

## Step 2: Understand User Context

Before recommending, clarify if not already provided:

| Parameter | User's Answer | Why It Matters |
|-----------|--------------|----------------|
| Goal | | Determines fund category |
| Horizon | | Equity vs debt ratio |
| Risk tolerance | | Equity allocation cap |
| Existing portfolio | | Avoid overlap |
| Tax bracket | | ELSS relevance, debt vs equity tax trade-off |
| Investment mode | | SIP vs lumpsum → category suitability |
| Monthly surplus | | SIP amount |
| Lumpsum available | | Deployment strategy |

If not provided, **ask before recommending**. A fund recommendation without context is irresponsible.

## Step 3: AMC (Fund House) Governance Check — DO THIS BEFORE RECOMMENDING

**Just as company governance matters for stocks, AMC integrity matters for funds.**

### 3.1 AMC Governance Red Flags

Search: `"{AMC name} SEBI action penalty"` + `"{AMC name} front running scandal"`

| Red Flag | Finding | Status |
|----------|---------|--------|
| SEBI enforcement orders against AMC | | Clean/Flagged |
| Front-running allegations (fund managers trading ahead of fund) | | Clean/Flagged |
| AMC penalty for mis-selling | | Clean/Flagged |
| Key management exits under controversy | | Clean/Flagged |
| Distributor commission kickback issues | | Clean/Flagged |
| Circular investing (AMC investing in own promoter's debt) | | Clean/Flagged |
| Side-pocketing misuse (debt fund credit events) | | Clean/Flagged |
| SEBI orders on NAV manipulation | | Clean/Flagged |

> **Note**: The 2022 Axis MF front-running case (fund managers trading ahead of scheme orders) is a real example. Always check for such cases before recommending.

### 3.2 AMC Strength Assessment

| Aspect | Detail |
|--------|--------|
| AMC Name | |
| Promoter group | (Domestic bank/corporate vs foreign AMC) |
| Total AUM (₹ Cr) | (>₹50,000Cr = large, established) |
| Category strengths | (Where does this AMC excel?) |
| Fund manager stability | (High turnover = concern) |
| Regulatory standing | |
| Investor complaint resolution | (Check SEBI SCORES for AMC-level complaints) |

**AMC Score**: Strong / Adequate / Weak / Avoid

## Step 4: Fund Category Selection

### By Investment Horizon

| Horizon | Equity % | Recommended Categories |
|---------|----------|----------------------|
| <1 year | 0% | Liquid, Overnight, Ultra-short duration |
| 1-3 years | 0-20% | Short Duration, Corporate Bond, Conservative Hybrid |
| 3-5 years | 30-50% | Balanced Advantage (BAF), Aggressive Hybrid, Large Cap |
| 5-7 years | 50-70% | Large Cap, Flexi Cap, Large & Mid Cap |
| 7-10 years | 60-80% | Flexi Cap, Mid Cap, Large & Mid Cap |
| 10+ years | 70-100% | Mid Cap, Small Cap, Flexi Cap, Nifty/Next 50 Index |

### Full Category Reference

**Equity Funds**:
| Category | Risk Level | Expected CAGR (LT) | Minimum Horizon | Notes |
|----------|-----------|-------------------|-----------------|-------|
| Large Cap | Moderate | 10-12% | 5Y | Top 100 cos by market cap |
| Mid Cap | High | 12-15% | 7Y | 101-250 by market cap |
| Small Cap | Very High | 14-18% | 10Y | 251+ by market cap |
| Flexi Cap | Mod-High | 11-14% | 5Y | No market cap restriction |
| Large & Mid Cap | Moderate-High | 11-14% | 7Y | Min 35% each in large, mid |
| Focused Fund | High | 12-15% | 7Y | Max 30 stocks, concentrated |
| ELSS | High | 12-15% | 3Y lock-in | Tax deduction under 80C |
| Index Fund (Nifty 50) | Moderate | 10-12% | 5Y | Passive, ~0.1-0.2% expense |
| Index Fund (Nifty Next 50) | Mod-High | 11-14% | 7Y | More mid-cap tilt |
| Sectoral/Thematic | Very High | Cyclical | 7Y+ | Avoid unless conviction |

**Debt Funds**:
| Category | Risk | Approx Return | Horizon | Use Case |
|----------|------|---------------|---------|----------|
| Overnight | Negligible | ~6.5% | 1 day | Very short parking |
| Liquid | Very Low | ~7% | <3 months | Emergency fund |
| Ultra Short Duration | Low | ~7-7.5% | 3-12 months | Short-term parking |
| Short Duration | Low-Mod | ~7.5-8% | 1-3 years | Short goals |
| Corporate Bond | Low-Mod | ~7.5-8.5% | 3+ years | Core debt allocation |
| Banking & PSU Debt | Low | ~7.5-8% | 3+ years | High credit quality |
| Gilt | Low credit, rate-sensitive | ~7-8% | 3+ years | When rates falling |
| Dynamic Bond | Variable | ~7-9% | 3+ years | Active duration management |
| Credit Risk | High | ~8-10% | 3+ years | Avoid unless specifically needed |

**Hybrid Funds**:
| Category | Equity % | Risk | Notes |
|----------|----------|------|-------|
| Conservative Hybrid | 10-25% | Low-Mod | For very conservative investors |
| Balanced Advantage (BAF) | Dynamic (30-80%) | Moderate | Model-driven equity/debt switch |
| Aggressive Hybrid | 65-80% | Mod-High | Equity taxation benefit |
| Multi-Asset | 65%+ equity | Moderate | Equity + debt + gold in one fund |

## Step 5: Fund Evaluation Framework

### 5.1 Performance Analysis

| Period | Fund Return | Category Avg | Benchmark | Alpha (Fund-Bmk) | Assessment |
|--------|-------------|--------------|-----------|------------------|------------|
| 1 Year | | | | | |
| 3 Year (CAGR) | | | | | |
| 5 Year (CAGR) | | | | | |
| 7 Year (CAGR) | | | | | |
| 10 Year (CAGR) | | | | | |
| Since Inception | | | | | |

**Performance red flags**:
- Underperforms benchmark across 3Y, 5Y, 7Y → Avoid (use index fund instead)
- Beats only in 1Y → Possible lucky year, insufficient evidence
- Beats in 3Y/5Y but not 10Y → Style worked recently but not durable

**Rolling returns** (more reliable than point-to-point):
- 3Y rolling (min/max/avg over last 10 years)
- 5Y rolling (min/max/avg)
- % of periods where fund beat benchmark → >60% = skilled manager

### 5.2 Risk Metrics

| Metric | Fund | Category Avg | Benchmark | Assessment |
|--------|------|--------------|-----------|------------|
| Std Deviation (3Y %) | | | | Lower = less volatile |
| Sharpe Ratio (3Y) | | | | >1 Good, >1.5 Excellent |
| Sortino Ratio | | | | Higher = better downside protection |
| Max Drawdown (%) | | | | Smaller absolute value = better |
| Beta | | | | <1 = defensive, >1 = aggressive |
| Alpha (Jensen's) | | | | >0 = value added by manager |
| Information Ratio | | | | >0.5 = consistent alpha generation |
| Upside Capture Ratio | | | | >100% ideal |
| Downside Capture Ratio | | | | <100% ideal |

**Best scenario**: High upside capture + Low downside capture = fund outperforms in bull AND protects in bear.

### 5.3 Portfolio Quality

| Aspect | Value | Assessment |
|--------|-------|------------|
| Total holdings | | >40 = diversified; <25 = concentrated |
| Top 10 holdings concentration (%) | | >50% = concentrated risk |
| Top sector (%) | | >25% = sector concentration |
| Top 3 sectors (%) | | >60% = sector risk |
| Large/Mid/Small cap split | | Matches category mandate? |
| Portfolio P/E | | vs Nifty P/E |
| Portfolio P/B | | |
| Portfolio turnover (%) | | <50% = buy-and-hold style; >100% = active churner |
| Overlap with Nifty 50 (%) | | High overlap = expensive index fund |
| Overlap with other funds in user's portfolio | | >50% common stocks = redundant |

### 5.4 Cost Analysis

| Component | This Fund | Category Avg | 20Y Impact on ₹1L/month SIP |
|-----------|-----------|--------------|------------------------------|
| Expense Ratio — Direct (%) | | | |
| Expense Ratio — Regular (%) | | | |
| Direct vs Regular gap (%) | | | |
| Exit Load | | | |
| Exit Load Free After | | | |

**Cost compounding** — always show this for each recommendation:

At 12% gross return, ₹10,000/month SIP for 20 years:
- 0.2% expense ratio (index fund): ≈ ₹98.9L
- 0.8% expense ratio (active direct): ≈ ₹93.2L
- 1.5% expense ratio (active regular): ≈ ₹86.4L
- **Difference between index and regular active**: ≈ ₹12.5L — pure cost drag

### 5.5 Fund Manager Assessment

| Aspect | Detail |
|--------|--------|
| Fund Manager Name | |
| Tenure on this fund | <2 years = insufficient track record |
| Other funds managed | Too many funds = stretched attention |
| Performance of other funds managed | Cross-validate skill |
| Investment philosophy/style | Growth/Value/Blend/Momentum |
| Style consistency (does portfolio reflect stated style?) | Style drift = red flag |
| Interview/commentary quality | Rational? Evidence-based? Or vague? |

## Step 6: ETF Evaluation Framework

### When to Use ETF vs Index Fund

| Factor | ETF | Index Fund |
|--------|-----|------------|
| Buying mechanism | Stock exchange (demat required) | Direct with AMC (no demat needed) |
| Price | Real-time market price | EOD NAV |
| Expense ratio | Slightly lower (0.05-0.15%) | Slightly higher (0.1-0.2%) |
| Bid-ask spread cost | Yes (can be 0.1-0.5%+) | None |
| Min investment | 1 unit (~market price) | ₹500 SIP |
| Liquidity risk | Yes (illiquid ETFs) | None |
| Tracking error | Typically higher than index funds | Typically lower |
| Ideal for | Large lumpsum, trading convenience | SIP investors, beginners |

**Verdict**: For most retail investors doing SIPs, **index funds beat ETFs** due to no bid-ask spread and easier investing. ETFs are better for large lumpsums and when expense ratio difference is significant.

### ETF-Specific Evaluation Metrics

| Metric | Value | Good Range | Notes |
|--------|-------|------------|-------|
| **Tracking Error (1Y, %)** | | <0.5% | How closely ETF tracks index. Lower = better |
| **Tracking Difference (%)** | | Negative or near 0 | Return of ETF minus return of index. Negative = ETF outperformed after costs |
| **Avg Daily Volume (₹ Cr)** | | >₹10Cr/day | Liquidity. Low volume = wide bid-ask spreads |
| **Avg Bid-Ask Spread (%)** | | <0.1% | Cost of buying/selling. Check on NSE/BSE |
| **Premium/Discount to NAV (%)** | | ±0.2% | ETF price vs underlying NAV. Large premium = overpaying |
| **AUM (₹ Cr)** | | >₹500Cr | Larger AUM = better liquidity, lower costs |
| **Market Maker quality** | | Active MM | AMC or authorized participant maintains liquidity |
| **Creation/Redemption spread** | | | Mechanism ensuring ETF price stays near NAV |

### ETF Evaluation Table

| ETF Name | Underlying Index | Expense Ratio | Tracking Error | Avg Volume | AUM | Verdict |
|----------|-----------------|---------------|----------------|------------|-----|---------|
| | | | | | | |

### ETF Red Flags
- [ ] Tracking error >1% consistently
- [ ] Daily volume <₹5 Cr (illiquid — avoid)
- [ ] AUM <₹100 Cr (may be wound up by AMC)
- [ ] Trades at persistent premium >0.5% to NAV
- [ ] No active market maker
- [ ] Sector/thematic ETF with no fundamental case

### ETF Categories in India

| Category | Example ETFs | Use Case |
|----------|-------------|----------|
| Broad Market | Nifty 50 ETF, Sensex ETF | Core equity allocation |
| Mid/Small | Nifty Midcap 150 ETF, Nifty Smallcap 250 ETF | Growth tilt |
| Factor | Nifty Alpha 50, Nifty Value 20, Nifty Quality 30 | Smart beta |
| Sectoral | Bank Nifty ETF, IT ETF, Pharma ETF | Tactical sector bets |
| Gold ETF | Nippon Gold ETF, SBI Gold ETF | Gold allocation |
| International | Mirae US ETF, Motilal Nasdaq 100 ETF | Global diversification |
| Debt/Gilt | Bharat Bond ETF, Gilt ETFs | Debt allocation |

**Gold ETF vs SGB (Sovereign Gold Bond)**:
- SGB: 2.5% annual interest + no capital gains tax on maturity → **preferred for long-term gold allocation**
- Gold ETF: Liquid, tradable, no lock-in → **preferred for tactical/short-term gold**

## Step 7: International Fund Evaluation

### Why International Diversification Matters
- India is ~3% of global market cap
- US market is ~45% of global market cap
- Currency hedge against INR depreciation over long term
- Access to global leaders (Apple, Microsoft, Alphabet) unavailable in India
- Diversification across economic cycles

### Types of International Funds Available in India

| Type | Examples | What it Invests In | Currency Risk |
|------|---------|-------------------|---------------|
| US Index FOF | Motilal US Direct, Franklin US Feeder | S&P 500 / Nasdaq 100 | Yes (INR/USD) |
| Global Diversified | Parag Parikh Flexi Cap (partial), Kotak World Gold | Multi-country | Yes |
| Thematic International | Mirae Global Electric & Autonomous, Edelweiss Europe | Specific global themes | Yes |
| International ETF | Motilal Nasdaq 100 ETF | US tech index | Yes |

### LRS (Liberalised Remittance Scheme) Context
- Under LRS, resident Indians can remit up to **$250,000 per year** for investments
- TCS (Tax Collected at Source) of **20% applies** on LRS remittances above ₹7L/year (can be offset against tax liability)
- For amounts above TCS threshold, direct foreign investment may be less efficient
- **Domestic international funds avoid LRS entirely** — preferred route for most investors

### Evaluation Framework for International Funds

| Metric | Value | Notes |
|--------|-------|-------|
| Underlying index / portfolio | | S&P 500? Nasdaq? Global? |
| Expense ratio (total, incl. underlying fund) | | FOF layering adds cost |
| Currency hedged or unhedged | | Usually unhedged = INR depreciation benefit |
| 5Y return in INR | | Include currency impact |
| 5Y return in USD | | Separate performance from currency |
| Tracking error (for index FOFs) | | Should be low |
| SEBI restriction impact | | SEBI has paused fresh investments in some int'l funds when industry-level limits are hit |

### SEBI Overseas Investment Limit Warning
SEBI caps total overseas investment by Indian MF industry at **$7 billion**. When this limit is hit, AMCs pause fresh inflows into international funds. **Always check if the fund is accepting fresh investments before recommending.**

### Suggested International Allocation

| Investor Profile | International Allocation | Instrument |
|-----------------|--------------------------|------------|
| Beginner, <₹10L portfolio | 0% (complexity not worth it) | Focus on domestic first |
| Intermediate, 5Y+ horizon | 5-10% of equity | US index fund / Nasdaq FOF |
| Advanced, >₹25L portfolio | 10-15% of equity | Mix of US index + global diversified |
| All profiles | Cap at 15% | Over-allocation adds complexity, not proportionate benefit |

## Step 8: SIP Planning

### SIP Calculator Output

For any SIP recommendation, show projections at multiple return assumptions:

| Parameter | Value |
|-----------|-------|
| Monthly SIP | ₹___ |
| Duration | ___ years |
| Total Amount Invested | ₹___ |
| Expected Corpus @ 10% CAGR | ₹___ |
| Expected Corpus @ 12% CAGR | ₹___ |
| Expected Corpus @ 14% CAGR | ₹___ |

**SIP step-up** (10% annual increase):
| Year | Monthly SIP (₹) | Cumulative Invested (₹) | Corpus @ 12% (₹) |
|------|----------------|------------------------|-----------------|
| 1 | | | |
| 5 | | | |
| 10 | | | |
| 15 | | | |
| 20 | | | |

### SIP vs Lumpsum Framework

| Market Condition | Nifty P/E | Recommendation | Why |
|-----------------|-----------|----------------|-----|
| Cheap | <18 | Lumpsum preferred | High margin of safety |
| Fair | 18-22 | SIP preferred | Averaging is prudent |
| Expensive | 22-26 | SIP mandatory | Avoid buying peak |
| Very expensive | >26 | SIP with caution; deploy slowly | Drawdown risk high |
| Large amount (>₹5L equity) | Any | STP over 6-12 months | Smooth entry regardless of market |

## Step 9: Fund Comparison

When comparing 2-3 funds:

| Parameter | Fund A | Fund B | Fund C | Winner |
|-----------|--------|--------|--------|--------|
| AMC governance | | | | |
| 3Y CAGR (Direct) | | | | |
| 5Y CAGR (Direct) | | | | |
| Benchmark alpha (5Y) | | | | |
| Sharpe Ratio | | | | |
| Max Drawdown | | | | |
| Expense Ratio | | | | |
| AUM (₹ Cr) | | | | |
| Manager Tenure | | | | |
| Portfolio Turnover | | | | |
| Top 10 Concentration | | | | |
| Rolling return consistency | | | | |
| **Overall Verdict** | | | | |

## Step 10: Fund Red Flags (Auto-Check)

Before any recommendation, verify ALL of these:

- [ ] AMC has no recent SEBI enforcement action or front-running case
- [ ] Consistent underperformance vs benchmark for 3+ years → switch to index fund
- [ ] Expense ratio >1.5% for equity direct plans → switch to lower-cost fund
- [ ] Expense ratio >0.5% for debt direct plans → compare alternatives
- [ ] Fund manager changed in last 12 months → track record resets
- [ ] AUM <₹100 Cr → liquidity/viability risk
- [ ] AUM >₹25,000 Cr for mid/small cap → size drag on performance
- [ ] Portfolio turnover >150% → expensive churning, tax drag
- [ ] Style drift (large cap fund buying 20%+ mid/small caps) → mandate violation
- [ ] Exit load applicable for user's investment horizon
- [ ] Overlap >50% with another fund user already holds
- [ ] For international funds: confirm SEBI limit not hit (fresh investments open)
- [ ] For ETFs: confirm daily volume >₹10 Cr and tracking error <0.5%
- [ ] Single stock >10% in portfolio → concentration risk
- [ ] Single sector >35% → sector concentration

## Step 11: Recommendation Output

### For Single Fund Analysis

**Fund**: {Name} — {Category} — {AMC}
**AMC Governance**: {Strong/Adequate/Weak}
**Verdict**: INVEST / AVOID / CONDITIONAL (with conditions stated)

**Strengths**:
1. {Specific, data-backed}
2. {Specific, data-backed}

**Concerns** (be blunt):
1. {Specific}
2. {Specific}

**Suitable for**: {Investor type}, {Horizon}, {Risk level}
**Minimum SIP**: ₹___/month for ___ years
**Direct Plan link**: {Value Research / AMFI direct plan route}
**Monitor quarterly**: {Specific metrics to watch}
**Sell/exit trigger**: {Specific — e.g., 3 consecutive quarters underperforming benchmark by >3%}

### For Portfolio Recommendation

| # | Fund Name | Category | Allocation | Monthly SIP | Expense Ratio | Role |
|---|-----------|----------|-----------|-------------|---------------|------|
| 1 | | Nifty 50 Index | ___% | ₹___ | ~0.1% | Core |
| 2 | | Flexi/Mid Cap | ___% | ₹___ | ~0.7% | Growth |
| 3 | | ELSS | ___% | ₹___ | ~0.8% | Tax + Growth |
| 4 | | Short Duration Debt | ___% | ₹___ | ~0.3% | Stability |
| 5 | | SGB/Gold ETF | ___% | ₹___ | ~0.01% | Hedge |
| 6 | | US Index FOF (optional) | ___% | ₹___ | ~0.5% | Global diversification |
| | **Total** | | **100%** | **₹___** | **Wtd avg: ___%** | |

**Portfolio snapshot**:
- Weighted expense ratio: ___%
- Equity allocation: ___%
- Number of underlying stocks (approx): ___
- Inter-fund overlap: Low / Medium / High
- Benchmark for the equity portion: Nifty 500 or Nifty 50 (depending on mix)

### Index Fund vs Active Fund Decision

| Factor | Index Fund | Active Fund |
|--------|-----------|-------------|
| Expense ratio | 0.1-0.2% | 0.5-1.5% |
| Manager risk | None | Present |
| Alpha potential | Zero (by design) | Positive or negative |
| Best use | Large cap equity | Mid/small cap where active adds value |
| Indian evidence | Large cap: index wins 70%+ of the time | Mid/small: active managers can outperform |
| Decision rule | Default to index for large cap | Only use active if 7Y+ consistent alpha evidence |
