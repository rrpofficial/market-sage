---
name: policy-impact-analyzer
description: |
  Analyzes impact of Indian government policies, Union Budget, RBI monetary policy,
  PLI schemes, regulatory changes, and global macro factors on Indian stock markets
  and specific sectors/stocks.
triggers:
  - budget impact
  - RBI policy impact
  - PLI scheme
  - government policy stocks
  - SEBI regulation
  - GST impact
  - crude oil impact
  - FII DII flows
---

# Policy Impact Analyzer — Government & Macro Analysis

## Activation

When the user asks about how government policies, budget announcements, RBI decisions, or macro events affect markets, sectors, or specific stocks.

## Step 1: Fetch Data

1. **WebSearch**: `"Union Budget {year} key announcements"` or the specific policy
2. **WebSearch**: `"RBI monetary policy {month} {year} rate decision"` for RBI
3. **WebSearch**: `"{Policy name} impact on {sector} stocks India"` for sectoral analysis
4. **WebFetch**: PIB press releases for official policy text
5. **WebSearch**: `"PLI scheme {sector} beneficiaries listed companies"` for PLI
6. **WebSearch**: `"India inflation GDP IIP PMI latest data"` for macro

**Critical**: Use ONLY official sources (PIB, RBI, Ministry of Finance, SEBI) for policy text. News interpretation is secondary — always start with the primary source.

## Step 2: Policy Classification

Classify the policy into:

| Type | Examples | Typical Impact Horizon |
|------|----------|----------------------|
| **Fiscal Policy** | Budget, tax changes, subsidies, capex allocation | 1-3 years |
| **Monetary Policy** | Repo rate, CRR, SLR, liquidity measures | 6-18 months |
| **Industrial Policy** | PLI schemes, Make in India, FDI policy | 3-10 years |
| **Regulatory** | SEBI rules, GST changes, environmental norms | Immediate to 2 years |
| **Trade Policy** | Tariffs, anti-dumping duties, FTAs | 1-5 years |
| **State Government** | State industrial policies, land allocation, incentives | 2-7 years |
| **Global Macro** | US Fed, crude oil, geopolitical events | Variable |

## Step 3: Sectoral Impact Assessment

### 3.1 Direct Impact Analysis

For each affected sector:

| Sector | Impact Type | Magnitude | Timeline | Confidence |
|--------|------------|-----------|----------|------------|
| | Positive/Negative/Neutral | High/Medium/Low | Immediate/1Y/3Y+ | High/Medium/Low |

### 3.2 Impact Chain Analysis

Map the cause-and-effect chain:

```
Policy → First-order effect → Second-order effect → Stock impact

Example:
RBI rate cut (-25bps)
  → Lower borrowing costs for banks
    → NIM pressure short-term, but loan growth increase
      → Banking stocks: Short-term negative (NIM), medium-term positive (growth)
  → Lower EMI for consumers
    → Boost to auto/housing demand
      → Auto/Real estate stocks: Positive in 2-4 quarters
  → Lower deposit rates
    → Savers seek equity/MF
      → Market liquidity: Positive for broader market
```

Always trace at least two levels of impact.

### 3.3 Winners & Losers Table

| Category | Sector/Company | Why | Expected Impact | Timeline |
|----------|---------------|-----|-----------------|----------|
| **Clear Winner** | | | | |
| **Clear Winner** | | | | |
| **Likely Winner** | | | | |
| **Neutral** | | | | |
| **Likely Loser** | | | | |
| **Clear Loser** | | | | |

## Step 4: Specific Policy Frameworks

### 4.1 Union Budget Analysis

Analyze each of these dimensions:

**Tax Changes**:
| Change | Who Benefits | Who Loses | Stocks to Watch |
|--------|-------------|-----------|-----------------|
| Income tax changes | | | Consumer, FMCG, Auto |
| Corporate tax changes | | | Broad market |
| Capital gains tax | | | Market sentiment |
| Customs duty changes | | | Import-dependent vs domestic |
| GST rate changes | | | Sector-specific |
| Excise/Cess changes | | | Tobacco, fuel, luxury |

**Expenditure / Capex**:
| Allocation Area | Amount (₹Cr) | YoY Change | Beneficiary Sectors | Key Stocks |
|----------------|--------------|------------|---------------------|------------|
| Infrastructure | | | Cement, Steel, L&T type | |
| Defence | | | HAL, BEL, defence cos | |
| Railways | | | IRCTC, Titagarh, RVNL type | |
| Agriculture | | | Fertilizer, agri-chem | |
| Healthcare | | | Pharma, hospitals | |
| Education | | | Ed-tech, infra | |
| Digital/IT | | | IT services, data centers | |
| Green Energy | | | Renewable, EV, battery | |

**Subsidies & Schemes**:
| Scheme | Budget | Sector Impact | Specific Beneficiaries |
|--------|--------|---------------|----------------------|
| PM Awas Yojana | | Housing, cement, paint | |
| PLI Schemes | | Manufacturing | |
| MNREGA | | Rural economy | |
| Food subsidy | | FMCG | |

### 4.2 RBI Monetary Policy Analysis

| Parameter | Current | Previous | Change | Market Impact |
|-----------|---------|----------|--------|---------------|
| Repo Rate | | | | |
| Reverse Repo / SDF | | | | |
| CRR | | | | |
| SLR | | | | |
| GDP Growth Forecast | | | | |
| Inflation Forecast | | | | |
| Stance | Accommodation/Neutral/Tightening | | | |

**Sectoral Impact of Rate Changes**:

| Rate Direction | Positive For | Negative For | Neutral |
|---------------|-------------|-------------|---------|
| **Rate Cut** | Banks (loan growth), Auto, Real Estate, NBFCs, Rate-sensitive | Bank NIMs (short-term) | IT, Pharma, FMCG |
| **Rate Hike** | Bank NIMs (short-term), Fixed deposits | Auto, Real Estate, NBFCs, High-debt cos | IT, Pharma, FMCG |
| **Status Quo** | Market stability | — | — |

**Liquidity Impact**:
- CRR cut = more liquidity = positive for credit growth
- CRR hike = tighter liquidity = negative for NBFCs especially
- OMO purchases = liquidity injection
- OMO sales = liquidity absorption

### 4.3 PLI Scheme Analysis

| Sector | PLI Outlay (₹Cr) | Duration | Key Listed Beneficiaries | Revenue Impact (est.) |
|--------|------------------|----------|--------------------------|----------------------|
| Mobile & Electronics | | | Dixon, Amber, etc. | |
| Auto & Components | | | Tata Motors, M&M, etc. | |
| Pharma | | | | |
| Textiles | | | | |
| Food Processing | | | | |
| Semiconductors | | | | |
| Solar PV | | | | |
| White Goods (AC/LED) | | | | |
| Telecom & Networking | | | | |
| Steel | | | | |
| Chemicals | | | | |
| Drones | | | | |

For each PLI beneficiary stock, assess:
- Has the company applied and been approved?
- What % of revenue will PLI incentive represent?
- Are they on track to meet production targets?
- Capex commitment vs balance sheet capacity?

### 4.4 Global Macro Factors

| Factor | Current Level | Trend | Impact on India |
|--------|--------------|-------|-----------------|
| **Crude Oil (Brent)** | $___/bbl | | India imports 85%+ oil. $10↑ = ~₹0.5 impact on CAD |
| **US Fed Funds Rate** | ___% | | Higher US rates → FII outflows from India |
| **US 10Y Treasury** | ___% | | Rising yield → pressure on EM valuations |
| **Dollar Index (DXY)** | ___ | | Strong dollar → Rupee depreciation → IT positive, importers negative |
| **USD/INR** | ₹___ | | Weak rupee → inflation risk, FII losses on currency |
| **FII Flows (Monthly)** | ₹___Cr | | Net sellers = market pressure |
| **DII Flows (Monthly)** | ₹___Cr | | SIP flows providing cushion |
| **China PMI** | ___ | | Weak China → metal price pressure, possible demand shift to India |
| **Gold Price** | ₹___/10g | | Safe haven demand indicator |
| **India VIX** | ___ | | >15 = elevated fear, <12 = complacency |

### 4.5 State Government Policy Analysis

When analyzing state policies:

| Aspect | Detail |
|--------|--------|
| State | |
| Policy/Scheme | |
| Objective | |
| Incentives offered | Tax breaks, land, subsidies, single-window clearance |
| Target sectors | |
| Duration | |
| Listed companies with operations in state | |
| Investment commitments received | |
| Estimated job creation | |
| Competitive position vs other states | |

Key states with active industrial policies: Maharashtra, Gujarat, Tamil Nadu, Karnataka, Telangana, UP, AP, Rajasthan, Odisha, MP

## Step 5: Investment Strategy Based on Policy

### Timing Framework

| Phase | Action | Risk Level |
|-------|--------|------------|
| **Policy announced** | Research, watchlist only | High (market may overreact) |
| **1-3 months post** | Selective accumulation in clear beneficiaries | Medium |
| **6-12 months post** | Assess actual implementation | Lower |
| **Annual review** | Check if policy delivering results | Lowest |

**Warning**: Markets often price in policy impact IMMEDIATELY on announcement. By the time retail investors react, the "easy money" is gone. Focus on:
1. **Second-order effects** that markets miss initially
2. **Implementation plays** — companies that will actually execute
3. **Avoid "concept stocks"** that rise on narrative without fundamentals

### Policy Durability Assessment

| Factor | Score (1-5) |
|--------|------------|
| Cross-party support (will survive govt change?) | |
| Funding adequacy (budget allocated?) | |
| Institutional mechanism (implementing body exists?) | |
| Track record (similar past policies succeeded?) | |
| Private sector interest (companies investing?) | |
| **Total Durability Score** | /25 |

>15 = High durability, invest with conviction
10-15 = Moderate, size positions conservatively
<10 = Low durability, avoid or keep very small positions

## Step 6: Output Format

### For Budget/Policy Analysis

**Policy**: {Name/Description}
**Date**: {Announcement date}
**Overall Market Impact**: Positive / Negative / Neutral
**Impact Magnitude**: High / Medium / Low

**Top 3 Beneficiary Sectors**:
1. {Sector} — {Why} — Key stocks: {List}
2. {Sector} — {Why} — Key stocks: {List}
3. {Sector} — {Why} — Key stocks: {List}

**Top 3 Negatively Impacted**:
1. {Sector} — {Why} — Key stocks: {List}
2. {Sector} — {Why} — Key stocks: {List}
3. {Sector} — {Why} — Key stocks: {List}

**Investment Action Items**:
- Immediate: {What to do now}
- 3-month: {What to research/accumulate}
- 12-month: {What to review}

**What the market is missing**: {Non-obvious second-order effect}

**Risk to thesis**: {What could make this analysis wrong}
