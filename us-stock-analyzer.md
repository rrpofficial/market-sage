---
name: us-stock-analyzer
description: |
  Deep fundamental, technical, valuation, and governance analysis of US equities
  (NYSE, NASDAQ, AMEX). Covers SEC-filing governance checks, SaaS/tech metrics,
  biopharma pipeline analysis, REIT evaluation, US IPO (S-1) review, and sector-
  specific frameworks for 10+ major US sectors. Produces structured research
  reports with hard data, peer comparison, and clear BUY/HOLD/AVOID verdicts.
  All data fetched live from Yahoo Finance, SEC EDGAR, Macrotrends, Morningstar.
triggers:
  - US stock analysis
  - analyze AAPL MSFT GOOGL AMZN NVDA META TSLA
  - NYSE NASDAQ stock
  - S&P 500 stock
  - US company fundamental analysis
  - US stock valuation
  - US IPO analysis
  - American stock analysis
  - SEC filing analysis
  - US corporate governance
---

# US Stock Analyzer — Deep US Equity Research

---

## ⛔ DATA INTEGRITY PRE-FLIGHT CHECK — RUN BEFORE EVERY ANALYSIS

**Before writing a single financial figure**, complete this check:

| Check | Condition | Action |
|-------|-----------|--------|
| 1. Web tools available? | YES → proceed to Step 1 | NO → tell user, present data checklist |
| 2. Did fetch return data? | YES → use it, cite source + date | NO → mark `[FETCH REQUIRED — verify at {URL}]` |
| 3. About to write a number from training memory? | ANY CASE → **STOP. Delete it. Fetch it first.** | No exceptions. |

**Forbidden sources**: LLM training knowledge, cached reasoning, "I recall...", "approximately...", "as of my last update...".
**Required sources**: WebSearch + WebFetch returning live data from Yahoo Finance, SEC EDGAR, Macrotrends, Morningstar, or equivalent portals.

Applies to: stock prices, P/E, P/B, EV/EBITDA, revenue, net income, EPS, FCF, ROE, ROIC, margins, debt, insider ownership %, analyst targets, and every other quantitative figure.

---

## Activation

When the user asks about a specific US stock, company, or US IPO. For comparisons, run this framework for each and add a comparative section.

## Step 1: Fetch Data (US Fallback Chain)

Before ANY analysis, fetch live data. Use this sequence if a source is blocked:

**Primary chain** (try in order):
1. **ms-us-quotes**: `uv run --project ~/.claude/market-sage-tools ms-us-quotes TICKER --pretty` — live price, P/E, forward P/E, EV/EBITDA, margins, ROE, analyst target in one call
2. **Yahoo Finance web**: WebSearch `"{Company} site:finance.yahoo.com"` → WebFetch for stats
3. **Macrotrends**: WebSearch `"{Company} macrotrends revenue net income"` → WebFetch for 10-year history
4. **Morningstar**: WebSearch `"{Company} morningstar stock analysis"` → WebFetch
5. **Simply Wall St**: WebSearch `"{Company} simply wall st analysis"` → WebFetch

**Always fetch separately**:
- **SEC Governance**: WebSearch `"{Company} SEC 10-K proxy DEF 14A insider trading"` + WebFetch `https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&company=&CIK={TICKER}&type=DEF+14A`
- **Form 4 insiders**: WebSearch `"{Company} Form 4 insider buying selling SEC"` → check for recent insider activity
- **SEC enforcement**: WebSearch `"{Company} SEC enforcement investigation penalty"` + WebSearch `"{Company} class action lawsuit securities fraud"`
- **Short interest**: WebSearch `"{Company} short interest FINRA short ratio"` or check ms-us-quotes `short_ratio` and `short_pct_of_float` fields
- **Analyst consensus**: WebSearch `"{Company} analyst consensus price target Wall Street"`
- **Technical**: `uv run --project ~/.claude/market-sage-tools ms-us-technicals TICKER --pretty`

**If ALL sources fail**: Do NOT fill any figures from LLM training knowledge:
```
I couldn't fetch live data. I will not use training data for US financial figures — those are stale.

Please paste the following from Yahoo Finance or Macrotrends for {Company}:
□ Current price, 52-week high/low
□ P/E (TTM), Forward P/E, EV/EBITDA, P/B, P/FCF
□ Revenue, net income, EPS (last 5 years)
□ Gross margin, operating margin, net margin (TTM)
□ ROE, ROIC, ROA
□ Debt/Equity, Current Ratio, Interest Coverage
□ FCF (last 3 years)
□ Insider ownership %, institutional ownership %
□ Short interest ratio
```

## Step 2: Corporate Governance Analysis (DO THIS FIRST)

**Non-negotiable — poor governance invalidates financial metrics.**

### 2.1 Ownership Structure

| Aspect | Finding | Signal |
|--------|---------|--------|
| Insider ownership (%) | | <1% = low alignment; >10% = strong alignment |
| Institutional ownership (%) | | >70% = institutions in control |
| Top 5 institutional holders | | Concentrated = activist risk |
| Short interest (% of float) | | >20% = significant bearish bet |
| Short ratio (days to cover) | | >10 = potential short squeeze |
| Dual-class shares? | | If YES — minority shareholders have limited voting power |
| Founder-led? | | Founder-CEO often = long-term orientation |
| Activist investors present? | | Could be catalyst or distraction |

**Fetch via**: SEC 13F filings (institutional), Form 4 (insider transactions), SEC 13G/13D (>5% owners)

### 2.2 Board & Management Quality

| Aspect | Finding | Signal |
|--------|---------|--------|
| Board size | | 7-12 optimal |
| Independent directors (%) | | NYSE/NASDAQ require majority independent |
| CEO-Chairman separation | | Combined = governance concern |
| Board diversity | | Skills and backgrounds |
| CEO tenure | | New CEO (<2 years) = transition risk |
| CEO total compensation vs peers | | Misaligned pay = governance risk |
| CEO pay ratio (CEO/median employee) | | >500x = excessive without commensurate performance |
| CFO tenure | | Frequent CFO changes = red flag |
| Auditor | | Big 4 (Deloitte/EY/PwC/KPMG) preferred |
| Auditor tenure | | >20 years for same partner = independence risk |
| Restatements (last 5 years) | | Any restatement = serious flag |

**Source**: DEF 14A (proxy statement) — search EDGAR for the latest proxy.

### 2.3 SEC Governance Red Flags

| Red Flag | Finding | Status |
|----------|---------|--------|
| SEC investigation / Wells notice | | Clean/Flagged — check SEC EDGAR EDGAR enforcement |
| Securities class action lawsuits | | Clean/Flagged |
| Accounting irregularities / restatements | | Clean/Flagged |
| Related party transactions (proxy statement) | | Arm's length? Material? |
| Executive option backdating history | | Historical check |
| Whistleblower reports / DOJ/FTC investigation | | Clean/Flagged |
| Short-seller attacks (Hindenburg, Muddy Waters) | | Any credible short reports? |
| Going concern audit opinion | | Serious — company may not survive |
| SOX 302/906 certification issues | | CEO/CFO signed off on controls? |
| Material weaknesses in internal controls | | 10-K disclosure — any material weaknesses? |

### 2.4 Capital Allocation Quality

| Aspect | Finding | Signal |
|--------|---------|--------|
| Share buyback history ($ and dilution trend) | | Buybacks at low prices = shareholder-friendly; at peak = destroys value |
| Dividend history and growth | | >10 consecutive years = dividend aristocrat |
| M&A track record | | Acquisitions at fair prices? Integration success? |
| Capex vs FCF (Capex/FCF ratio) | | >100% = heavy investment cycle |
| Return on invested capital (ROIC) vs WACC | | ROIC > WACC = value creation; ROIC < WACC = value destruction |

### 2.5 Governance Score: **Strong / Adequate / Weak / Avoid**

If **Weak** or **Avoid**, display prominently:
> **⚠ GOVERNANCE WARNING**: [Specific issues]. Consider avoiding regardless of financial metrics.

## Step 3: Fundamental Analysis

### 3.1 Business Overview

| Item | Detail |
|------|--------|
| GICS Sector / Industry | |
| Market Cap ($B) & Category | Mega (>$200B) / Large ($10-200B) / Mid ($2-10B) / Small ($0.3-2B) / Micro (<$0.3B) |
| Business Model | |
| Revenue Segments (%) | Breakdown by product/geography |
| Geographic Mix | US vs International % |
| Key Customers / Concentration Risk | Any customer >10% of revenue? |
| Competitive Position | Leader / Challenger / Niche |
| Economic Moat | Wide / Narrow / None |
| Moat Source | Brand / Network Effect / Switching Cost / Cost Advantage / Intangible / Regulatory |

### 3.2 Profitability Metrics

| Metric | Current (TTM) | 3Y Avg | 5Y Avg | Industry Median | Assessment |
|--------|---------------|--------|--------|-----------------|------------|
| Gross Margin (%) | | | | | |
| Operating Margin (%) | | | | | |
| Net Profit Margin (%) | | | | | |
| EBITDA Margin (%) | | | | | |
| FCF Margin (%) | | | | | |
| ROE (%) | | | | | |
| ROA (%) | | | | | |
| ROIC (%) | | | | | |

**Assessment benchmarks** (US context):
- Gross margin: >50% = software/services quality; <20% = commodity/distribution
- Operating margin: >25% = excellent; >15% = good; <5% = thin
- ROE: >20% = excellent; >15% = good; <10% = poor
- ROIC > WACC (8-12% for most US companies) = value-creating business

### 3.3 Growth Metrics

| Metric | 1Y (YoY) | 3Y CAGR | 5Y CAGR | 10Y CAGR | Assessment |
|--------|----------|---------|---------|----------|------------|
| Revenue | | | | | |
| Gross Profit | | | | | |
| Operating Income | | | | | |
| Net Income | | | | | |
| EPS (diluted) | | | | | |
| FCF | | | | | |

**Growth quality check**:
- Revenue growing but margins shrinking → investigate (investment phase vs structural problem)
- EPS growing faster than revenue → operating leverage (positive)
- EPS growing slower than revenue → dilution from stock-based comp (common in US tech — quantify)
- FCF consistently > net income → high earnings quality

### 3.4 Financial Health

| Metric | Value | Benchmark | Assessment |
|--------|-------|-----------|------------|
| Total Debt / Equity | | <1 conservative | |
| Net Debt / EBITDA | | <2 safe; <3 acceptable | |
| Interest Coverage Ratio | | >5 safe | |
| Current Ratio | | 1.5-3 | |
| Quick Ratio | | >1 | |
| Cash & Equivalents ($B) | | | |
| Free Cash Flow ($B, TTM) | | | |
| FCF / Net Income ratio | | >1 = quality earnings | |
| CapEx / Operating CF | | | |

**Cash flow quality** (critical — FCF is harder to manipulate than GAAP income):
- FCF consistently ≥ Net Income = HIGH quality (non-cash charges exceed capex, or light-asset model)
- FCF persistently < Net Income = INVESTIGATE (working capital buildup, aggressive revenue recognition)
- Negative FCF + positive net income for 3+ years = SERIOUS RED FLAG in mature companies

**Stock-based compensation (SBC) — US-specific**:
- SBC is a real cost in the US tech sector. Always compute:
  - SBC as % of revenue
  - FCF adjusted for SBC (GAAP FCF minus SBC = true owner earnings)
  - Diluted share count trend (increasing = shareholder dilution)

### 3.5 Shareholding & Institutional Activity

| Holder | % | Recent Change | Signal |
|--------|---|---------------|--------|
| Insiders total | | | Buying = bullish signal |
| Top institutional (13F) | | | Berkshire, Sequoia, Baupost buying = validation |
| ETF / Index funds | | | Passive ownership floor |
| Short interest | | | Rising = increasing bearish conviction |

**Key signals**:
- Large insider purchase (Form 4) = management buying at current price = strong conviction
- Multiple insiders selling simultaneously = distribution signal (could be tax planning or concern)
- Activist investor (13D) = potential catalyst for change
- Short interest >20% + declining price = high conviction short thesis — investigate credibility

## Step 4: Valuation Analysis

### 4.1 Relative Valuation

| Metric | Current | 5Y Median | 10Y Median | Sector Median | Assessment |
|--------|---------|-----------|------------|---------------|------------|
| P/E (TTM) | | | | | |
| Forward P/E | | | | | |
| PEG Ratio | | | | | |
| EV/EBITDA | | | | | |
| EV/Revenue | | | | | |
| P/FCF (Price/FCF per share) | | | | | |
| P/B | | | | | |
| Dividend Yield (%) | | | | | |

**PEG interpretation**: PEG < 1 = potentially undervalued; PEG > 2 = expensive relative to growth

### 4.2 Intrinsic Value — US Parameters

**US WACC inputs** (different from India):
- Risk-free rate: US 10-year Treasury yield (~4.2-4.5% range — **fetch current rate** from FRED: WebSearch `"US 10 year treasury yield today"`)
- Equity risk premium: ~5-5.5% (US ERP; lower than India's ~6-8%)
- Typical US WACC range: **8-12%** (vs 12-14% for India)
- Terminal growth: **2-3%** (US nominal GDP growth; vs 5% for India)

**Method 1: DCF**
```
ms-dcf --symbol {TICKER} --price {PRICE} --fcf {FCF_MILLIONS_÷10} --growth {GROWTH%}
       --discount {WACC} --terminal {TERMINAL_GROWTH} --shares {SHARES_MILLIONS÷10}
```
Note: ms-dcf uses ₹Cr units by convention — for USD, pass values directly in the same units (e.g., FCF in $M as if it were ₹Cr — the math is identical since DCF is unit-agnostic).

**Method 2: EV/EBITDA Approach**
- Fetch EBITDA and sector median EV/EBITDA multiple
- Intrinsic EV = EBITDA × fair multiple
- Intrinsic equity value = EV - Net Debt
- Per-share value = Intrinsic equity / shares outstanding

**Method 3: P/FCF Approach**
- FCF per share (TTM)
- Fair P/FCF multiple for sector and quality
- Intrinsic value = FCF/share × fair multiple

**Method 4: Reverse DCF**
```
ms-dcf --symbol {TICKER} --price {PRICE} --fcf {FCF} --growth 0 --shares {SHARES} --reverse-only
```
At current market price, what growth rate is priced in? If implied growth > 25% for 10 years, extreme expectations are built in.

### 4.3 Valuation Verdict Table

| Method | Intrinsic Value ($) | Current Price ($) | Upside/Downside | MoS |
|--------|---------------------|-------------------|-----------------|-----|
| DCF | | | | |
| EV/EBITDA | | | | |
| P/FCF | | | | |
| Reverse DCF implied growth | ___% | Historical: ___% | Reasonable? | |

**Overall**: Undervalued / Fairly Valued / Overvalued
- MoS ≥ 25% = BUY zone
- MoS 0-25% = HOLD / accumulate on dips
- Negative MoS = AVOID new entry

## Step 5: Technical Analysis

Run `ms-us-technicals TICKER --pretty` for live indicator values.

### 5.1 Trend Analysis

| Indicator | Value ($) | Signal |
|-----------|-----------|--------|
| Current Price | | |
| 20-DMA | | Above/Below |
| 50-DMA | | Above/Below |
| 200-DMA | | Above/Below |
| 50 vs 200 DMA | | Golden/Death Cross |
| 52-Week High | | ___% from high |
| 52-Week Low | | ___% from low |

### 5.2 Momentum Indicators

| Indicator | Value | Signal |
|-----------|-------|--------|
| RSI (14) | | >70 overbought, <30 oversold |
| MACD Histogram | | Positive = bullish momentum |
| Bollinger Band position | | Upper/Middle/Lower band |
| ATR (14) — volatility | | |

### 5.3 Volume & Market Microstructure

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Avg Daily Volume (20D) | | |
| Volume vs 20D avg | | Higher = conviction |
| Short Interest (Days to Cover) | | >10 = squeeze potential |
| Options Market (Put/Call ratio) | | >1.2 = bearish; <0.7 = bullish |

### 5.4 Technical Verdict

| Timeframe | Signal | Confidence |
|-----------|--------|------------|
| Short-term (1-4 weeks) | Bullish/Bearish/Neutral | |
| Medium-term (1-6 months) | | |
| Long-term (6-12 months) | | |

## Step 6: Peer Comparison

| Metric | **{Stock}** | Peer 1 | Peer 2 | Peer 3 | Sector Avg |
|--------|-------------|--------|--------|--------|------------|
| Market Cap ($B) | | | | | |
| Revenue ($B, TTM) | | | | | |
| Revenue Growth (1Y %) | | | | | |
| Gross Margin (%) | | | | | |
| Operating Margin (%) | | | | | |
| Net Margin (%) | | | | | |
| FCF Margin (%) | | | | | |
| ROE (%) | | | | | |
| ROIC (%) | | | | | |
| P/E (TTM) | | | | | |
| Forward P/E | | | | | |
| EV/EBITDA | | | | | |
| P/FCF | | | | | |
| Net Debt / EBITDA | | | | | |
| Insider ownership (%) | | | | | |
| Short interest (%) | | | | | |
| **Best in class?** | **Y/N** | | | | |

## Step 7: Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Regulatory / antitrust (FTC, DOJ) | H/M/L | | |
| Competition intensifying | | | |
| Revenue concentration risk | | | |
| Macro / recession sensitivity | | | |
| Interest rate sensitivity | | | |
| Valuation re-rating risk | | | |
| Technology disruption | | | |
| Key person / management risk | | | |
| FX risk (if international revenues) | | | |
| Debt / refinancing risk | | | |
| Sector-specific regulatory changes | | | |

**Scenario Analysis**:
- Bull case: What goes right → Upside ___% over ___ years
- Base case: Most likely → Return ___% over ___ years
- Bear case: What goes wrong → Downside ___% risk

## Step 8: Final Verdict

### Summary Scorecard

| Dimension | Score (1-10) | Weight | Weighted |
|-----------|-------------|--------|----------|
| Business Quality & Moat | | 20% | |
| Financial Strength | | 15% | |
| Growth Prospects | | 20% | |
| Valuation | | 20% | |
| Corporate Governance | | 15% | |
| Technical Setup | | 10% | |
| **Total** | | **100%** | **/10** |

**Score**: >7.5 = Strong BUY, 6-7.5 = BUY/HOLD, 4.5-6 = HOLD, <4.5 = AVOID

### Recommendation

**Verdict**: BUY / HOLD / AVOID / SELL
**Suitable for**: Conservative / Moderate / Aggressive
**Investment Horizon**: Minimum ___ years
**Max allocation**: ___% of equity portfolio
**Entry strategy**: Lumpsum at $___/ DCA / Wait for dip to $___

### What to Monitor
- **Quarterly**: Revenue growth, margins, FCF, share repurchases, guidance
- **Annually**: 10-K SEC filing (full audit), proxy (board/pay), capex plans
- **Event-based**: [What would change the thesis]

---

## US IPO Analysis Framework

### Activation
When user asks about a US IPO, direct listing, or SPAC merger.

### Step 1: Fetch IPO Data
1. WebSearch `"{Company} S-1 prospectus SEC IPO"` → WebFetch EDGAR S-1/S-11
2. WebSearch `"{Company} IPO underwriters roadshow"` → Goldman, Morgan Stanley, etc.
3. WebSearch `"{Company} IPO valuation peer comparison"` → analyst write-ups
4. WebSearch `"{Company} IPO lock-up period expiry date"`

### Step 2: IPO Structure Evaluation

| Parameter | Detail | Assessment |
|-----------|--------|------------|
| Issue type | Traditional IPO / Direct Listing / SPAC | SPAC = higher governance risk historically |
| Total proceeds ($M) | | |
| Primary vs secondary | Primary ($M for company) / Secondary ($M for sellers) | High secondary = insiders exiting |
| Primary % | | >50% fresh = company investing in growth |
| Use of proceeds | Growth capex / Debt repayment / Working capital / PE exit | Growth capex = best |
| Pre-IPO investors | VC/PE firms, average entry price vs IPO price | High markup = insiders cashing out |
| Lock-up period | Days | Selling pressure risk at lock-up expiry |
| Underwriters | | Tier 1 (Goldman, Morgan Stanley, JPMorgan) = better diligence |
| IPO price range | $___ - $___ | |
| Post-IPO float (%) | | Low float = high volatility |

### Step 3: IPO-Specific Red Flags
- [ ] Company only recently profitable (last 1-2 years)
- [ ] Revenue/profit spike in IPO year (window-dressing)
- [ ] Negative FCF despite profitability claims
- [ ] SPAC merger (historically poor post-merger performance as a category)
- [ ] Multiple class shares with low public shareholder voting rights
- [ ] Heavy related party transactions in S-1 risk factors
- [ ] Key customer >25% of revenue — concentration risk
- [ ] No clear moat or path to profitability for pre-revenue companies
- [ ] Aggressive TAM claims with no addressable market evidence

### Step 4: IPO Valuation vs Peers

| Metric | IPO Price | Peer 1 | Peer 2 | Assessment |
|--------|-----------|--------|--------|------------|
| EV/Revenue (NTM) | | | | |
| P/E (if profitable) | | | | |
| EV/EBITDA (if profitable) | | | | |
| Revenue growth (%) | | | | Better growth can justify premium |
| Gross margin (%) | | | | |

### Step 5: IPO Recommendation
**Verdict**: SUBSCRIBE / AVOID / WAIT FOR LOCK-UP EXPIRY

**Post-IPO strategy**:
- For listing day gains: High risk, historically IPOs underperform after first-day pop
- For long-term: Consider buying 3-6 months post-IPO after price discovery and lock-up expiry
- Watch for: lock-up expiry date (Day 180) — selling pressure from early investors

---

## Sector-Specific Analysis Frameworks

### Technology / Software / SaaS

**Core SaaS metrics** (fetch from earnings release, investor deck, or SEC 10-Q):

| Metric | Value | Good Range | Notes |
|--------|-------|------------|-------|
| **Annual Recurring Revenue (ARR)** | $___M | Growing >20% | Leading revenue indicator |
| **ARR Growth Rate (YoY %)** | | >30% for high-growth | Key growth metric |
| **Net Revenue Retention (NRR)** | ___% | >120% = excellent; >100% = expanding | Existing customers expanding |
| **Gross Revenue Retention** | ___% | >90% | Customers NOT leaving |
| **Customer Acquisition Cost (CAC)** | $___ | Declining = efficiency | Cost to acquire one customer |
| **Lifetime Value (LTV)** | $___ | LTV/CAC > 3x | Value of a customer relationship |
| **LTV/CAC Ratio** | | >3x sustainable, >5x excellent | |
| **CAC Payback Period (months)** | | <18 months = efficient | |
| **Magic Number** | | >1 = efficient growth | (NNQ growth / Previous Q S&M spend) |
| **Rule of 40** | | >40% healthy | Revenue growth % + FCF margin % |
| **Gross Margin (%)** | | >70% for SaaS | Software cost structure |
| **SBC as % of Revenue** | | <15% prudent | Real dilution cost |
| **Churn Rate (Monthly)** | | <2% monthly is acceptable | |

**Valuation for SaaS**:
- EV/NTM Revenue is the primary metric (not P/E) for high-growth, pre-profit SaaS
- Rule of 40 score + revenue growth multiple framework:
  - Rule of 40 >50 + growing >30% = 10-20x NTM Revenue is defensible
  - Rule of 40 25-40 + growing 15-25% = 5-10x NTM Revenue
  - Rule of 40 <25 = value framework applies

### Healthcare & Biopharma

**This sector requires special handling — clinical-stage companies have binary outcomes.**

| Metric | Value | Notes |
|--------|-------|-------|
| **Pipeline stage breakdown** | Phase 1/2/3/NDA/Approved | Map every major programme |
| **Lead asset PDUFA date** | | FDA decision deadline — mark as event risk |
| **FDA approval probability by stage** | ~8% P1 / ~15% P2 / ~60% P3 / ~85% NDA | Historical industry averages |
| **Patent expiry (lead products)** | | Patent cliff = revenue drop |
| **Royalty / licensing revenue (%)** | | Recurring quality revenue |
| **Cash runway (quarters)** | | Pre-revenue biotech lives on cash; <4Q runway = equity raise risk |
| **FDA designations** | | Fast Track / Breakthrough Therapy / RMAT = accelerated path |
| **PDUFA action dates** | | Key binary events — position size accordingly |
| **Competitor approvals pending** | | Head-to-head competition risk |

**For pre-revenue biotech**: Never use P/E or EV/Revenue multiples. Use:
- Pipeline risk-adjusted NPV (rNPV)
- Cash burn rate and runway analysis
- Probability-weighted option value of pipeline assets

**FDA regulatory risk is paramount**: A Complete Response Letter (CRL) or clinical hold can wipe 40-70% market cap in one day.

### Financials — US Banks & Insurance

| Metric (Banks) | Value | Good Range |
|----------------|-------|------------|
| **Net Interest Margin (NIM %)** | | >3% good |
| **Non-Performing Loans (NPL %)** | | <1% |
| **Efficiency Ratio** | | <50% excellent; <60% good |
| **Tier 1 Capital Ratio (%)** | | >10% (Fed minimum 6%) |
| **Loan Loss Reserves / NPLs** | | >100% = well-reserved |
| **ROA (%)** | | >1.2% excellent; >0.8% good |
| **ROE (%)** | | >12% good; >15% excellent |
| **Return on Tangible Common Equity (ROTCE %)** | | >15% excellent |
| **Deposit Growth (YoY %)** | | |
| **Cost of Deposits (%)** | | Rising deposits costs = NIM pressure |
| **Loan Growth (YoY %)** | | |
| **CRE Concentration (% of loans)** | | >300% of capital = Fed scrutiny |
| **Net Charge-Off Rate (%)** | | <0.5% good |
| **DSCR on loan book** | | |

**Valuation for banks**: P/Tangible Book Value (P/TBV) primary. P/E secondary. Price/Pre-Provision Net Revenue (PPNR) for through-cycle analysis.

### Real Estate Investment Trusts (REITs)

| Metric | Value | Notes |
|--------|-------|-------|
| **FFO (Funds from Operations) per share** | $___  | Key earnings metric for REITs — add back depreciation to net income |
| **AFFO (Adjusted FFO) per share** | $___ | FFO minus maintenance capex — best proxy for distributable cash |
| **P/FFO ratio** | | vs REIT category average |
| **Dividend Yield (%)** | | REITs must distribute 90% of taxable income |
| **Dividend Coverage (AFFO / Dividend)** | | >1.1x = safe; >1.3x = well-covered |
| **Occupancy Rate (%)** | | >90% good |
| **Same-Store NOI Growth (%)** | | Organic growth quality metric |
| **Weighted Avg Lease Expiry (WALE, years)** | | Longer = more stable |
| **Debt / Total Assets** | | <40% conservative |
| **Net Debt / EBITDA** | | <6x for diversified REITs |
| **Fixed Charge Coverage** | | >2x |
| **NAV per share** | $___ | Compare market price vs NAV — premium or discount? |
| **Cap Rate (%)** | | Going-in yield on property portfolio; vs current risk-free rate |

**REIT subtypes require different frameworks**: Office / Retail / Industrial / Residential / Data Center / Healthcare / Hotel — each has different cycle dynamics.

### Energy — US E&P, Midstream, Integrated

| Metric (E&P) | Value | Notes |
|--------------|-------|-------|
| **Proved Reserves (BOE, millions)** | | PUD vs PD split |
| **Reserve Replacement Ratio (%)** | | >100% = growing reserves |
| **Reserve Life Index (years)** | | Production / Proved reserves |
| **Finding & Development Costs ($/BOE)** | | Lower = more profitable |
| **Break-even oil price ($/bbl)** | | Vs current WTI/Brent |
| **Production growth (YoY %)** | | |
| **Hedged volumes (%)** | | Locked-in cash flow certainty |
| **Debt / EBITDAX** | | <2x conservative; <3.5x manageable |
| **FCF at current prices** | | |
| **Shareholder returns (buyback + dividend yield)** | | |

**For Midstream**: Fee-based vs commodity-exposed revenue split. Distributable Cash Flow (DCF) is the key metric. Coverage ratio (DCF / distribution). Debt / EBITDA.

### Consumer Discretionary / Retail

| Metric | Value | Notes |
|--------|-------|-------|
| **Same-store sales growth (SSS %)** | | Organic growth, removes new store noise |
| **E-commerce % of revenue** | | Omnichannel trend |
| **Gross margin trend** | | Pricing power indicator |
| **Inventory turnover** | | Higher = less capital tied up |
| **Days Inventory Outstanding (DIO)** | | Rising = demand concern |
| **Net promoter score / brand sentiment** | | |
| **Average Revenue Per User (ARPU)** | | For membership/subscription models |
| **Store count growth** | | New unit economics |

### Industrials / Aerospace & Defense

| Metric | Value | Notes |
|--------|-------|-------|
| **Book-to-bill ratio** | | >1 = orders exceeding shipments |
| **Backlog ($B)** | | Revenue visibility |
| **Organic revenue growth (%)** | | Ex-acquisitions |
| **Operating leverage** | | % margin expansion per 1% revenue growth |
| **Free Cash Flow conversion (FCF/Net Income)** | | Defense typically >80% |
| **DoD budget exposure (%)** | | Government customer concentration risk |
| **Export / ITAR-restricted programs** | | International growth opportunity |

---

## US Tax Reference (verify current rates)

Before citing tax rates, WebSearch `"US capital gains tax rates {current year}"` to confirm:

| Transaction | Holding | Tax Rate (2025 rates — verify) |
|-------------|---------|-------------------------------|
| Long-term capital gains | >1 year | 0% / 15% / 20% based on income |
| Short-term capital gains | <1 year | Ordinary income rate (up to 37%) |
| Qualified dividends | Any | 0% / 15% / 20% (same as LTCG) |
| Non-qualified dividends | Any | Ordinary income rate |
| REIT dividends | Any | Mostly ordinary income (special treatment) |
| Net Investment Income Tax | Any | +3.8% for high earners (MAGI >$200K/$250K) |

**Tax efficiency note**: Holding US stocks in tax-advantaged accounts (401k, IRA, Roth IRA) eliminates capital gains and dividend tax. Recommend asset location planning.

---
