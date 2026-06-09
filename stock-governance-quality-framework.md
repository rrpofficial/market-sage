---
name: stock-governance-quality-framework
description: |
  Forensic accounting and governance quality framework for Indian equities based on
  Howard Schilit's Financial Shenanigans and Thornton O'Glove's Quality of Earnings.
  Detects early-warning signals of earnings manipulation, cash flow misdirection, key
  metric distortion, and governance deterioration. Produces a structured Manipulation
  Risk Score (MRS) — Red/Amber/Green — with source-cited evidence for every flag.
triggers:
  - governance quality analysis
  - forensic accounting
  - earnings quality
  - accounting manipulation
  - financial shenanigans
  - red flags analysis
  - cash flow quality
  - related party transactions
  - auditor resignation
  - contingent liabilities
  - DSO analysis
  - earnings manipulation check
  - quality of earnings
  - corporate fraud indicators
---

# Stock Governance & Quality Framework
### Forensic Accounting Screen — Based on Schilit's *Financial Shenanigans* & O'Glove's *Quality of Earnings*

---

## ⛔ DATA INTEGRITY MANDATE — IDENTICAL TO ALL MARKET SAGE SKILLS

Every number in this framework **must be fetched live** from source filings, annual reports, NSE/BSE disclosures, or financial databases. No figure may come from LLM training memory. All tables must cite source + date. Blank fields show `[FETCH REQUIRED — verify at {URL}]`.

---

## Activation

Invoke this framework when:

1. The user explicitly asks for a **governance deep-dive**, **forensic accounting check**, **earnings quality screen**, or **red flag analysis**.
2. The `stock-analyzer.md` Step 2 governance check returns **Weak** or **Avoid** — escalate to this full forensic screen.
3. The user is evaluating a company with any of: rapid revenue growth, acquisition-heavy strategy, promoter pledge, opaque related party disclosures, or a mid-term auditor change.
4. Any IPO where DRHP reveals unusual financial patterns (revenue spike in pre-IPO year, CWIP build-up, large RPTs).

**This framework EXTENDS the `stock-analyzer.md` Step 2 governance section.** When invoked, this framework's output replaces and supersedes Section 2 of that skill with a far deeper forensic analysis.

---

## Step GQ-0: Pre-flight Data Gathering

### Run `ms-forensic` First (Sections 1 + 2 automated)

**Before any manual data gathering**, invoke the Python CLI tool that automates all quantitative checks in Sections 1 and 2:

```bash
uv run --project ~/.claude/market-sage-tools ms-forensic {SYMBOL} --years 5 --pretty
```

This tool fetches live Screener.in data and pre-computes:

| Auto-computed check | Threshold applied |
|---------------------|------------------|
| 1.1 DSO-to-Revenue divergence (per year) | DSO growing >15pp faster than revenue → Amber; >20pp or DSO up + revenue flat → Red |
| 1.3 DIO-Gross Margin decoupling (per year) | DIO +20% YoY while margin holds → Amber; DIO +30% YoY + margin expands + revenue declining → Red |
| 1.4 CWIP aging (% of fixed assets) | CWIP >25% → Amber; CWIP >35% or 3+ consecutive growth years → Red |
| 2.1 Annual CFO/PAT + rolling 3Y CFO/PAT | Annual <0.8 for 2+ years → Amber; Rolling 3Y <0.8 → Red (O'Glove rule); CFO negative while PAT positive → Red |
| 2.2 DPO inflation (per year) | DPO +20% YoY → Amber; DPO +30% YoY → Red |

The tool outputs a **preliminary MRS** (🟢/🟡/🟠/🔴) for the quantitative checks and lists exactly which manual checks remain for Sections 1.2, 2.3, 3.x, and all of Section 4.

After reviewing the `ms-forensic` output, continue with manual data gathering only for the sections not covered by the tool.

---

Before running any forensic checks, gather at minimum **5 years** of financial data from these sources:

**Primary fetch sequence (run in parallel):**

1. **`ms-forensic` tool** (above — covers Sections 1.1, 1.3, 1.4, 2.1, 2.2 automatically)
2. **Screener.in**: `screener.in/company/{SYMBOL}/consolidated/` — 10-year P&L, Balance Sheet, Cash Flow Statement
2. **Annual Report PDFs** (last 2-3 years): `WebSearch "{Company} annual report {FY} PDF site:bseindia.com OR site:nseindia.com"`
3. **NSE Filings**: `WebSearch "{Company} NSE auditor change resignation announcement"` + `"{Company} NSE pledge data promoter"`
4. **BSE Corporate Announcements**: `bseindia.com/corporates/ann.html` — search for auditor resignation letters, board resolutions
5. **MCA21**: `WebSearch "{Company} MCA charges director disqualification"` — charges, form CHG-1
6. **SEBI Orders**: `WebSearch "{Company} SEBI enforcement order penalty adjudication site:sebi.gov.in"`

**Critical data points required:**

| Data Point | Source | Used In |
|-----------|--------|---------|
| Accounts Receivable (5Y) | Screener.in Balance Sheet | DSO trend |
| Revenue (5Y) | Screener.in P&L | DSO, unbilled ratio |
| Inventory (5Y) | Screener.in Balance Sheet | DIO trend |
| COGS / Material costs (5Y) | Screener.in P&L | DIO trend |
| Gross Margin (5Y) | Screener.in P&L | DIO-Margin decoupling |
| Net Profit (5Y) | Screener.in P&L | CFO divergence |
| Cash Flow from Operations (5Y) | Screener.in Cash Flow | CFO quality |
| CapEx (5Y) | Screener.in Cash Flow | Capitalization check |
| Capital Work-in-Progress (CWIP) (5Y) | Screener.in Balance Sheet | CWIP aging |
| "Other Intangibles" / Capitalized costs | Screener.in Balance Sheet | Soft asset inflation |
| Changes in Working Capital breakdown | Annual Report (CFO section) | WC financing check |
| Related Party Transactions (value, counterparty, nature) | Annual Report Notes | RPT gate |
| Auditor name, tenure, resignation history | Annual Report / BSE filings | Auditor integrity |
| Audit fees vs Non-audit fees | Annual Report Notes | Auditor independence |
| Contingent liabilities (detailed list) | Annual Report Notes | Off-balance-sheet exposure |
| Net Worth / Shareholders' Equity | Screener.in Balance Sheet | Contingent liabilities ratio |
| Goodwill (5Y) | Screener.in Balance Sheet | Acquisition distortion |
| "Contract Assets" / Unbilled Revenue | Annual Report Balance Sheet Notes | Unbilled revenue check |
| Accounts Payable (5Y) | Screener.in Balance Sheet | WC financing check |

**If Annual Report PDF is inaccessible:** WebSearch `"{Company} {FY} annual report related party transactions contingent liabilities auditor fees"` and extract from investor relations pages.

---

## Section 1: Earnings Manipulation Detection

*Based on Schilit Chapters 2-6: Inflating Revenues, Boosting Income with One-time Gains, Shifting Current Expenses to a Later Period*

---

### Check 1.1 — DSO-to-Revenue Divergence Rule

**What it catches**: Aggressive revenue recognition — booking sales before cash is collected, channel stuffing, or recording revenue before delivery obligations are fulfilled.

**Calculation**:

```
DSO (Days Sales Outstanding) = (Accounts Receivable / Revenue) × 365
```

Compute for each of the last 5 fiscal years.

| Year | Revenue (₹Cr) | Accounts Receivable (₹Cr) | DSO (days) | YoY DSO change (%) | YoY Revenue change (%) | DSO - Revenue divergence |
|------|--------------|--------------------------|------------|---------------------|------------------------|--------------------------|
| FY21 | | | | — | — | — |
| FY22 | | | | | | |
| FY23 | | | | | | |
| FY24 | | | | | | |
| FY25 | | | | | | |

**Red Flag Trigger**:

| Condition | Severity | Interpretation |
|-----------|----------|----------------|
| DSO growing **>15%** faster than Revenue in the same year | **Amber** | Revenue recognition likely stretched beyond delivery or collections |
| DSO growing **>20%** faster than Revenue for **2+ consecutive years** | **Red** | Systematic aggressive revenue booking; investigate customer contracts closely |
| DSO expanding while Revenue is **flat or declining** | **Red** | Classic channel stuffing signal — forcing product into distributor pipeline |
| DSO suddenly **contracts sharply** after 2+ years of growth | **Amber** | May indicate a large write-off of bad receivables was absorbed; check provisions |

**Contextual factors**: IT/Services companies (TCS, Infosys) structurally have lower DSO (~45-60 days). EPC/Infrastructure companies may have structurally high DSO (>90 days) due to government receivables. Compare DSO against sector peers before flagging.

**Finding**: ___

**Status**: ✅ Clean / ⚠ Amber / 🔴 Red

---

### Check 1.2 — Unbilled Revenue & Contract Asset Ratio

**What it catches**: Booking revenue (and profits) on long-term contracts well ahead of actual invoicing, cash collection, or project milestones — common in EPC, infrastructure, SaaS, and construction companies.

**Calculation**:

```
Unbilled Revenue Ratio = Unbilled Revenue (or Contract Assets) / Total Revenue
```

Note: Unbilled revenue appears in Balance Sheet under "Current Assets → Other Current Assets" or explicitly as "Contract Assets" (Ind AS 115). Extract from Annual Report Notes.

| Year | Total Revenue (₹Cr) | Unbilled Revenue / Contract Assets (₹Cr) | Ratio (%) | QoQ trend |
|------|---------------------|------------------------------------------|-----------|-----------|
| FY21 | | | | |
| FY22 | | | | |
| FY23 | | | | |
| FY24 | | | | |
| FY25 | | | | |

**Red Flag Trigger**:

| Condition | Severity | Interpretation |
|-----------|----------|----------------|
| Unbilled ratio **accelerating** over 3+ consecutive quarters/years | **Amber** | Accounting revenue outpacing invoiceable milestones |
| Unbilled revenue **>15% of annual revenue** | **Amber** | Material portion of P&L is not yet backed by invoices |
| Unbilled revenue **>25% of revenue** with flat/declining cash collections | **Red** | Earnings are significantly ahead of economic reality; high reversal risk |
| Unbilled revenue growing **faster than order book** | **Red** | Revenue being booked on paper without new orders to justify it |

**Sector benchmarks**: EPC/Construction: 5-12% typical; IT services: <3%; FMCG/retail: near zero. Any value above these norms for the sector warrants explanation.

**Finding**: ___

**Status**: ✅ Clean / ⚠ Amber / 🔴 Red

---

### Check 1.3 — Inventory vs COGS Decoupling (DIO Analysis)

**What it catches**: Over-production to park manufacturing overhead in inventory on the balance sheet (rather than expensing it), artificially inflating gross margins. Classic in auto, FMCG, manufacturing, and pharma.

**Calculation**:

```
DIO (Days Inventory Outstanding) = (Inventory / COGS) × 365
Gross Margin (%) = (Revenue - COGS) / Revenue × 100
```

| Year | Inventory (₹Cr) | COGS (₹Cr) | DIO (days) | YoY DIO change | Gross Margin (%) | YoY Margin change |
|------|----------------|-----------|------------|----------------|-----------------|------------------|
| FY21 | | | | — | | — |
| FY22 | | | | | | |
| FY23 | | | | | | |
| FY24 | | | | | | |
| FY25 | | | | | | |

**Red Flag Trigger**:

| Condition | Severity | Interpretation |
|-----------|----------|----------------|
| DIO rising **>20% YoY** while gross margin is **flat or expanding** | **Amber** | Overhead absorption into inventory, not into P&L — margins are cosmetically clean |
| DIO rising **>30% YoY** while gross margin **expands** against falling revenue | **Red** | Classic over-production manipulation; inventory build is masking demand destruction |
| DIO rising AND inventory composition shifting to **WIP or finished goods** (vs raw materials) | **Red** | Completed product not selling; production-line stuffing; near-term write-down risk |
| Inventory write-off / write-down appearing suddenly after 2+ years of rising DIO | **Amber** | Confirmation that prior DIO build was unsustainable; quality of prior earnings overstated |

**Finding**: ___

**Status**: ✅ Clean / ⚠ Amber / 🔴 Red

---

### Check 1.4 — Expense Capitalization Scrutiny

**What it catches**: Shifting what should be operating expenses (R&D, maintenance, marketing, interest) to the balance sheet as capital assets — artificially boosting current operating profit while inflating assets that may never generate real returns.

**Calculation**: Track the relationship between:
- CapEx growth vs Revenue growth
- CWIP (Capital Work-in-Progress) as % of Gross Block — and whether it converts to productive assets
- "Other Intangibles" or "Capitalized Expenses" on balance sheet trend
- R&D / Marketing / Maintenance in P&L — a sudden collapse without explanation

| Year | Revenue (₹Cr) | CapEx (₹Cr) | CapEx/Revenue (%) | CWIP (₹Cr) | CWIP/Gross Block (%) | Intangibles (₹Cr) | OpEx (R&D+Mktg) in P&L | Observations |
|------|--------------|------------|-------------------|-----------|---------------------|-------------------|------------------------|--------------|
| FY21 | | | | | | | | |
| FY22 | | | | | | | | |
| FY23 | | | | | | | | |
| FY24 | | | | | | | | |
| FY25 | | | | | | | | |

**Red Flag Trigger**:

| Condition | Severity | Interpretation |
|-----------|----------|----------------|
| CWIP growing year-after-year **without ever completing** projects into Gross Block | **Amber** | CWIP is a parking lot for costs that may never be commercially productive |
| CWIP > **30% of Gross Block** for 3+ consecutive years | **Red** | Projects chronically stalled; capital is being destroyed or misclassified |
| R&D expense (P&L) **collapses >30%** while "Intangible Assets" simultaneously spike | **Red** | R&D being shifted from expense to asset — classic capitalization manipulation |
| "Capital Expenditure" jumps **>30% YoY** while revenue is flat or declining | **Amber** | Aggressive capitalization without revenue justification; check audit notes for policy change |
| Depreciation rate declining (assets being depreciated over longer lives) | **Amber** | Extending useful life assumptions = reducing current expense = overstating profit |

**Specific fetches required**:
- WebSearch `"{Company} capital work in progress aging analysis annual report"`
- WebSearch `"{Company} capitalized expenditure intangible assets policy change"`

**Finding**: ___

**Status**: ✅ Clean / ⚠ Amber / 🔴 Red

---

## Section 2: Cash Flow Misdirection Detection

*Based on Schilit Chapter 7-9: Shifting Current Income to a Future Period, Releasing Reserves Improper CFO Inflation*
*O'Glove: "Earnings without cash are accounting, not reality."*

**The central principle**: Management can manipulate the income statement more easily than cash. But there are specific techniques for artificially cleaning up Operating Cash Flow (CFO). Detect them here.

---

### Check 2.1 — The Net Income vs CFO Divergence Rule

**What it catches**: Persistent gap between reported profits and cash actually generated from operations — the single most reliable early-warning indicator of earnings quality problems.

**Calculation**:

```
Annual CFO Quality Ratio = CFO / Net Profit
Rolling 3-Year CFO Quality = Σ(CFO, 3Y) / Σ(Net Profit, 3Y)
```

| Year | Net Profit (₹Cr) | CFO (₹Cr) | Annual CFO/PAT ratio | Notes |
|------|-----------------|----------|----------------------|-------|
| FY21 | | | | |
| FY22 | | | | |
| FY23 | | | | |
| FY24 | | | | |
| FY25 | | | | |
| **3Y Rolling (FY23-25)** | | | **→ KEY NUMBER** | |

**Red Flag Trigger**:

| Condition | Severity | Interpretation |
|-----------|----------|----------------|
| Annual CFO/PAT ratio **<0.8** for 1 year | **Watch** | One-off: check working capital changes; not alarming alone |
| Annual CFO/PAT ratio **<0.8** for **2+ consecutive years** | **Amber** | Systematic shortfall; earnings are not converting to cash |
| Rolling 3-year CFO/PAT **<0.8** | **Red** | O'Glove's hard rule: cumulative mismatch proves earnings are of poor quality |
| CFO is **negative** while Net Profit is **positive** for 2+ years | **Red** | Company is booking accounting profits but bleeding cash; unsustainable |
| CFO growing **much faster** than Net Profit (ratio >2.5 consistently) | **Amber** | Investigate: may be legitimate (non-cash charges) OR artificial (WC manipulation in CFO) |

**High-quality earnings benchmark**: World-class companies (TCS, HUL, Asian Paints historically) maintain CFO/PAT >1.0 consistently over 5-10 year periods. Any ratio below 0.8 over a rolling 3-year period is a forensic red flag per O'Glove's framework.

**Finding**: ___

**Status**: ✅ Clean / ⚠ Amber / 🔴 Red

---

### Check 2.2 — Working Capital Financing Check (AP Inflation & Vendor Factoring)

**What it catches**: Companies using bank-facilitated supply chain financing (reverse factoring / vendor financing) to inflate Accounts Payable temporarily — boosting CFO while hiding what is effectively financial debt.

**Calculation**: Track Days Payable Outstanding alongside CFO.

```
DPO (Days Payable Outstanding) = (Accounts Payable / COGS) × 365
```

| Year | Accounts Payable (₹Cr) | COGS (₹Cr) | DPO (days) | YoY DPO change | CFO (₹Cr) | YoY CFO change | Notes |
|------|----------------------|-----------|------------|----------------|----------|----------------|-------|
| FY21 | | | | — | | — | |
| FY22 | | | | | | | |
| FY23 | | | | | | | |
| FY24 | | | | | | | |
| FY25 | | | | | | | |

**Red Flag Trigger**:

| Condition | Severity | Interpretation |
|-----------|----------|----------------|
| DPO rising **>20%** in a single year while vendor count and purchase volumes are **stable** | **Amber** | AP inflation — check if vendor financing/factoring facility was introduced (check annual report notes) |
| DPO extends sharply **and** CFO improves by similar magnitude | **Red** | Working capital manipulation: AP inflation is boosting CFO artificially |
| Annual report Notes mention "Supply Chain Financing", "Reverse Factoring", or "Vendor Financing Program" | **Red** | Confirm whether this is classified in CFO or properly disclosed as financial liability; if in CFO = misdirection |
| AP balance **far exceeds** cash position while interest costs are rising (separately) | **Amber** | Bank facilities likely being used to defer vendor payments; off-balance-sheet financing risk |

**Specific fetch required**:
- WebSearch `"{Company} supply chain financing reverse factoring annual report notes"`
- Extract from Annual Report: "Changes in Trade Payables" within CFO section; compare against "Borrowings" note

**Finding**: ___

**Status**: ✅ Clean / ⚠ Amber / 🔴 Red

---

### Check 2.3 — Classification Arbitrage (CFI/CFF vs CFO)

**What it catches**: Shifting what should be operating outflows to the Investing/Financing section (making CFO look better) or shifting one-time investing inflows into operating cash (making CFO look higher). Schilit's "Boosting CFO with One-Time Activities."

**Methodology**: Analyze cash flow statement line-by-line for structural anomalies.

**Known techniques to look for**:

| Manipulation Technique | Where It Hides | How to Detect |
|----------------------|----------------|---------------|
| Capitalizing operating expenses (maintenance, marketing, training) | Cash Flow from Investing (CFI) | CapEx spike without asset completion; check CWIP aging |
| Selling receivables (factoring) and booking proceeds as CFO | CFO looks artificially high | Check "Proceeds from sale of current investments" in CFO; look for factoring disclosures in Annual Report notes |
| Booking gains from asset sales (property, investments) inside CFO | CFO inflated by non-operational one-time cash | Look for "Profit/Loss on sale of investments" inside the CFO section rather than CFI |
| Acquiring customers / winning contracts via CapEx (e.g., paying for placement or customer acquisition costs capitalized) | CFI outflow, but operationally an OpEx | Look for suspicious "Customer acquisition costs" or "Contract fulfillment costs" in intangible assets |
| Interest paid shifted from CFO to CFF (under Ind AS choice) | CFO looks better, financing looks worse | Check treatment of interest: if classified in CFF rather than CFO, adjust CFO downward for comparison |

**Specific investigation table**:

| Anomaly Check | Finding | Status |
|--------------|---------|--------|
| Interest paid classification: CFO or CFF? | | Clean/Flag |
| Dividend received classification: CFO or CFI? | | Clean/Flag |
| Any operational receipts appearing in CFI? | | Clean/Flag |
| "Proceeds from sale of assets" — how material vs CFO? | | Clean/Flag |
| Capitalised borrowing costs — is CWIP interest loaded to balance sheet? | | Clean/Flag |
| Factoring / bill discounting disclosed? If yes, classified correctly? | | Clean/Flag |

**Finding**: ___

**Status**: ✅ Clean / ⚠ Amber / 🔴 Red

---

## Section 3: Key Metric & Acquisition Distortion

*Based on Schilit Chapters 10-14: Key Metrics Shenanigans — Non-GAAP manipulation and M&A spring-loading*

---

### Check 3.1 — Non-GAAP / Custom Metric Variance Audit

**What it catches**: Management presenting a flattering alternative version of profitability by systematically excluding recurring costs, burying them as "one-time" or "exceptional" items, year after year.

**Applicable to**: Companies that regularly report "Adjusted EBITDA", "Normalised PAT", "EBITDA before exceptional items", or custom metrics in investor presentations.

**Methodology**: Fetch investor presentations / earnings call transcripts alongside statutory P&L.

| Year | Reported PAT (₹Cr) | "Adjusted" PAT per Mgmt (₹Cr) | Gap (₹Cr) | Gap as % of Reported PAT | What was excluded |
|------|-------------------|------------------------------|-----------|--------------------------|-------------------|
| FY21 | | | | | |
| FY22 | | | | | |
| FY23 | | | | | |
| FY24 | | | | | |
| FY25 | | | | | |

**Red Flag Trigger**:

| Condition | Severity | Interpretation |
|-----------|----------|----------------|
| Same cost category excluded as "exceptional" for **3+ consecutive years** | **Red** | By definition, recurring costs are not exceptional. Management is gaming perception. |
| Gap between statutory and adjusted PAT consistently **>10%** | **Amber** | Adjusted number is meaningfully misleading investors about actual profitability |
| Stock-Based Compensation excluded from "Adjusted" results | **Amber** | SBC is a real cost paid by shareholders via dilution; excluding it overstates economics |
| Restructuring charges recur every 1-2 years | **Red** | Perpetual restructuring = the business is operationally broken OR management uses it as an annual expense absorber |
| Management's "adjusted" metric consistently exceeds analyst consensus earnings on reported basis | **Amber** | Guidance theater: company guides to easily beatable adjusted numbers, misses on real numbers |

**Specific fetches required**:
- WebSearch `"{Company} investor presentation Q4 {FY} exceptional items adjusted EBITDA"`
- WebSearch `"{Company} exceptional items {FY} annual report notes"`

**Finding**: ___

**Status**: ✅ Clean / ⚠ Amber / 🔴 Red

---

### Check 3.2 — M&A Spring-Loading & Goodwill Impairment Filter

**What it catches**: Acquisition-driven companies that: (a) depress acquisition target's pre-deal financials to manufacture a fake post-acquisition "turnaround", (b) book enormous goodwill and then write it off in pieces, signalling capital destruction.

**Applicable to**: Companies that have done 2+ acquisitions in the past 5 years.

**Goodwill History**:

| Year | Goodwill on B/S (₹Cr) | Acquisitions made (₹Cr) | Goodwill Impairment (₹Cr) | Impairment as % of Goodwill |
|------|----------------------|------------------------|--------------------------|----------------------------|
| FY21 | | | | |
| FY22 | | | | |
| FY23 | | | | |
| FY24 | | | | |
| FY25 | | | | |

**Post-acquisition Performance Check**: For the company's 2-3 largest acquisitions, compare:

| Acquisition | Target Revenue pre-deal | Target Revenue 1Y post-deal | Claimed "Organic growth" | Was growth real or manufactured? |
|------------|------------------------|---------------------------|--------------------------|----------------------------------|
| [Name, Year] | | | | |
| [Name, Year] | | | | |

**Red Flag Trigger**:

| Condition | Severity | Interpretation |
|-----------|----------|----------------|
| Goodwill impairment in **any year post-acquisition** | **Amber** | Acquisition was overpaid OR target's prospects deteriorated quickly |
| Multiple goodwill impairments across **different acquisitions** | **Red** | Serial capital destruction; management's M&A judgement is flawed |
| Goodwill > **30% of Total Assets** | **Amber** | Balance sheet is disproportionately composed of unverifiable intangible value |
| Acquired entity's revenue mysteriously **collapses pre-deal** and **surges post-deal** | **Red** | Classic spring-loading: expenses pre-loaded before acquisition, reversed after for a synthetic "turnaround" |
| No post-acquisition performance disclosures in subsequent annual reports | **Amber** | Lack of transparency; buried or forgotten bad deals |

**Finding**: ___

**Status**: ✅ Clean / ⚠ Amber / 🔴 Red

---

## Section 4: Governance Hard Filters — The Binary Rules

*These rules are not scored — they are pass/fail. A single Hard Reject means **immediate AVOID regardless of financials**.*

---

### Filter 4.1 — Related Party Transaction (RPT) Gate

**The core concern**: Companies where promoters siphon value out of the listed entity into private family entities via inflated purchase prices, below-market rent, interest-free loans, or phantom service contracts.

**What to extract from Annual Report (Notes to Accounts — "Related Party Transactions")**:

| RPT Category | Counterparty | Nature | Amount (₹Cr) | % of Revenue / COGS / Total Purchases | Arms-length? (per auditor) | Red flag? |
|-------------|-------------|--------|-------------|--------------------------------------|--------------------------|-----------|
| Sales to related parties | | | | | | |
| Purchases from related parties | | | | | | |
| Loans given to related parties | | | | | | |
| Loans taken from related parties | | | | | | |
| Rent paid to promoter entities | | | | | | |
| Management/consultancy fees paid | | | | | | |
| Corporate guarantees given | | | | | | |
| Other services | | | | | | |

**Red Flag Trigger**:

| Condition | Severity | Interpretation |
|-----------|----------|----------------|
| RPT purchases/sales to promoter-owned entities **>5% of total revenue** | **Amber** | Material leakage risk; investigate pricing and necessity |
| RPT purchases/sales **>10% of total revenue** | **Red** | Hard downgrade — value extraction likely at scale |
| Loans to promoter or promoter-related entities (any amount) | **Red** | Classic fund diversion technique; frequently precedes accounting frauds |
| "Management fees" or "brand royalties" paid to promoter holding entity **without disclosed rationale** | **Red** | Structural value extraction via opaque service contracts |
| RPTs increasing as % of revenue year-over-year | **Amber** | Escalating transfer pricing risk |
| Auditor qualified the RPT disclosure as "not fully arm's length" | **Hard Reject** | Auditor is flagging possible fraud; exit immediately |

**Finding**: ___

**Status**: ✅ Clean / ⚠ Amber / 🔴 Red / 🚫 Hard Reject

---

### Filter 4.2 — Auditor Integrity Check

**The core concern**: Auditors are the last line of defence. A compromised, captured, or rapidly-exiting auditor is a severe governance red flag.

**Auditor History**:

| Year | Auditor Name | Big 4 / National firm? | Tenure (years as of that year) | Audit Fee (₹L) | Non-Audit Fee (₹L) | Non-Audit/Audit ratio | Notes |
|------|-------------|----------------------|-------------------------------|---------------|-------------------|----------------------|-------|
| FY21 | | | | | | | |
| FY22 | | | | | | | |
| FY23 | | | | | | | |
| FY24 | | | | | | | |
| FY25 | | | | | | | |

**Auditor Resignation Investigation**: WebSearch `"{Company} auditor resignation BSE announcement"` — extract the resignation letter from BSE corporate announcements. The stated reason is critical.

**Red Flag Trigger**:

| Condition | Severity | Interpretation |
|-----------|----------|----------------|
| Mid-term auditor resignation with reason "pre-occupation of time" or "other professional commitments" | **Hard Reject** | This phrasing is standard cover for forced or uncomfortable exits. Exit signal per ICAI guidance. |
| Mid-term resignation with **no reason given** | **Hard Reject** | Regulatory obligation requires reason; absence means it was withheld by both parties |
| Auditor resigned **during or immediately after** a fraud investigation, SEBI order, or sharp stock decline | **Hard Reject** | Temporal proximity = association with the underlying problem |
| Non-audit fees / Audit fees ratio **>25%** | **Amber** | Independence compromised when consulting relationships are material |
| Non-audit fees / Audit fees ratio **>50%** | **Red** | Auditor is more a business partner than independent watchdog |
| Auditor changed **more than once in 5 years** (without the mandated SEBI rotation reason) | **Amber** | Repeated auditor shopping; investigate what each prior auditor flagged |
| Auditor gave **qualified opinion** on financials | **Amber** | Specific qualification scope must be read carefully |
| Auditor gave **adverse opinion or disclaimer** | **Hard Reject** | Nuclear-level governance failure; statements cannot be relied upon |
| Small, obscure local firm auditing a ₹1000Cr+ company | **Red** | Capacity mismatch; raises independence and quality questions |

**Finding**: ___

**Status**: ✅ Clean / ⚠ Amber / 🔴 Red / 🚫 Hard Reject

---

### Filter 4.3 — Contingent Liabilities Burden

**The core concern**: Large contingent liabilities sitting quietly off-balance-sheet can materialize overnight — turning a reported profitable company into a loss-making or net-worth-negative entity. Indian companies routinely bury years of exposure in small-font Annual Report notes.

**Extract from Annual Report Notes (typically Note: "Contingent Liabilities and Commitments")**:

| Category | Amount (₹Cr) | Status / Nature | Probability of crystallisation (per auditor) | Impact if crystallised |
|---------|-------------|----------------|---------------------------------------------|----------------------|
| Income Tax disputes (pending appeals) | | | | |
| GST / Indirect Tax disputes | | | | |
| Customs / Excise disputes | | | | |
| SEBI / regulatory penalties (contested) | | | | |
| Litigation / commercial disputes | | | | |
| Corporate guarantees given to subsidiaries | | | | |
| Guarantees given to third parties | | | | |
| Environmental liabilities | | | | |
| **Total Contingent Liabilities** | | | | |
| **Net Worth (Shareholders' Equity)** | | | | |
| **CL / Net Worth ratio** | | | | |

**Red Flag Trigger**:

| Condition | Severity | Interpretation |
|-----------|----------|----------------|
| Total contingent liabilities **>10% of Net Worth** | **Amber** | Non-trivial exposure; assess crystallisation probability for each item |
| Total contingent liabilities **>20% of Net Worth** | **Red** | Material risk — if even 50% of CL crystallise, net worth is significantly impaired |
| Total contingent liabilities **>Net Worth** | **Hard Reject** | A crystallisation event could result in negative net worth; stock is effectively a call option on legal outcomes |
| Corporate guarantees given to **loss-making subsidiaries** | **Red** | Guarantee will likely be called; it is functionally already a liability |
| Tax disputes contested for **>7 years** with escalating amounts | **Amber** | Long-running disputes often resolve partially against the company; provision may be understated |
| CL growing **>25% YoY** for 2+ consecutive years | **Amber** | Liability profile deteriorating; legal/regulatory environment worsening for the company |

**Finding**: ___

**Status**: ✅ Clean / ⚠ Amber / 🔴 Red / 🚫 Hard Reject

---

## Forensic Scoring — Manipulation Risk Score (MRS)

Tally all checks from Sections 1-4. **A single Hard Reject in Section 4 overrides the entire scorecard and forces a AVOID verdict regardless of score.**

### Hard Reject Override (binary — check first)

| Hard Reject Trigger | Triggered? (Y/N) | Source Evidence |
|--------------------|-----------------|----------------|
| Auditor mid-term resignation with vague reason | | |
| Auditor adverse opinion or disclaimer of opinion | | |
| RPT auditor qualification as "not arm's length" | | |
| Contingent liabilities > Net Worth | | |

**If ANY Hard Reject is triggered → Output: `🚫 HARD REJECT — DO NOT INVEST` with the specific trigger cited. Skip remainder of scoring.**

---

### Scorecard (only if no Hard Reject)

| Check | Status | Weight | Contribution |
|-------|--------|--------|-------------|
| 1.1 DSO-Revenue Divergence | ✅/⚠/🔴 | 12% | |
| 1.2 Unbilled Revenue Ratio | ✅/⚠/🔴 | 8% | |
| 1.3 Inventory-COGS Decoupling (DIO) | ✅/⚠/🔴 | 8% | |
| 1.4 Expense Capitalization (CWIP/Intangibles) | ✅/⚠/🔴 | 10% | |
| 2.1 CFO vs Net Income Divergence | ✅/⚠/🔴 | 18% | |
| 2.2 Working Capital / AP Inflation | ✅/⚠/🔴 | 10% | |
| 2.3 Cash Flow Classification Arbitrage | ✅/⚠/🔴 | 7% | |
| 3.1 Non-GAAP Metric Variance | ✅/⚠/🔴 | 7% | |
| 3.2 M&A Goodwill / Spring-Loading | ✅/⚠/🔴 | 5% | |
| 4.1 Related Party Transaction Gate | ✅/⚠/🔴 | 8% | |
| 4.2 Auditor Integrity (no Hard Reject triggered) | ✅/⚠/🔴 | 4% | |
| 4.3 Contingent Liabilities Burden | ✅/⚠/🔴 | 3% | |

**Scoring key**: ✅ Clean = 0 penalty points | ⚠ Amber = 1 point | 🔴 Red = 2 points

**Total penalty points (weighted)**:

| Penalty Band | MRS Rating | Interpretation |
|-------------|-----------|----------------|
| 0 points | **🟢 GREEN — High Earnings Quality** | No red flags; proceed to full financial analysis with confidence |
| 1-2 weighted Amber flags | **🟡 AMBER — Caution** | Monitor the flagged areas; deeper investigation recommended before investing |
| Any single Red flag OR 3+ Amber flags | **🟠 ORANGE — Significant Concern** | Potential systematic manipulation; require management explanation before investing; reduce position size |
| 2+ Red flags | **🔴 RED — Avoid** | Multiple manipulation signals; high probability of earnings overstated; do not invest until resolved |
| Hard Reject triggered | **🚫 HARD REJECT** | Automatic AVOID regardless of financial metrics |

---

## Output Report Template

When this framework is invoked, produce a structured report in this format:

```
## Forensic Accounting & Governance Report: {Company Name} ({Symbol})
Analyst: Market Sage | Date: {date} | Sources: {list all sources cited}

### Hard Reject Check
[PASS / FAIL — with specific trigger if FAIL]

### Manipulation Risk Score (MRS): {🟢/🟡/🟠/🔴/🚫} — {Rating Name}

### Executive Summary
[3-5 bullet points: the most important findings — what is clean, what is flagged, what needs immediate attention]

### Section 1: Earnings Manipulation
- 1.1 DSO Divergence: {Status} — {1-2 line finding with data}
- 1.2 Unbilled Revenue: {Status} — {1-2 line finding}
- 1.3 Inventory-COGS Decoupling: {Status} — {1-2 line finding}
- 1.4 Expense Capitalization: {Status} — {1-2 line finding}

### Section 2: Cash Flow Quality
- 2.1 CFO vs Net Income: {Status} — {Rolling 3Y ratio: X.XX — finding}
- 2.2 Working Capital / AP: {Status} — {DPO trend + AP financing finding}
- 2.3 Cash Flow Classification: {Status} — {specific anomalies found or none}

### Section 3: Metric & Acquisition Distortion
- 3.1 Non-GAAP Variance: {Status} — {Gap in ₹Cr and %, recurring items}
- 3.2 M&A Goodwill: {Status} — {Goodwill impairment history}

### Section 4: Governance Hard Filters
- 4.1 Related Party Transactions: {Status} — {Key RPTs, amounts, % of revenue}
- 4.2 Auditor Integrity: {Status} — {Name, tenure, non-audit fees ratio, any resignation}
- 4.3 Contingent Liabilities: {Status} — {Total CL, CL/Net Worth %, key items}

### Detailed Evidence
[Full tables from all checks above, with source citations and dates]

### Investor Guidance
[Based on MRS rating:
- GREEN: What to continue monitoring; proceed with financial analysis
- AMBER: Specific questions to ask management; what to verify before investing
- ORANGE/RED: Specific risks to articulate; position sizing guidance; what resolution looks like
- HARD REJECT: Specific trigger, why this is a binary AVOID, what would need to change]
```

---

## Integration with Stock Analyzer

When this framework is run as part of a full stock analysis (via `stock-analyzer.md`):

1. **This framework replaces Step 2** (Corporate Governance Analysis) with a deeper forensic version.
2. The **MRS rating feeds directly into the Final Verdict** in Step 8 (Summary Scorecard):
   - 🟢 GREEN: Governance dimension scores 8-10/10
   - 🟡 AMBER: Governance dimension scores 5-7/10
   - 🟠 ORANGE: Governance dimension scores 2-4/10; total score capped at 6/10 regardless of other factors
   - 🔴 RED: Governance dimension scores 0-1/10; total score capped at 4/10; verdict forced to **AVOID**
   - 🚫 HARD REJECT: Verdict forced to **AVOID — DO NOT INVEST** overriding all other analysis
3. The Section 4 filters (RPT Gate, Auditor, Contingent Liabilities) **must be summarized in the Corporate Governance Red Flags table** in Step 2.3.

---

## Sector-Specific Forensic Calibration

Not all accounting choices are manipulative — some are industry-normal. Apply these contextual adjustments:

| Sector | Expected High DSO | Expected High CWIP | Non-GAAP common? | Key forensic focus |
|--------|------------------|-------------------|------------------|--------------------|
| IT Services | Yes (60-90 days) | No | Yes (exclude SBC) — watch SBC exclusion size | Unbilled revenue, DSO vs revenue divergence |
| EPC / Infrastructure | Yes (90-150 days govt receivables) | Yes (normal) | Yes | Unbilled revenue ratio, CWIP aging, CFO vs PAT |
| FMCG / Consumer | No (low DSO expected) | No | Rarely | DIO, channel stuffing, RPT with promoter brands |
| Real Estate | Yes (pre-sales) | Yes (under-construction) | Yes (pre-sales focus) | Revenue recognition timing, contingent liabilities |
| Pharma | Moderate | Yes (R&D capitalization) | Common | R&D capitalization, USFDA-related contingencies |
| Manufacturing | Moderate | Yes | Rare | DIO, CWIP aging, over-production |
| Banking / NBFC | N/A | N/A | Yes (pre-provision profit) | NPA provisioning adequacy (not covered here — use banking sector framework) |
| Metals / Mining | Moderate | Yes | Common | Revenue recognition, inventory valuation method |

---

*This framework synthesizes Howard Schilit's Financial Shenanigans (4th edition), Thornton O'Glove's Quality of Earnings, and forensic accounting practices adapted for the Indian market regulatory environment (Ind AS, SEBI LODR, ICAI standards). All financial checks require live fetched data per Market Sage's non-negotiable data integrity mandate.*

---
**Disclaimer**: This forensic framework is for educational and analytical purposes only. It does not constitute financial or legal advice. The identification of red flags does not prove fraud — it signals areas requiring deeper investigation. Always verify findings independently before making investment decisions. Consult a SEBI-registered investment advisor.
