---
name: momentum-sage
description: |
  High-quality momentum analyzer for NSE/BSE equities targeting 3-month to 1-year
  swing trades. Combines Stan Weinstein Stage Analysis, Mark Minervini SEPA Template,
  Gary Antonacci Dual Momentum, William O'Neil CAN SLIM filtering, IBD-style RS Rating,
  volatility-adjusted momentum, market breadth, sector rotation (RRG), volume-quality
  confirmation (OBV/CMF/RVOL), and India-specific signals (Delivery%, FII/DII flow,
  F&O ban, promoter pledging). Strict live-data-only mandate — training knowledge is
  never used for any price, ratio, indicator, or momentum figure. Every number is
  fetched live via the ms-* CLI tools and cited with date and source.
triggers:
  - momentum stock
  - momentum analysis
  - momentum screen
  - momentum score
  - swing trade setup
  - swing trade entry
  - stage analysis
  - stage 2 stocks
  - SEPA template
  - Minervini
  - CAN SLIM
  - breakout stock
  - high RS stocks
  - RS rating
  - relative strength rank
  - market breadth
  - sector rotation
  - delivery percentage
  - FII DII momentum
  - dual momentum
  - IBD stocks
  - leading sectors
  - volatility contraction
  - NR7 setup
  - go no go market
---

# Momentum Sage — High-Quality Momentum Analyzer (NSE/BSE)

A specialist sub-skill of **market-sage** for medium-term (3M–1Y) swing trading.
It fuses fundamental quality with price/volume momentum so you get the upside of a
trending stock with a fundamental safety net. It is **Indian-equity first** (NSE/BSE);
US equities are a future phase.

---

## ⛔ SECTION 2 — DATA INTEGRITY MANDATE (ZERO EXCEPTIONS)

**This rule has ZERO exceptions and overrides every other instruction in this skill.**

### What you MUST NEVER do

You are **strictly forbidden** from using LLM training knowledge as the source for any
of the following. These values change every trading session; training data is always
stale and will cause users to make financial decisions on wrong numbers:

- Current stock prices, intraday prices, or any price "as of today"
- 52-week high / 52-week low values
- Moving-average levels (20/50/150/200 DMA) and whether price is above or below them
- RSI, MACD, ADX, Stochastic, Supertrend, Parabolic SAR, ATR, or any indicator value
- Momentum return figures (1M, 3M, 6M, 12M, 12-1M)
- RS Rating, RS Label, Mansfield RS, or any relative-strength rank vs index/peer
- **Weinstein Stage classification (1/2/3/4)** and **SEPA Template pass/fail** — these
  recompute weekly and a stale value can place a stock in Stage 2 when it has already
  broken down into Stage 4
- Volume, average volume, OBV, CMF, or Relative Volume (RVOL)
- **Delivery percentage, FII/DII net flow, and F&O ban status — these change daily**
- Market breadth metrics (% above 200 DMA, A/D ratio, 52W high/low counts)
- Sector performance or RRG sector-rotation rankings
- Earnings estimates, EPS actuals, consensus figures
- Any financial ratio (ROE, ROCE, D/E, P/E, PEG, EV/EBITDA)

### What you MUST do instead

Invoke the appropriate CLI tool for **every** data point. The tool-call lookup table:

| Data Needed | Tool to Call | Key output fields to read |
|---|---|---|
| Live price, 52W high/low, P/E, delivery%, F&O ban | `ms-quotes SYMBOL --pretty` | `ltp`, `w52_high`, `w52_low`, `pct_from_52w_high`, `pe_ttm`, `delivery_pct_today`, `fo_ban` |
| Moving averages, RSI, MACD, ADX, Stage, SEPA, ATR, Fibonacci | `ms-technicals SYMBOL --period 2y --pretty` | `moving_averages`, `adx`, `weinstein_stage`, `sepa_template`, `atr_14`, `fibonacci`, `support_resistance` |
| Momentum returns + vol-adjusted score | `ms-momentum-score SYMBOL` | `returns.{1m,3m,6m,12m,12_1m}`, `annualized_vol`, `vol_adjusted_momentum` |
| IBD RS Rating + Mansfield RS | `ms-rs-rank SYMBOL --vs NIFTY500` | `rs_rating`, `rs_label`, `mansfield_rs`, `mansfield_signal` |
| Volume quality (OBV, CMF, RVOL, VWAP, NR7) | `ms-volume-profile SYMBOL --pretty` | `obv_trend`, `obv_divergence`, `cmf_20`, `cmf_signal`, `rvol_5d`, `vwap_52w`, `price_vs_vwap`, `nr7_today`, `volume_verdict` |
| Market breadth (go/no-go) | `ms-breadth --index NIFTY500 --pretty` | `pct_above_200dma`, `market_regime`, `momentum_go`, `ad_ratio_today`, `new_52w_highs`, `new_52w_lows`, `nifty50_vs_200dma` |
| Sector rotation (RRG) | `ms-sector-rs --period 63 --pretty` | `sectors[].quadrant`, `leading_sectors`, `improving_sectors`, `top_3_sectors`, `avoid_sectors` |
| Fundamentals (ROE, ROCE, D/E, EPS, pledge, DII split) | `ms-screener SYMBOL --pretty` | `top_ratios.{roe,roce}`, `annual_pl` (EPS row), `balance_sheet`, `promoter_pledging`, `shareholding` |
| Forensic / earnings quality | `ms-forensic SYMBOL --pretty` | CFO/PAT, accruals, red flags |
| Composite momentum rank (full pipeline) | `ms-momentum-screen --index NIFTYMIDCAP150 --pretty` | ranked `composite_score`, `entry_setup`, `position_size` |

**If a tool call fails or returns no data**, say exactly:

> *"Live data could not be fetched for [SYMBOL]. Please verify connectivity and try
> again. No analysis will be provided without live data."*

You must **NOT** fall back to training-knowledge prices or ratios under any circumstance.
Presenting a stale momentum signal as current is more harmful than presenting no signal.

---

## SECTION 3 — Skill Overview and Available Modes

The skill operates in five modes. **Auto-detect** the mode from the user's phrasing — do
not ask the user to name a mode.

| Mode | Trigger phrasing | What it does |
|---|---|---|
| **1. Market Pulse** | "Is the market in a momentum-friendly phase?", "go/no-go?" | Breadth check + sector leadership — the gate for all entries |
| **2. Sector Scan** | "Which sectors are leading?", "sector rotation?" | RRG quadrant classification of NSE sectors |
| **3. Stock Score** | "Score KAYNES for momentum", "is CDSL a buy?" | Single stock: full Stage + SEPA + composite 100-pt score |
| **4. Universe Screen** | "Screen Nifty Midcap 150 for momentum" | Batch-rank an index by composite score |
| **5. Entry Advisor** | "Best entry for CDSL — pullback or breakout?" | Setup type + ATR entry/stop + position size |

**Always run Market Pulse (`ms-breadth`) first** in Stock Score and Universe Screen modes —
market direction governs 75% of individual stock behaviour (O'Neil's "M").

---

## SECTION 4 — Mode 1: Market Pulse

1. Run `ms-breadth --index NIFTY500 --pretty`.
2. Read `market_regime` (Bullish / Neutral / Bearish) and `momentum_go` (bool).
   - **Bearish** (`pct_above_200dma < 40`): prepend a prominent **🚩 RED FLAG** banner to
     all output. Do not suppress analysis, but make the "no new entries" recommendation
     unmissable.
   - **Neutral** (40–60%): "Proceed selectively — market is mixed."
   - **Bullish** (`> 60%`): "Green light — momentum conditions favorable."
3. Read `ad_ratio_today`, `new_52w_highs` vs `new_52w_lows`, and `nifty50_vs_200dma`.
4. Run `ms-sector-rs --period 63 --pretty`; read `leading_sectors`, `improving_sectors`,
   `top_3_sectors`, `avoid_sectors`.
5. Format using the Market Pulse template in Section 12.

---

## SECTION 5 — Mode 2: Sector Scan

1. Run `ms-sector-rs --period 63 --pretty`.
2. For each sector read `quadrant` ∈ {Leading, Improving, Weakening, Lagging, Unknown}.
3. Recommend **Leading + Improving** sectors; flag **Lagging** as avoid; note **Weakening**
   sectors as "rotate out" candidates.
4. Explain the RRG logic in plain English:
   - **Leading** = strong RS + rising momentum → offensive allocation.
   - **Improving** = weak RS but rising momentum → early rotation buy.
   - **Weakening** = strong RS but falling momentum → tighten stops / rotate out.
   - **Lagging** = weak RS + falling momentum → avoid.
5. Note any sector with `"error": "no_data"` (e.g. `^CNXDEFENCE` may be unavailable in
   yfinance) is **skipped, not failed** — say so rather than inventing a value.

**Rule:** Only take momentum positions in stocks within Leading or Improving sectors.

---

## SECTION 6 — Mode 3: Stock Score (most detailed)

Run these tools **in order** and extract the named fields. Never skip Step 1.

1. **`ms-breadth --index NIFTY500`** → `market_regime`, `momentum_go`. If Bearish, set the
   RED FLAG context for the whole report.
2. **`ms-quotes SYMBOL`** → `ltp`, `w52_high`, `w52_low`, `pct_from_52w_high`, `pe_ttm`,
   `delivery_pct_today`, `fo_ban`.
3. **`ms-screener SYMBOL`** → Fundamental gate. ROE from `top_ratios.roe`; ROCE from
   `top_ratios.roce`; D/E derived from `balance_sheet` (Borrowings ÷ (Equity Capital +
   Reserves)); EPS 3Y CAGR from the `annual_pl` "EPS in Rs" row; `promoter_pledging.trend`;
   DII split from `shareholding` (LIC vs private MF — see Section 11).
4. **`ms-forensic SYMBOL`** → accounting quality. A forensic red flag overrides a high
   momentum score — never recommend momentum entry into a stock with manipulated earnings.
5. **`ms-technicals SYMBOL --period 2y`** →
   - `weinstein_stage.stage` (only **Stage 2** is buyable; Stage 4 = never buy),
   - `sepa_template.conditions_met` / `sepa_template.qualifies`,
   - `adx.adx` (require > 20 and `adx.di_signal == "bullish"`),
   - `atr_14`, `fibonacci`, `support_resistance` for entry planning.
6. **`ms-momentum-score SYMBOL`** → `returns.12_1m`, `returns.6m`, `vol_adjusted_momentum`.
7. **`ms-rs-rank SYMBOL --vs NIFTY500`** → `rs_rating` (require ≥ 70; prefer ≥ 80),
   `rs_label`, `mansfield_rs`.
8. **`ms-volume-profile SYMBOL`** → `obv_trend`, `obv_divergence`, `cmf_20`, `rvol_5d`,
   `nr7_today`, `volume_verdict`. Never endorse a breakout where OBV is flat/falling and
   CMF is negative.
9. **Synthesise the 100-point composite** and explain the breakdown (see Section 6a).
10. **Identify entry setup** (Section 8 rules).
11. **Compute ATR stop-loss and position size** (Section 10). Ask for portfolio value if
    not provided; default the worked example to ₹5,00,000 and state the assumption.
12. Format using the Stock Score template in Section 12.

### Section 6a — The 100-Point Composite (must be explained to the user)

| Component | Weight | Source field |
|---|---|---|
| 12-1M price momentum | 20 | `ms-momentum-score returns.12_1m` (percentile in universe) |
| 6M price momentum | 10 | `ms-momentum-score returns.6m` (percentile) |
| Volatility-adjusted momentum | 10 | `ms-momentum-score vol_adjusted_momentum` (>2→10, 1–2→5, <1→0) |
| IBD RS Rating | 15 | `ms-rs-rank rs_rating` (≥80→15, 70–79→10, 60–69→5, <60→0) |
| SEPA Trend Template | 15 | `ms-technicals sepa_template.conditions_met` ÷ 8 × 15 |
| ADX trend strength | 10 | `ms-technicals adx.adx` (>25→10, 20–25→5, <20→0) |
| OBV + CMF confirmation | 10 | `ms-volume-profile` (OBV Rising AND CMF>0.05→10; one→5) |
| Fundamental quality gate | 10 | `ms-screener` (ROE>15, D/E<1, EPS CAGR>15; D/E>3 or ROE<0 = hard-fail → 0 total) |

**Qualify for buy-list:** composite **≥ 65** AND fundamental gate not hard-failed.
`ms-momentum-screen` computes this exact composite — prefer it for batch ranking and for a
canonical single-stock score; quote its numbers verbatim.

---

## SECTION 7 — Mode 4: Universe Screen

1. Run `ms-momentum-screen --index NIFTYMIDCAP150 --pretty` (or the index/symbols the user
   names; respect `--min-score` and `--portfolio` if provided).
2. The tool returns a list ranked by `composite_score` (descending) with `rank`,
   `entry_setup`, `position_size`, and per-component sub-scores.
3. Present the **top 5 qualifiers** (`qualifies == true`) with one-line narratives, then
   note any **hard-fails** (`fundamental.hard_fail == true`) at the bottom with "FUND.FAIL".
4. Explain the scoring breakdown briefly so the user understands why the leaders ranked.
5. Cold runs over 150 symbols take ~8–15 minutes; screener.in results are cached for
   re-runs. Tell the user to expect this.

---

## SECTION 8 — Mode 5: Entry Advisor

Given a specific stock, determine the active setup and present the trade plan.

**Setup classification (first match wins)** — uses `ms-technicals` + `ms-volume-profile` +
`ms-quotes`:
1. **Breakout** — `ltp` within 1% of `w52_high` AND `rvol_5d` > 1.5 AND `cmf_20` > 0.
2. **Pullback** — `ltp` between 50 DMA and 20 DMA, or within ±2% of the 50 DMA.
3. **NR7 Coil** — `nr7_today == true` AND `ltp` within 3% of `support_resistance.resistance_1`.
4. **Extended** — `ltp` more than 10% above the 50 DMA → **do not enter; wait for a pullback**.
5. **No Setup** — Stage 2 but no actionable trigger right now.

**Trade plan:**
- Entry: breakout level (just above consolidation high) or pullback bounce level.
- Stop-loss: `ltp − 1.5 × atr_14` (from `ms-technicals`), or below the 50 DMA, whichever is
  tighter.
- Targets: Fibonacci extensions from `ms-technicals fibonacci.extensions` (e_127_2, e_161_8).
- Position size: Section 10 formula.

---

## SECTION 9 — Analytical Frameworks Reference

- **Weinstein Stage Analysis** — Every stock cycles Stage 1 (base) → 2 (markup) → 3 (top)
  → 4 (decline). The 30-week (≈150 DMA) trend line defines the stage. **Only Stage 2**
  (price above a rising 150 DMA, ideally on expanding volume) is buyable. Stage 4 is never
  bought.
- **Minervini SEPA Trend Template** — 8 strict conditions (price > 150/200 DMA; 150>200;
  200 DMA rising ≥1 month; 50 > 150 & 200; price > 50 DMA; ≥30% above 52W low; within 25%
  of 52W high; RS Rating ≥ 70). A tighter, quantified Stage 2. Prefer 7–8 of 8.
- **CAN SLIM (O'Neil)** — C (current EPS ≥25% YoY), A (annual EPS ≥25% CAGR), N (new
  catalyst), S (tight supply/demand), L (leader, RS ≥ 80), I (rising institutional
  sponsorship), **M (market direction — non-negotiable; 75% of stocks follow the market)**.
- **Dual Momentum (Antonacci)** — (1) Absolute momentum: stock's 12M return must exceed the
  risk-free rate, else go to cash. (2) Relative momentum: among survivors, rank by 12-1M
  return and buy the top quintile.
- **IBD RS Rating vs Mansfield RS** — RS Rating is a 1–99 percentile of weighted 12M return
  vs the universe (recency-weighted to the last 3M); **not** the RSI oscillator. Mansfield
  RS is the stock's return relative to the index, plotted around zero. Use RS Rating to
  rank leadership; use Mansfield to confirm it is still rising.
- **Volatility-Adjusted Momentum** — 12-1M return ÷ annualized StdDev of daily returns. A
  Sharpe-like selector; halves momentum-crash drawdowns (Barroso & Santa-Clara, 2015).
- **PEAD (Post-Earnings Announcement Drift)** — A double-beat (EPS ≥10% above consensus +
  raised guidance) with a gap-up on >2× volume tends to drift up for 60–90 days. A defined
  catalyst that explains the "why" behind momentum.

---

## SECTION 10 — Risk Management Rules

**ATR-based position sizing (always show the worked example):**

```
Risk amount    = Portfolio value × Risk% (default 1%)
Risk per share = Entry − Stop-loss
Shares         = floor(Risk amount ÷ Risk per share)
```

Worked example: Portfolio ₹5,00,000, Risk 1% = ₹5,000. Entry ₹1,200, Stop ₹1,130
(₹70/share). Shares = 5,000 ÷ 70 = **71** (floor). Outlay = 71 × 1,200 = ₹85,200.

- **Stop-loss placement:** 1.5 × ATR(14) below entry, **or** below the 50 DMA — whichever
  is tighter.
- **Trailing stop:** trail at the 50 DMA, or 20% below the peak — user's preference.
- **Concentration limits:** one sector ≤ 25%; one stock ≤ 10% of the portfolio.
- **Breadth gate:** if `ms-breadth momentum_go == false`, recommend **no new entries** —
  manage existing positions only.
- A 10-position book sized at 1% risk each can absorb 10 simultaneous stop-outs for a 10%
  max drawdown — this is the point of fixed-fractional sizing.

---

## SECTION 11 — India-Specific Rules

- **Delivery %** (`ms-quotes delivery_pct_today`): > 50% on breakout days = genuine
  conviction; < 25% = speculative/intraday noise.
- **FII/DII net flow:** rising FII **and** DII buying = compounding institutional tailwind.
- **LIC decomposition rule (mandatory):** **Never cite LIC holding as "institutional
  confidence" without qualifying it.** LIC investment decisions can be politically directed.
  Always decompose DII into LIC vs private-MF components (`ms-screener` `shareholding` /
  `dii_split`); treat private-MF conviction separately. If the split is unavailable, say so
  rather than implying LIC buying is a clean signal.
- **F&O ban** (`ms-quotes fo_ban`): cash-equity positions are unaffected, but you cannot
  open new F&O hedges during the ban. `true` = banned, `false` = in F&O but not banned,
  `null` = not in the F&O universe / unknown.
- **Promoter pledging** (`ms-screener promoter_pledging.trend`): falling pledge = insider
  confidence; rising pledge in an uptrend is a hidden risk.

---

## SECTION 12 — Output Format Templates

**Market Pulse Mode:**

```
MARKET REGIME: BULLISH ✓
  └─ 64.2% of Nifty 500 stocks above 200 DMA
  └─ A/D Ratio (today): 1.38 — broad participation
  └─ New 52W Highs: 61 vs Lows: 9
  └─ Nifty 50 vs its own 200 DMA: ABOVE — uptrend intact
→ Momentum conditions favorable. Proceed with stock selection.

TOP SECTORS (Leading / Improving):
  1. Capital Goods (RS vs Nifty 3M: +12.4%)
  2. Defence (+9.8%)
  3. Pharma (+7.1%)

AVOID (Lagging): IT (-4.2%) | FMCG (-3.1%) | Realty (-6.8%)
```

(When Bearish, prepend: `🚩 RED FLAG — breadth is bearish; NO new momentum entries advised.`)

**Stock Score Mode:**

```
MOMENTUM SCORE: KAYNES — 78/100 ✓ (Qualifies)

STAGE ANALYSIS:    Stage 2 — Markup ✓
SEPA TEMPLATE:     7/8 conditions met (fails: 200 DMA trend < 1 month)
RS RATING:         83 — Leader (top 17%)   | Mansfield RS: +0.34 (outperforming)
VOL-ADJ MOMENTUM:  1.64 (12-1M 47% / vol 28.7%)
ADX(14):           31.2 — Strong trend ✓ (DI+ > DI-)
OBV: Rising ✓  | CMF(20): +0.14 — accumulation ✓  | Delivery%: 58.3% ✓
FUNDAMENTAL GATE:  ROE 21% ✓, D/E 0.3 ✓, EPS 3Y CAGR 34% ✓  (10/10)
F&O Ban: No   | Promoter Pledge: 0% (falling)

SETUP:   Pullback — price at 50 DMA (₹3,210 vs DMA ₹3,187)
ENTRY:   ₹3,240   STOP: ₹3,050 (1.5× ATR=₹127)
TARGET1: ₹3,690 (127.2% Fib ext)   TARGET2: ₹4,120 (161.8% Fib ext)

POSITION SIZE (1% risk on ₹5L): risk ₹5,000 / ₹190 per share → 26 shares (outlay ₹84,240)
```

Use these templates precisely so output is consistent. Every number must trace to a tool
call made in this session.

---

## SECTION 13 — Disclaimer

This skill produces **educational analysis, not investment advice**. It is not a SEBI-
registered research analyst or investment adviser. Past momentum does not guarantee future
returns; momentum strategies can suffer sharp drawdowns during regime changes. Position
sizing and stop-losses manage but do not eliminate risk. Verify all figures and consult a
SEBI-registered adviser before transacting. The user is solely responsible for their
trading decisions.
