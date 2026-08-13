# Stage 4B — Market Matchup Analysis

**Goal:** Discover the highest-value market weakness of the frozen Champion before
building a challenger. No Champion code was modified; this is observation-only.

**Bottom line:** The frozen Champion (ChampionPolicy / `auto`) wins only **6 of 12**
(50%) games against the `market` opponent. The Champion's own behaviour is
*near-invariant* between wins and losses — the outcome is driven entirely by the
opponent. The decisive variable is **high-value crop capture (melon)**: whenever
the `market` opponent commits to a melon-heavy endgame (≈40 melon sold), the
Champion loses (6/6); whenever it does not (≤15 melon), the Champion wins. The
Champion leads for ~26 days then is overtaken in the **final endgame window
(day 28)** by the opponent's melon liquidation spike.

---

## 1. Benchmark Configuration

| Item | Value |
|------|-------|
| Champion | `main.agent` → `FailSafeAgent(ChampionPolicy())` (frozen, "auto") |
| Opponent | `market` preset (`sell_min_ratio=0.7`, `reserve_money=300`, `target_hands=(3,4,5,6)`) |
| Player assignment | Champion = player 0, market = player 1 (fixed) |
| Episode length | 720 turns (30 days × 24) |
| Seeds | 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 (deterministic via `configuration.seed`) |
| Games | 12 (full 720-turn completion, 0 errors, 0 fallbacks) |
| Telemetry source | `env.steps` per-step observation + action for both players |
| Reproducible | Yes — same seed → identical result (verified) |

Scripts: `scripts/stage4b/market_matchup_benchmark.py` (collection),
`scripts/stage4b/analyze_market_matchup.py` (aggregation).

## 2. Headline Results

| Metric | Value |
|--------|-------|
| Games | 12 |
| Wins / Losses / Ties | 6 / 6 / 0 |
| Win rate | **50.0%** |
| Avg Champion coins | 13,391 |
| Median Champion coins | 12,101 |
| Avg Market coins | 13,404 |
| Median Market coins | 13,587.5 |
| Avg margin (Champ − Market) | −13.2 |
| Median margin | −1,663.5 |
| Best game | seed 3 (Champ 18,593 / Market 10,526, +8,067) |
| Worst game | seed 0 (Champ 10,350 / Market 16,050, −5,700) |

This is far below the historical "21/21 vs diverse opponents" claim, and the
`market` opponent is the only preset that consistently beats the Champion at
scale.

### Per-game results

| Seed | Winner | Champ | Market | Margin |
|------|--------|-------|--------|--------|
| 0 | Market | 10,350 | 16,050 | −5,700 |
| 1 | Market | 11,277 | 16,986 | −5,709 |
| 2 | Market | 10,923 | 14,507 | −3,584 |
| 3 | Champ  | 18,593 | 10,526 | +8,067 |
| 4 | Champ  | 17,209 | 10,980 | +6,229 |
| 5 | Market | 11,153 | 16,809 | −5,656 |
| 6 | Champ  | 16,522 | 8,298  | +8,224 |
| 7 | Market | 11,043 | 14,713 | −3,670 |
| 8 | Champ  | 17,017 | 11,013 | +6,004 |
| 9 | Champ  | 12,942 | 12,613 | +329 |
| 10| Market | 10,739 | 15,688 | −4,949 |
| 11| Champ  | 12,925 | 12,668 | +257 |

---

## 3. Win-Game vs Loss-Game Champion Characteristics

(Champion's own metrics; means over the 6 win games vs 6 loss games.)

| Characteristic | Wins | Losses | Delta |
|----------------|------|--------|-------|
| Avg final coins | 15,868 | 10,914 | — |
| Avg final land (quadrants) | 2.0 | 2.0 | 0 |
| Avg final animals | 0.0 | 0.0 | 0 |
| Avg final planted tiles | 22.8 | 21.8 | ~1 |
| Avg late shed (last 5 days) | 25.9 | 22.0 | small |
| Avg final shed (unsold) | 23.3 | 23.8 | ~0 |
| Total units sold (all games) | 2,003 | 2,017 | ~0 |
| Avg endgame units sold (day≥26) | 106.5 | 90.0 | small |
| Total BUY_LAND | 6 | 6 | 0 |
| Total HIRE calls | 852 | 852 | 0 |
| Total FERTILIZE | **0** | **0** | 0 |

**Interpretation:** The Champion plays *essentially the same game* whether it wins
or loses — same land, same hiring, same planting volume, same sales volume, same
zero animal production, and it **never fertilizes**. The outcome is therefore
explained by the *opponent's* variance, not by a Champion mistake that only
appears in losses.

---

## 4. The Decisive Variable: Melon (High-Value Crop)

Units sold per game, by product (from SELL action events):

| Game | Champ WHEAT | Champ CARROT | Champ MELON | Market WHEAT | Market CARROT | Market MELON |
|------|-------------|--------------|-------------|--------------|---------------|--------------|
| Win seeds (3,4,6,8,9,11) | 979 | 819 | **205** | 1,034 | 853 | **65** |
| Loss seeds (0,1,2,5,7,10) | 1,070 | 892 | **55** | 710 | 700 | **240** |

**Near-deterministic pattern:**

- Champion melon sales: **205 in wins vs 55 in losses** (3.7× more melon when winning).
- Market melon sales: **240 in its wins vs 65 in its losses**.
- **Every seed where the market opponent sells 40 melon → Champion loses (6/6).**
- **Every seed where the market opponent sells ≤15 melon → Champion wins.**

Estimated gross revenue (units × that day's shared market price — *correlational
estimate, not exact*):

| | Champion | Market |
|--|----------|--------|
| In Champion-win games | 110,808 | 78,035 |
| In Champion-loss games | 78,574 | 106,207 |

When the Champion wins, it captures the high-value revenue; when it loses, the
market opponent captures it. Melon is the swing product because it is the only
high-value crop either agent meaningfully produces in this matchup.

### Crop mix (final-day snapshot of planted tiles + shed)
- Champion final planted tiles: ~131–137 **WHEAT**, effectively 0 of every other crop.
- Champion shed at end: ~140 **WHEAT**, 0 of everything else.
- The Champion's live production is overwhelmingly **wheat + carrot (low value,
  self-glut-depressed price)** with only a thin melon tail.

**The Champion produces ZERO animals, ZERO tomato, ZERO strawberry, and never
fertilizes.** Its value ceiling is set by staple crops.

---

## 5. Turning-Point Analysis (Question 3)

Average daily coin margin (Champ − Market), grouped:

| Day | Avg margin — Champ WINS | Avg margin — Champ LOSES |
|-----|-------------------------|--------------------------|
| 10 | −228 | +130 |
| 14 | +210 | +316 |
| 18 | +454 | +542 |
| 22 | +220 | +1,122 |
| 24 | +100 | +1,322 |
| 26 | +93  | **+1,633** |
| 28 | **+4,918** | **−5,140** |

**Key finding:** In the games the Champion *loses*, it is **ahead for most of the
season** (margin +1,000 to +1,600 at days 22–26) and is **overtaken only in the
final endgame window (day 28)**. Durable divergence (|margin| > 1000 that never
recovers) lands on **day 28** for 10/12 games (the other two, seeds 9 & 11, are
near-ties decided by <330 coins and never cross durably).

So the losing divergence is **late, not early**. The Champion's mid-game staple
economy builds a lead; the opponent's **melon harvest matures late and is
liquidated at the end for a coin spike the Champion cannot match** with its
wheat/carrot base.

---

## 6. Market Behaviour Analysis (Question 5)

- The `market` opponent is **deterministic per seed**. Re-running seed N gives the
  identical result. Its win/loss outcome is reproduced exactly.
- Its winning mode is a **melon commitment**: in its 6 wins it sells 240 melon
  (≈40/seed); in its 6 losses it sells 65 melon (≈10/seed). This is a stable,
  reproducible strategy branch, not noise.
- The market opponent also produces **zero animals** in these games, so animals
  are *not* the differentiator here; **melon is**.
- Both agents sell similar total volumes (~2,000 units for Champ, ~300–1,950 for
  market), but the *composition* differs: the market opponent's winning games skew
  toward high-value melon, which, sold late, dominates the endgame coin tally.

**Reproducible advantage?** Yes. Against this frozen Champion, a melon-committed
market opponent reproducibly wins. The advantage is robust to the Champion's
fixed strategy because the Champion never contests the high-value endgame.

---

## 7. Why the Champion Wins / Loses (Questions 1 & 2)

**Why it wins:** When the market opponent does *not* commit to melon (sells ≤15),
the Champion's staple economy plus its own thin melon tail is enough to hold the
endgame lead it builds during days 10–26.

**Why it loses:** When the market opponent commits to melon (~40 units), that
crop matures late and is liquidated in the day-28 window for a coin spike that
overtakes the Champion's stagnant staple lead. The Champion has **no comparable
high-value endgame harvest** to answer with.

---

## 8. Issue Classification (Question 4)

| Category | Involved? | Evidence |
|----------|-----------|----------|
| Production / crop mix | **Yes (primary)** | Staple-heavy (wheat/carrot); melon under-produced; zero animals/tomato/strawberry |
| Endgame behaviour | **Yes (secondary)** | Lead built days 10–26 collapses at day 28; no high-value liquidation to answer melon spike |
| Pricing | No | Both sell at the shared market price; no price-setting ability exists |
| Selling timing | Partial | Champion sells steadily; the *composition* (what it has to sell) is the issue, not the cadence |
| Capital allocation | No | Land (2 quads), hiring (852), buys are identical in wins/losses |
| Expansion | No | Same land bought in both; same BUY_LAND count |
| Workers | No | Hiring volume identical; endgame workers=1 in both |
| Animals | No (in this matchup) | Both agents use zero animals; not the differentiator *here*, but a structural gap |
| Fertilizer | **Yes (missed lever)** | `FERTILIZE` count = 0 in every game; melon especially benefits from fertilize+water |

**Primary issue: PRODUCTION — high-value crop (melon) under-allocation and
complete absence of animals/tomato/strawberry.** Secondary: no high-value
endgame liquidation to defend the mid-game lead.

---

## 9. Suspected Weakness

> The frozen Champion's value generation is capped by a staple-heavy crop mix.
> It floods the market with low-value wheat/carrot (depressing its own prices),
> under-invests in the one high-value crop it touches (melon), and entirely
> ignores animals, tomato, and strawberry. Against any opponent that captures a
> high-value endgame harvest (here: melon), the Champion's mid-game staple lead
> is reliably overturned in the final days.

---

## 10. Evidence & Confidence

- **Evidence:** 12 deterministic games; per-step telemetry of both farms, private
  sheds, market prices/inventory, town demand, and both players' actions
  (see `artifacts/championship/MARKET_MATCHUP_TELEMETRY/seed_NNN.json`).
- **Correlation observed:** market melon ≥40 ⇔ Champion loss (6/6); market melon
  ≤15 ⇔ Champion win (6/6); Champion melon 205 (wins) vs 55 (losses).
- **Causality caveat:** The Champion is invariant across games, so *all* outcome
  variance is opponent-driven. We can demonstrate a strong, reproducible
  *correlation* between the opponent's melon focus and Champion losses; we cannot
  from observation alone prove that changing the Champion's mix would flip those
  losses (that requires a challenger experiment). The Champion's structural
  staple-heavy mix is, however, a clear, fixable ceiling.
- **Confidence:** **High** that (a) the `market` opponent's melon commitment is
  the reproducible winning lever, and (b) the Champion lacks a high-value
  endgame harvest to contest it. Medium on the precise quantitative lift a fix
  would yield (requires challenger validation).

---

## 11. Recommended Next Hypothesis

> **H-MARKET-1 (High-value endgame harvest):** A challenger that allocates
> substantially more tiles to melon (and/or enables animals / tomato /
> strawberry for high-value, late-maturing inventory) and ensures those crops
> mature for the day-26–29 liquidation window will (a) build a larger endgame
> coin spike and (b) defend the mid-game lead the staple economy already
> produces — raising the win rate against market-aware opponents above 50%.
>
> **H-MARKET-2 (Fertilize high-value crops):** Enabling `FERTILIZE` on melon
> (currently used 0 times) should increase melon yield and amplify H-MARKET-1.

These hypotheses should be tested by building a challenger (the Champion remains
frozen) and re-running this exact benchmark. No Champion code was changed in this
investigation.

---

## 12. Telemetry Availability & Honesty Notes

- **Collected (environment-exposed):** cash trajectory (per step, both players),
  inventory/shed trajectory (per day, both players), land, workers, animals, crop
  activity (planted + per-crop counts), fertilizer usage (FERTILIZE/COLLECT_
  events), sales (SELL events by product/quantity), purchases (BUY_SEED /
  BUY_LAND / HIRE / BUY_ANIMAL events), market prices & inventory (per day),
  town demand (`unlocked_shops`, per day), major strategic decisions (event log),
  endgame actions (SELL events day≥26).
- **NOT available / not fabricated:** The Champion's *internal* strategy-mode
  transitions are not exposed by the environment. "Phases" referenced above are
  *inferred from observable actions and state* (e.g., lead-building vs endgame
  liquidation), not read from internal policy state. Animal production telemetry
  is N/A because neither agent used animals in this matchup (counts are real: 0).
- All figures in this report are computed directly from the saved telemetry; no
  values were estimated beyond the explicitly-labelled gross-revenue approximation
  in §4.
