---
name: stock-analyzer
description: |
  Deep fundamental, technical, valuation, and corporate governance analysis of
  individual Indian stocks. Includes IPO evaluation, dividend investing framework,
  and sector-specific analysis for 12+ sectors. Produces structured research reports
  with hard data, peer comparison, and clear BUY/HOLD/AVOID verdicts.
triggers:
  - analyze stock
  - company analysis
  - stock comparison
  - fundamental analysis
  - intrinsic value
  - is stock overvalued
  - corporate governance
  - technical analysis stock
  - IPO analysis
  - dividend stock
  - should I invest in
---

# Stock Analyzer — Deep Equity Research

## Activation

When the user asks about a specific Indian stock, company analysis, IPO evaluation, or dividend stock selection. For stock comparisons, run the framework for each stock and add a comparative section.

## Step 1: Fetch Data (with Fallback Chain)

Before ANY analysis, fetch real data. Use this fallback sequence if a source is blocked or down:

**Primary chain** (try in order until one works):
1. **Screener.in**: WebSearch `"{Company} screener.in"` → WebFetch the URL
2. **Ticker by Finology**: WebSearch `"{Company} ticker finology"` → WebFetch
3. **Trendlyne**: WebSearch `"{Company} trendlyne stock"` → WebFetch
4. **Moneycontrol**: WebSearch `"{Company} moneycontrol stock"` → WebFetch
5. **Tickertape**: WebSearch `"{Company} tickertape"` → WebFetch

**Additional mandatory searches** (run in parallel):
- **Governance**: WebSearch `"{Company} SEBI penalty order site:sebi.gov.in"` + WebSearch `"{Company} promoter pledge NSE"` + WebSearch `"{Company} auditor qualification annual report"`
- **Technical**: WebSearch `"{Company} technical analysis trendlyne"` or `"{Company} technical analysis investing.com"`
- **Operational**: WebSearch `"{Company} tijori finance"` for revenue segments, geographic mix, operational metrics
- **News/Red flags**: WebSearch `"{Company} tax dispute litigation fraud SEBI penalty {current year}"`

**If ALL sources fail**: Present the analysis template with blanks and ask user:
```
I couldn't fetch live data. Please provide from Screener.in ({Company}):
□ Key ratios: ROE, ROCE, P/E, P/B, Debt/Equity
□ 5Y Revenue and Profit CAGR
□ Shareholding: Promoter/FII/DII/MF %, Promoter pledge %
□ Current price, 52-week high/low
□ Last 5 years annual Revenue, PAT, EPS
□ Peer comparison (3-4 peers)
```

## Step 2: Corporate Governance Analysis (DO THIS FIRST)

**This section is NON-NEGOTIABLE and must appear BEFORE financial analysis.** Poor governance invalidates all financial metrics.

### 2.1 Board & Management Structure

| Aspect | Finding | Red Flag? |
|--------|---------|-----------|
| Promoter holding (%) | | <40% is concern |
| Promoter pledge (%) | | >10% is red flag (check NSE pledge data) |
| Pledge trend (3Y) | | Increasing = danger |
| Independent directors (%) | | <33% is non-compliant per SEBI LODR |
| Board diversity | | |
| CEO-Chairman separation | | Combined = concern |
| Auditor name | | Big 4/reputed = positive |
| Auditor tenure | | >10 years or <1 year = flag |
| Auditor changes (5Y) | | >1 change = investigate why |

### 2.2 Corporate Governance Red Flags

Investigate and report on EACH — mark as Clean / Flag / Serious:

| Red Flag Area | Finding | Status |
|---------------|---------|--------|
| **Related party transactions** (arm's length? size vs revenue?) | | |
| **Tax disputes / penalties** (IT, GST, SEBI, sectoral regulators) | | |
| **SEBI actions** (orders, penalties, show-cause — check sebi.gov.in) | | |
| **SCORES complaints** (high complaint volume = governance issue) | | |
| **Auditor qualifications** (qualified opinion, emphasis of matter) | | |
| **Management integrity** (insider trading, front-running, fund diversion) | | |
| **Whistle-blower complaints** (any reported cases?) | | |
| **Promoter criminal cases** (ongoing litigation against promoters?) | | |
| **Succession planning** (family business — is next gen ready?) | | |
| **Executive compensation** (aligned with performance? vs peer ratio) | | |
| **MCA filings** (any charges, director disqualifications — check MCA21) | | |
| **Group company transactions** (opaque holding structures?) | | |

### 2.3 Governance Score

Rate governance: **Strong / Adequate / Weak / Avoid**

If governance is **Weak** or **Avoid**, prominently warn:
> **⚠ GOVERNANCE WARNING**: [Specific issues]. Investors should exercise extreme caution regardless of financial metrics. This alone may be reason to AVOID.

## Step 3: Fundamental Analysis

### 3.1 Business Overview

| Item | Detail |
|------|--------|
| Sector / Industry | |
| Market Cap (₹Cr) & Category | Large (>₹20K Cr) / Mid (₹5K-20K) / Small (<₹5K) |
| Business Model | |
| Revenue Segments | Segment-wise % (fetch from Tijori Finance for granularity) |
| Geographic Mix | Domestic vs Export % |
| Key Customers/Clients | Concentration risk? |
| Competitive Position | Leader / Challenger / Niche |
| Economic Moat | Wide / Narrow / None |
| Moat Source | Brand / Cost / Network / Switching / Regulatory / Intangible |

### 3.2 Profitability Metrics

| Metric | Current | 3Y Avg | 5Y Avg | 10Y Avg | Sector Median | Assessment |
|--------|---------|--------|--------|---------|---------------|------------|
| ROE (%) | | | | | | |
| ROCE (%) | | | | | | |
| Operating Margin (%) | | | | | | |
| Net Profit Margin (%) | | | | | | |
| Free Cash Flow Yield (%) | | | | | | |

**Assessment criteria**:
- ROE: >15% Good, >20% Excellent, <10% Poor
- ROCE: >18% Good, >25% Excellent, <12% Poor
- Margins: Compare with sector median. Expanding = positive, contracting = negative

### 3.3 Growth Metrics

| Metric | 3Y CAGR | 5Y CAGR | 10Y CAGR | TTM YoY | Assessment |
|--------|---------|---------|----------|---------|------------|
| Revenue | | | | | |
| Operating Profit | | | | | |
| Net Profit | | | | | |
| EPS | | | | | |

**Growth quality check**:
- Is profit growing faster than revenue? (Operating leverage = positive)
- Is EPS growth tracking profit growth? (No excessive dilution)
- Is growth organic or acquisition-driven?
- Is growth consistent or lumpy? (Calculate coefficient of variation if data available)

### 3.4 Financial Health

| Metric | Value | Safe Range | Assessment |
|--------|-------|------------|------------|
| Debt/Equity | | <1 | |
| Interest Coverage | | >3 | |
| Current Ratio | | 1.5-3 | |
| Cash & Equivalents (₹Cr) | | | |
| CFO / Net Profit | | >1 (quality check) | |
| Capex / CFO | | <60% | |
| Dividend Payout (%) | | | |
| Net Debt / EBITDA | | <3 | |
| Working Capital Days | | Improving/Deteriorating | |

**Cash flow quality** (critical — accounting profits can be faked, cash flow is harder to fake):
- CFO consistently > Net Profit = HIGH quality earnings
- CFO consistently < Net Profit = INVESTIGATE (aggressive revenue recognition, stuffing channels, working capital bloat)
- Negative FCF for 3+ years despite profits = Capex-heavy or cash-burning business

### 3.5 Shareholding Pattern & Trends

| Holder | Current % | QoQ Change | YoY Change | Trend |
|--------|-----------|------------|------------|-------|
| Promoter | | | | |
| FII | | | | |
| DII | | | | |
| Mutual Funds | | | | |
| Retail | | | | |

**Key signals**:
- Promoter buying = strong confidence signal
- Promoter selling = investigate why (tax planning = benign, distress = alarming)
- FII increasing = institutional validation of India thesis
- MF increasing = domestic institutional interest
- Retail increasing while institutions exit = potential distribution phase (bearish)
- Check bulk/block deals on NSE for large transactions

## Step 4: Valuation Analysis

### 4.1 Relative Valuation

| Metric | Current | 5Y Median | 10Y Median | Sector Median | Assessment |
|--------|---------|-----------|------------|---------------|------------|
| P/E (TTM) | | | | | |
| P/E (Forward est.) | | | | | |
| P/B | | | | | |
| EV/EBITDA | | | | | |
| P/S | | | | | |
| PEG Ratio | | | | | |
| Dividend Yield (%) | | | | | |

### 4.2 Intrinsic Value Estimation

Calculate using multiple methods and triangulate:

**Method 1: DCF (Discounted Cash Flow)**
- Free Cash Flow (latest): ₹___ Cr
- Growth rate assumption: ___% (use 5Y FCF CAGR, cap at 15%)
- Terminal growth: 5% (India nominal GDP growth)
- Discount rate (WACC): 12-14% for India (risk-free ~7% + equity risk premium ~6%)
- Intrinsic value per share: ₹___
- Show the math step by step

**Method 2: Earnings-Based (PE Method)**
- Normalized EPS (3Y avg): ₹___
- Fair PE (based on growth + quality + sector): ___x
- Intrinsic value: ₹___

**Method 3: Graham Number**
- Formula: √(22.5 × EPS × Book Value per share)
- Graham Number: ₹___
- Note: Best suited for stable, asset-heavy businesses

**Method 4: Reverse DCF**
- At current market price of ₹___, what growth rate is priced in?
- Market-implied growth: ___%
- Is this reasonable vs historical 5Y/10Y growth? Yes/No
- If market expects >20% growth for >10 years, valuation is likely stretched

### 4.3 Valuation Verdict

| Method | Intrinsic Value | Current Price | Upside/Downside | Margin of Safety |
|--------|----------------|---------------|-----------------|------------------|
| DCF | ₹___ | ₹___ | ___% | ___% |
| PE-based | ₹___ | ₹___ | ___% | ___% |
| Graham | ₹___ | ₹___ | ___% | ___% |
| Reverse DCF implied growth | ___% | Historical: ___% | Reasonable? | |

**Overall**: Undervalued / Fairly Valued / Overvalued
- Margin of safety 25%+ = BUY zone
- 0-25% margin = HOLD / accumulate on dips
- Negative margin (overvalued) = AVOID new entry

## Step 5: Technical Analysis

### 5.1 Trend Analysis

| Indicator | Value | Signal |
|-----------|-------|--------|
| Current Price | ₹___ | |
| 20-DMA | ₹___ | Above/Below (short-term trend) |
| 50-DMA | ₹___ | Above/Below (medium-term) |
| 200-DMA | ₹___ | Above/Below (long-term trend) |
| 50 vs 200 DMA | | Golden Cross / Death Cross / Neutral |
| 52-Week High | ₹___ | __% from high |
| 52-Week Low | ₹___ | __% from low |
| Price position in 52W range | | Upper / Middle / Lower third |

### 5.2 Momentum Indicators

| Indicator | Value | Signal | Interpretation |
|-----------|-------|--------|----------------|
| RSI (14-day) | | | >70 Overbought, <30 Oversold, 40-60 Neutral |
| MACD Line | | | Above/Below signal line |
| MACD Histogram | | | Expanding (strengthening) / Contracting (weakening) |
| ADX (14-day) | | | >25 Strong trend, <20 Rangebound |
| Stochastic %K/%D | | | >80 Overbought, <20 Oversold |
| Bollinger Band position | | | Upper band / Middle / Lower band |

### 5.3 Volume Analysis

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Avg Daily Volume (20D) | | |
| Avg Daily Volume (50D) | | |
| Volume trend vs 20D avg | | Higher volume = conviction behind move |
| Delivery % (recent sessions) | | >50% = genuine buying, <30% = speculative |
| OI change (if F&O stock) | | Rising OI + rising price = bullish; Rising OI + falling price = bearish |

### 5.4 Support & Resistance Levels

| Level Type | Price (₹) | Basis |
|------------|-----------|-------|
| Resistance 3 | | (52W high / previous peak) |
| Resistance 2 | | (recent swing high) |
| Resistance 1 | | (nearest overhead level) |
| **Current Price** | **₹___** | |
| Support 1 | | (nearest floor) |
| Support 2 | | (200 DMA / recent swing low) |
| Support 3 | | (52W low / major historical support) |

Sources: Previous swing highs/lows, moving averages, round numbers, volume profile zones.

### 5.5 Chart Patterns (if identifiable)

Note any visible patterns from Trendlyne/Chartink/Investing.com:
- Head & Shoulders / Inverse H&S
- Double Top / Double Bottom
- Cup & Handle
- Triangle (ascending/descending/symmetrical)
- Flag / Pennant / Wedge
- Channel (ascending/descending/horizontal)

**If chart pattern data is not available via web sources**: "Chart pattern analysis requires visual review. Check TradingView (tradingview.com) or Chartink (chartink.com) for pattern scans."

### 5.6 Technical Verdict

| Timeframe | Signal | Confidence |
|-----------|--------|------------|
| Short-term (1-4 weeks) | Bullish/Bearish/Neutral | High/Med/Low |
| Medium-term (1-6 months) | Bullish/Bearish/Neutral | |
| Long-term (6-12 months) | Bullish/Bearish/Neutral | |

**Important**: Technical analysis is SECONDARY to fundamental analysis for long-term investors. Use technicals for:
- Entry/exit timing (not stock selection)
- Identifying accumulation (smart money buying) vs distribution (smart money selling)
- Confirming or contradicting fundamental thesis

## Step 6: Peer Comparison

| Metric | **{Stock}** | Peer 1 | Peer 2 | Peer 3 | Sector Avg |
|--------|-------------|--------|--------|--------|------------|
| Market Cap (₹Cr) | | | | | |
| Revenue (₹Cr) | | | | | |
| Net Profit (₹Cr) | | | | | |
| ROE (%) | | | | | |
| ROCE (%) | | | | | |
| OPM (%) | | | | | |
| P/E | | | | | |
| P/B | | | | | |
| EV/EBITDA | | | | | |
| Debt/Equity | | | | | |
| Promoter (%) | | | | | |
| 5Y Revenue CAGR | | | | | |
| 5Y Profit CAGR | | | | | |
| Dividend Yield | | | | | |
| **Best in class?** | **Y/N** | | | | |

## Step 7: Risk Assessment

### Quantified Risks

| Risk | Probability | Impact | Mitigation for Investor |
|------|-------------|--------|------------------------|
| Sector downturn | H/M/L | | Diversify across sectors |
| Regulatory change | | | Monitor policy news |
| Competition intensifying | | | Check market share trend |
| Management/Governance risk | | | Track promoter actions |
| Valuation overstretch | | | Don't buy above fair value |
| Concentration (single client/product) | | | Check revenue segment split |
| Currency/Export risk | | | Hedge or accept |
| Technology disruption | | | Check R&D spend, adaptability |
| Debt/Liquidity crisis | | | Monitor D/E and interest coverage |
| Key person risk | | | Succession plan? |

### Scenario Analysis
- **Bull Case**: What goes right → Upside ___% over ___ years
- **Base Case**: Most likely → Return ___% over ___ years
- **Bear Case**: What goes wrong → Downside ___% risk

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

**Score interpretation**: >7.5 = Strong BUY, 6-7.5 = BUY/HOLD, 4.5-6 = HOLD, <4.5 = AVOID

### Recommendation

**Verdict**: BUY / HOLD / AVOID / SELL
**Suitable for**: Conservative / Moderate / Aggressive investors
**Investment Horizon**: Minimum ___ years
**Max allocation**: ___% of equity portfolio
**Entry strategy**: Lumpsum at ₹___ / SIP / Wait for dip to ₹___

### What to Monitor
- **Quarterly**: Revenue growth, margin trend, debt changes, order book (if applicable)
- **Annually**: Annual report governance section, auditor report, capex plans
- **Event-based**: [Triggers that would change thesis — e.g., regulatory change, management exit, debt spike]

---

## IPO Analysis Framework

### Activation
When user asks about an upcoming or recently listed IPO.

### Step 1: Fetch IPO Data
1. WebSearch `"{Company} IPO analysis {year}"` — for prospectus highlights
2. WebSearch `"{Company} DRHP SEBI"` — for Draft Red Herring Prospectus
3. WebSearch `"{Company} IPO grey market premium"` — to note GMP but DO NOT use it for recommendation
4. WebSearch `"{Company} IPO peer comparison listed peers"` — for valuation benchmark

### Step 2: IPO Evaluation Table

| Parameter | Detail | Assessment |
|-----------|--------|------------|
| **Company** | | |
| **Issue Size** | ₹___ Cr | |
| **Price Band** | ₹___ - ₹___ | |
| **Fresh Issue vs OFS** | Fresh: ₹___Cr / OFS: ₹___Cr | Fresh = growth capex; OFS = promoter exit |
| **Fresh Issue %** | ___% | >50% fresh = positive (company raising capital for growth) |
| **OFS %** | ___% | High OFS = promoter/PE cashing out = cautious |
| **Use of Proceeds** | | Growth capex = good; Debt repayment = okay; PE exit = cautious |
| **Promoter Holding Pre-IPO** | ___% | |
| **Promoter Holding Post-IPO** | ___% | Significant dilution = concern |
| **PE/VC Investors** | | Reputed PE = positive signal |
| **PE/VC Entry Price** | ₹___ per share (approx) | Compare with IPO price = markup |
| **Lock-in Period** | ___ months for promoter, ___ for anchor | Post-lockup selling pressure risk |

### Step 3: Financial Check (Same as fundamental analysis but focus on)

| Metric | FY-3 | FY-2 | FY-1 | Latest Period | Trend |
|--------|------|------|------|---------------|-------|
| Revenue (₹Cr) | | | | | Growing? |
| PAT (₹Cr) | | | | | Profitable? |
| ROE (%) | | | | | Consistent >15%? |
| Debt/Equity | | | | | Improving? |
| CFO (₹Cr) | | | | | Positive? |

**IPO-specific red flags**:
- [ ] Company only recently turned profitable (1-2 years)
- [ ] Revenue/profit spike in IPO year (window-dressed?)
- [ ] Negative operating cash flow despite profits
- [ ] High debt being repaid with IPO proceeds (not growth capex)
- [ ] Numerous related party transactions in DRHP
- [ ] Litigation/regulatory issues disclosed in risk factors
- [ ] Key customer concentration (>30% revenue from one client)
- [ ] No clear competitive moat

### Step 4: Valuation vs Listed Peers

| Metric | IPO Price | Peer 1 | Peer 2 | Peer 3 | Assessment |
|--------|-----------|--------|--------|--------|------------|
| P/E at IPO price | | | | | Premium/Discount |
| P/B at IPO price | | | | | |
| EV/EBITDA | | | | | |
| P/S | | | | | |
| ROE (%) | | | | | Justifies premium? |
| Growth (%) | | | | | Higher growth = some premium okay |

**Valuation verdict**:
- IPO priced at significant premium to peers WITHOUT superior growth/ROE = AVOID
- IPO priced at par or discount to peers WITH comparable metrics = SUBSCRIBE
- IPO priced at premium WITH demonstrably better growth/moat = CONSIDER

### Step 5: IPO Recommendation

**Verdict**: SUBSCRIBE / AVOID / SUBSCRIBE (only for long-term)

**Key reason**: {1-2 sentences}

**GMP warning**: Grey market premium reflects speculative demand, NOT fundamental value. A high GMP does not mean the stock is worth it long-term. Never base investment decisions on GMP.

**Post-listing strategy**:
- If subscribing for listing gains: High risk, not recommended
- If subscribing for long-term: Hold through initial volatility, review at 6-month mark
- If avoiding IPO: Add to watchlist, consider buying post-listing after price discovery (usually 3-6 months)

---

## Dividend Investing Framework

### Activation
When user asks about dividend stocks, income investing, or building a dividend portfolio.

### Dividend Stock Evaluation

| Metric | Value | Threshold | Assessment |
|--------|-------|-----------|------------|
| Dividend Yield (%) | | >1.5% (meaningful) | |
| Dividend Yield vs 5Y avg | | At/above avg = attractive entry | |
| Dividend Growth (5Y CAGR) | | >8% = growing dividend | |
| Payout Ratio (%) | | 20-60% sustainable; >80% unsustainable | |
| Consecutive Years of Dividend | | >10 years = reliable | |
| Ever Cut/Skipped Dividend? | | If yes, investigate when and why | |
| FCF Payout Ratio (Div/FCF) | | <70% safe; >100% funded by debt = danger | |
| Special Dividends (history) | | Positive signal if regular | |
| Buyback History | | Alternative to dividend, tax-efficient | |

### Dividend Sustainability Check

The most important question: **Can the company CONTINUE paying and GROWING its dividend?**

| Factor | Assessment |
|--------|------------|
| Revenue stability (cyclical or stable?) | |
| Margin consistency (±5% or volatile?) | |
| Debt level (high debt + high dividend = risky) | |
| Capex needs (high capex = less free cash for dividends) | |
| Industry structure (regulated utilities stable, cyclicals risky) | |
| Promoter intent (history of shareholder-friendly actions) | |

### Dividend Tax Consideration
- Dividends taxed at slab rate (up to 30% + cess for highest bracket)
- For high-bracket investors: Buyback may be more tax-efficient than dividend
- Compare post-tax dividend yield with debt fund yields to assess true attractiveness

### Best Sectors for Dividend Investing in India
1. **IT Services**: High cash generation, low capex, regular dividends + buybacks (TCS, Infosys, HCL Tech)
2. **FMCG**: Stable cash flows, moderate payout (HUL, ITC, Nestle, Dabur)
3. **Power Utilities**: Regulated returns, high payout (Power Grid, NTPC, NHPC)
4. **Coal/Mining**: PSU with government mandated payout (Coal India)
5. **Oil & Gas PSUs**: High dividend but cyclical (ONGC, IOC, BPCL)

**Avoid for pure dividend**: Banks (need to retain capital), small caps (need to reinvest), high-growth (should reinvest rather than distribute)

---

## Stock Comparison Framework

When comparing 2+ stocks:

1. **Side-by-side table** of all key metrics (profitability, growth, valuation, governance, technicals)
2. **Winner in each dimension** with reason
3. **Overall recommendation**: Which stock for which investor type
4. **Portfolio suggestion**: Can both be held? Or pick one? Overlap risk?

---

## Sector-Specific Analysis Frameworks

### Banking & NBFC

**Replace standard metrics with**:

| Metric | Value | Good Range | Assessment |
|--------|-------|------------|------------|
| NIM (%) | | >3% for banks, >4% for NBFCs | |
| GNPA (%) | | <2% | |
| NNPA (%) | | <1% | |
| PCR (%) | | >70% | |
| CASA Ratio (%) | | >40% (for banks) | |
| Credit Cost (%) | | <1% | |
| CAR (%) | | >12% (well above RBI min) | |
| RoA (%) | | >1% for banks, >2% for NBFCs | |
| Credit Growth (%) | | >15% | |
| Slippage Ratio (%) | | <2% | |
| Cost-to-Income (%) | | <45% efficient | |

**Valuation**: P/B and P/Adjusted Book primary. P/E secondary. Book value growth = key driver.

### IT Services

| Metric | Value | Good Range |
|--------|-------|------------|
| Revenue per Employee | | >₹30L |
| Attrition (LTM %) | | <15% |
| Large Deal TCV (₹Cr) | | Growing QoQ/YoY |
| Client Concentration (Top 5 %) | | <25% |
| USD Revenue Growth (CC %) | | >10% |
| EBIT Margin (%) | | >20% |
| Digital Revenue (%) | | >50% and growing |
| Fresher to Lateral Ratio | | Higher fresher = margin expansion |

**Valuation**: P/E and EV/EBITDA primary. P/B less relevant. Revenue growth in constant currency is the key driver.

### Pharma & Healthcare

| Metric | Value | Notes |
|--------|-------|-------|
| ANDA Pipeline (for US generics) | | Larger pipeline = more opportunities |
| USFDA Observations / Warning Letters | | ANY warning letter = major red flag |
| API vs Formulation Mix (%) | | Formulation = higher margin |
| R&D Spend (% of revenue) | | >6% for innovation-led, >3% for generics |
| US Revenue (%) | | Concentration risk if >50% |
| CRAMS/CDMO Revenue (%) | | Growing = secular tailwind |
| Biosimilar Pipeline | | Future growth driver |

**Regulatory risk is paramount**: A single FDA warning can wipe 20-30% market cap. Always check FDA import alerts.

### Real Estate

| Metric | Value | Notes |
|--------|-------|-------|
| Pre-sales (₹Cr, QoQ/YoY) | | Leading indicator of revenue |
| Collections (₹Cr) | | Cash flow proxy |
| Net Debt/Equity | | <0.5 preferred |
| Launch Pipeline (mn sq ft) | | Growth visibility |
| Land Bank (years of development) | | Revenue visibility |
| Realizations (₹/sq ft) | | Improving = pricing power |
| Completed Inventory (unsold) | | High unsold = demand concern |

**Valuation**: NAV-based (land bank + ongoing projects) more relevant than P/E. P/E often misleading due to revenue recognition timing.

### Capital Goods / Infrastructure / EPC

| Metric | Value | Notes |
|--------|-------|-------|
| Order Book (₹Cr) | | >2.5x revenue = strong visibility |
| Book-to-Bill Ratio | | >1 = order inflow > execution |
| Order Inflow Growth (YoY %) | | >15% |
| Execution Rate (QoQ revenue trend) | | Consistent improvement |
| Working Capital Days | | <90 good, >120 concern (capital locked up) |
| Retention Money / Claims Pending | | Large claims = cash flow risk |

### FMCG

| Metric | Value | Notes |
|--------|-------|-------|
| Volume Growth (%) | | More important than value growth |
| Rural vs Urban Mix (%) | | Rural recovery = growth catalyst |
| Distribution Reach (outlets) | | Wider = stronger moat |
| Brand Portfolio Strength | | Multiple ₹1000Cr brands = diversified |
| New Product Revenue (%) | | Innovation pipeline |
| Market Share Trend | | Gaining or losing? |

Premium valuation is normal for FMCG. Focus on growth sustainability, not absolute P/E.

### Metals & Mining (Cyclical)

| Metric | Value | Notes |
|--------|-------|-------|
| EV/EBITDA (through-cycle avg) | | Use mid-cycle, not peak EBITDA |
| Cost Curve Position | | Bottom quartile = survives downturns |
| Reserve Life (years) | | >15 years |
| Commodity Price Sensitivity | | Model: 10% price change → ___% EBITDA impact |
| Capacity Utilization (%) | | >85% = pricing power |
| Net Debt/EBITDA | | <2 at cycle peak (stress test at cycle trough) |

**Critical**: NEVER value metals at cycle-peak earnings. Use normalized/mid-cycle EV/EBITDA.

### Utilities / Power

| Metric | Value | Notes |
|--------|-------|-------|
| Regulated Equity Base (₹Cr) | | Drives regulated RoE |
| Allowed RoE (%) | | Per CERC/SERC norms |
| Capacity Utilization / PLF (%) | | >70% for thermal, track for renewable |
| PPA Mix (Long-term vs Merchant %) | | Long-term PPA = revenue stability |
| Fuel Cost Pass-through | | Full pass-through = margin safety |
| Capex Pipeline (₹Cr) | | Growth visibility for regulated cos |
| Renewable Capacity (MW) | | Transition readiness |

### Insurance

| Metric | Value | Good Range | Notes |
|--------|-------|------------|-------|
| **Embedded Value (EV) per share** | ₹___ | | Key intrinsic value metric |
| **P/EV ratio** | | <2.5x for life, <1.5x for general | Primary valuation metric |
| **VNB (Value of New Business)** | ₹___Cr | Growing | Profitability of new policies sold |
| **VNB Margin (%)** | | >25% life, >15% general | Higher = better product mix |
| **APE (Annualized Premium Equivalent)** | ₹___Cr | Growing | Sales volume metric |
| **Persistency Ratio 13th/61st month** | | >85% / >55% | Customer retention |
| **Combined Ratio (General Insurance)** | | <100% (underwriting profit) | >105% = underwriting losses |
| **Solvency Ratio** | | >1.5x (IRDAI min) | Capital adequacy |
| **Claims Settlement Ratio** | | >95% | Customer trust |
| **Investment Income Yield** | | | Float returns matter |

**Valuation**: Use P/EV (Price to Embedded Value) and VNB growth, NOT P/E. P/E is misleading for insurance due to reserve changes.

### Oil & Gas / Refineries

| Metric | Value | Notes |
|--------|-------|-------|
| **GRM (Gross Refining Margin)** ($/bbl) | | >$5 = healthy; benchmark: Singapore GRM |
| **Throughput (MMTPA)** | | Utilization of refining capacity |
| **Marketing Margin (₹/liter)** | | Government-influenced for PSUs |
| **Upstream Realization ($/bbl)** | | Linked to global crude prices |
| **Gas Production (MMSCMD)** | | Domestic vs imported mix |
| **Petchem Revenue (%)** | | Integration = better margins |
| **Debt/Equity** | | CapEx-heavy sector, <1.5 preferred |
| **Subsidy/Under-recovery Exposure** | | PSU-specific risk (ONGC, IOC) |

**Key driver**: Crude oil price sensitivity — model impact of $10/bbl change on EBITDA.

### Telecom

| Metric | Value | Notes |
|--------|-------|-------|
| **ARPU (₹/month)** | | >₹200 and rising = positive |
| **ARPU Growth (QoQ/YoY %)** | | Tariff hikes = direct ARPU uplift |
| **Subscriber Base (Mn)** | | Market share trend |
| **Active Subscriber % ** | | >75% preferred |
| **Net Subscriber Additions (Mn/Q)** | | Positive = share gains |
| **Data Usage per Sub (GB/month)** | | Rising = upselling opportunity |
| **EBITDA Margin (%)** | | >50% for scaled players |
| **Net Debt/EBITDA** | | <3.5x; spectrum liabilities huge |
| **Capex/Revenue (%)** | | 5G cycle drives capex, will normalize |
| **Spectrum Liability (₹Cr)** | | Check deferred payment schedule |
| **Tower Count / Sharing Ratio** | | Sharing = cost optimization |

**Valuation**: EV/EBITDA primary (high debt makes P/E misleading). EV/Subscriber for relative valuation. ARPU trajectory is THE key metric.

### Hotels / Aviation / Travel

| Metric | Value | Notes |
|--------|-------|-------|
| **RevPAR (Revenue Per Available Room)** (Hotels) | ₹___ | Key profitability driver |
| **Occupancy Rate (%)** (Hotels) | | >65% breakeven for most |
| **ARR (Average Room Rate)** (Hotels) | ₹___ | Pricing power indicator |
| **Load Factor (%)** (Aviation) | | >80% profitable |
| **Yield per RPK (₹)** (Aviation) | | Revenue quality |
| **CASK (Cost per ASK) ex-fuel** (Aviation) | ₹___ | Cost efficiency |
| **Fleet Size & Orders** (Aviation) | | Growth visibility |
| **Net Debt / EBITDA** | | Both sectors capital-intensive |
| **Domestic vs International Mix** | | International = higher yield |

**Aviation warning**: Indian aviation has destroyed more capital than it has created. Only invest in airlines with structural cost advantages. Hotels are generally better businesses than airlines.

### Defence & Aerospace

**Macro context before any defence stock analysis** — always fetch:
1. WebSearch `"India defence budget {current year} capital expenditure allocation"` — for budget allocation trend
2. WebSearch `"India defence indigenisation negative import list {current year}"` — for import substitution pipeline
3. WebSearch `"India defence exports target MoD {current year}"` — for export growth story
4. WebSearch `"{Company} defence order book Ministry of Defence"` — for company-specific order wins

**Structural tailwinds to assess**:
- India's defence budget as % of GDP (target ~2.5%) and capital expenditure share (target 25%+)
- Negative Import List (items banned from import = mandatory domestic sourcing) — more items added = larger addressable market for Indian cos
- Defence exports target (₹50,000 Cr by FY29) — export-eligible companies command premium
- Atmanirbhar Bharat in defence (DRDO technology transfer, joint ventures with foreign OEMs)
- Geopolitical context: India's border tensions, defence modernisation urgency, NATO alignment shift

**Company-level metrics**:

| Metric | Value | Notes |
|--------|-------|-------|
| **Order Book (₹Cr)** | | Pipeline of confirmed orders |
| **Order Book / Revenue ratio** | | >5x = exceptional visibility; >3x = strong |
| **Order Inflow (YoY growth %)** | | Leading indicator of future revenue |
| **Order Execution Rate (%)** | | Revenue / Opening order book = execution pace |
| **MoD-linked revenue (%)** | | Govt dependency — stable but can be slow-paying |
| **Export Revenue (%)** | | Diversification; export contracts = better margins |
| **DRDO-approved products** | Count | More certified products = broader addressable market |
| **Foreign OEM JV / ToT (Transfer of Technology)** | | Higher-value, more complex products |
| **R&D spend (% of revenue)** | | >5% signals genuine technology builder vs assembler |
| **Working Capital Days** | | Govt receivables inflate WC; >180 days = caution |
| **Indigenisation %** | | % of components sourced from India = strategic moat |
| **EBIT Margin (%)** | | 15-25% range for quality defence players |
| **Advance-to-Contract ratio** | | Govt advances reduce working capital pressure |
| **Maintenance/Service revenue (%)** | | Recurring = higher quality revenue |

**Valuation considerations for defence**:

| Aspect | Notes |
|--------|-------|
| **Premium P/E justified?** | Yes — long order visibility, policy tailwind, strategic sector. But current Indian defence stocks often trade 40-80x P/E which is extreme. |
| **Use EV/EBITDA** | More reliable than P/E when working capital is inflated by govt receivables |
| **Order book discounting** | Discount order book by execution risk, govt budget revisions, payment delays |
| **Reverse DCF** | At current price, what growth is priced in? If >25% for 10 years, risk of disappointment is high |
| **Execution risk** | Defence projects face delays (technology complexity, trials, approvals). Revenue recognition can lag order wins by 2-5 years |

**Defence red flags** (specific to sector):
- [ ] Order book heavily concentrated in 1-2 platforms (single programme risk)
- [ ] Promoter is a PSU (HAL, BEL, GRSE, MDL) — good order visibility but bureaucratic, lower ROE
- [ ] Very high government receivables (>6 months revenue) — cash flow stress
- [ ] No independent R&D — pure assembler/integrator = low moat, margin squeeze risk
- [ ] R&D spend <2% of revenue — technology dependent on foreign/DRDO with no proprietary IP
- [ ] Order inflow growth has stalled for 2+ quarters despite strong policy narrative
- [ ] Valuation > 50x P/E without demonstrated earnings scale (speculative premium)
- [ ] No export revenue or pipeline — purely domestic = single-customer risk

**Order Execution Queue Analysis** (critical — order book headline hides execution reality):

The order book number tells you *how much* is contracted. This section tells you *whether it will actually convert to revenue on time*.

| Metric | Value | Notes |
|--------|-------|-------|
| **Order book age profile** | | What % of orders are >3 years old? Old, unexecuted orders = execution concern |
| **Revenue from orders won this year vs 3Y ago** | | Are old orders converting or stalling? |
| **Delivery milestones met (last 3 years)** | Count on-time vs delayed | Most important execution metric |
| **Programme-wise execution stage** | | Map each major programme: order → development → trials → production → delivery |
| **Trials pending (number of platforms)** | | Trials can take 1-5 years; revenue recognition only after acceptance |
| **User acceptance delays** | | Indian Armed Forces acceptance trials are notoriously slow |
| **Cost overruns vs contract value** | | Fixed-price contracts mean overruns eat the company's margin, not customer's |
| **Contract modifications / amendments** | | Frequent amendments = scope creep, execution complexity |
| **Advance utilisation rate** | | Government advances consumed vs % of order delivered — lag = inefficiency |
| **Receivables days (defence-specific)** | | >180 days = government is slow-paying or project is disputed |
| **Arbitration / disputes pending** | | Unresolved disputes with MoD = revenue recognition risk |

Fetch: WebSearch `"{Company} order execution delay defence ministry"` + `"{Company} delivery milestone acceptance trial"`

**Execution Track Record** (history predicts future):

| Question | Finding | Implication |
|----------|---------|-------------|
| Has the company ever missed a major delivery deadline? | | One-off or pattern? |
| Any contract cancellation by MoD in last 10 years? | | Cancellation = catastrophic for financials |
| Any penalty/liquidated damages (LD) clauses invoked by MoD? | | LD clauses can be 0.5-1% of contract value per week |
| How long did the company's last major platform take from order to first delivery? | | Benchmark against contracted timeline |
| Has R&D-led product development met DRDO qualification deadlines? | | Technology programmes routinely run 2-5 years late |
| What is the gap between order inflow and revenue recognition? | | <2 years = execution-capable; >4 years = chronic execution lag |
| Revenue CAGR vs order inflow CAGR (last 5 years) | | If orders grow 30% but revenue grows 10%, orders aren't converting |

**Competitive Landscape Analysis**:

This is essential — many investors assume defence PSUs have permanent moats. That is increasingly wrong.

| Competitive Force | Detail to Investigate |
|-------------------|-----------------------|
| **PSU vs Private sector dynamics** | Private players (L&T, Bharat Forge, Tata Advanced Systems, Mahindra Defence) are increasingly winning contracts once reserved for PSUs. PSUs have cost and scale advantages; privates have agility and R&D investment. Check: is this company losing market share to private players? |
| **DPSU reform pressure** | Defence PSUs face "corporatisation" pressure and performance benchmarking. HAL, BEL must now compete on price, not just allocation. Track: MoD's DPSU performance ratings and policy direction. |
| **Foreign OEM competition** | Despite Atmanirbhar push, some platforms still procure via imports (jets, submarines, helicopters). For every import purchase, a domestic player lost. Check: what % of this company's addressable market is still being imported? |
| **Foreign OEM partnership quality** | Is the company partnering with tier-1 OEMs (Lockheed, Safran, Airbus, Rheinmetall) or tier-2/3 suppliers? Tier-1 partnerships = technology transfer + export potential; tier-2 = lower value-add assembly |
| **Make I vs Make II vs Buy (Indian)** | Government contract categories affect who can bid. Make I (govt funded) = usually PSUs. Make II (industry funded) = open to private. Buy (Indian IDDM) = open competition. Track what % of addressable orders are open to private players. |
| **Offset obligations** | Foreign OEM offset obligations (mandatory investment in Indian defence) are creating new private sector entrants. These new entrants become future competitors. |
| **SME / MSME threat** | Government is mandating 25% of defence procurement from MSMEs. This fragments addressable market and reduces large-order concentration for listed mid-caps. |
| **New entrant threat** | Who received a defence industrial licence in last 3 years? New entrants may not matter today but matter in 5 years. |
| **Export competition** | In global export markets, Indian companies compete with established players from Russia, France, USA, Israel, South Korea. Check: which geographies is this company targeting and who are the incumbents? |

**Competitive Position Verdict**:

| Dimension | This Company | Status |
|-----------|-------------|--------|
| PSU or Private | | PSUs have govt protection; privates have agility |
| Unique technology / sole-source platform | | Sole-source = moat; competitive tender = margin pressure |
| Market share trend (last 3 years) | | Gaining / Stable / Losing |
| Private sector challengers in core product | | Named competitors + their growth |
| Foreign competition in addressable market | | % of market open to imports |
| Export market presence | | Nil / Early-stage / Established |
| Pricing power | | Cost-plus (regulated) / Competitive tender |

**Indian Defence Ecosystem — categories to be aware of** (for peer context):

| Category | Key Players (examples — verify independently) | Moat Type |
|----------|----------------------------------------------|-----------|
| **Platform OEM** (aircraft, ships, missiles) | HAL, Mazagon Dock, Garden Reach, Cochin Shipyard | Govt-backed monopoly / duopoly |
| **Electronics & Systems** | Bharat Electronics (BEL), Data Patterns, Astra Microwave | Technology IP, govt DPSU status |
| **Munitions & Explosives** | Solar Industries, Premier Explosives | Explosives license = high barrier |
| **Precision Components** | MTAR Technologies, Paras Defence, Dynamatic | Niche tech, aerospace-grade manufacturing |
| **Optics & Sensors** | Zen Technologies, Bharat Dynamics | Defence electronics, simulation |
| **Diversified with Defence division** | Bharat Forge, L&T Defence, Tata Advanced Systems | Scale + engineering strength |

**Valuation reality check for Indian defence stocks**:
Many Indian defence stocks trade at extreme valuations (50-100x P/E) pricing in decade-long perfect execution. Apply reverse DCF rigorously — if the market-implied growth rate requires >20% revenue CAGR for 10 consecutive years with expanding margins, the stock is pricing in near-perfection. Any execution delay, budget cut, or technology failure creates significant downside. The combination of: (a) long order-to-revenue cycles, (b) chronic execution delays in Indian defence programmes, and (c) rising private sector competition means the headline order book overstates near-term earnings power far more than in any other sector. **Don't confuse a great sector with a great stock at any price.**

---

## Worked Example: TCS (Tata Consultancy Services)

Below is a **condensed example** showing the expected output format. In real analysis, every number would be fetched live.

### Corporate Governance: **Strong**
- Promoter (Tata Sons): ~72%, zero pledge, stable for 10+ years
- Board: Independent chairman (post-Tata governance reforms), diverse board, 50%+ independent directors
- Auditor: Deloitte (Big 4), consistent
- No SEBI penalties, clean SCORES record, no material litigation
- Succession: Smooth CEO transitions historically (Chandra → Gopinathan → Muthuswamy)
- Related party: Tata group transactions at arm's length, disclosed, audited

### Quick Scorecard

| Dimension | Metric | Value (Illustrative) | Signal |
|-----------|--------|---------------------|--------|
| Valuation | P/E | ~28x | Fair for quality (5Y median ~28x) |
| Profitability | ROE 3Y avg | ~47% | Excellent (capital-light) |
| Profitability | OPM | ~25% | Strong |
| Growth | Revenue 5Y CAGR | ~12% (INR) | Moderate |
| Health | Debt/Equity | ~0 | Fortress balance sheet |
| Ownership | Promoter | ~72% | Rock solid |
| Technical | vs 200 DMA | Assume near/above | Neutral-to-positive |

### Valuation
- P/E ~28x on TTM EPS. 5Y median also ~28x → **Fairly valued**
- DCF (12% discount, 12% growth, 5% terminal) → ₹___ per share
- Reverse DCF: Market pricing in ~14% growth → reasonable vs 12% historical

### Verdict: **HOLD** (Score: 7.2/10)
- Outstanding business quality, governance, capital allocation
- Fairly valued — not a bargain at current levels
- **BUY on dips**: If price drops 15-20% below fair value (to P/E ~24x)
- Suitable for: All investor types as a core IT holding (max 8-10% of portfolio)
- Monitor: Deal wins, attrition, BFSI client spend, USD/INR, US recession risk

*This example illustrates the expected depth and critical tone. Note that governance came first, numbers are specific, and the verdict is honest ("not a bargain") rather than cheerful.*
