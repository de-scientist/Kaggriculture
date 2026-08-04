# Kaggriculture AI Platform — Technical & Architectural Specification

**Version:** 1.0 (Stage 0 — Technical Discovery & System Design)
**Status:** Authoritative blueprint. Governs implementation in Stages 1–4.
**Sources of truth:** `kaggle_environments/envs/kaggriculture/kaggriculture.py` (engine), `README.md`, `AGENTS.md` (official docs). All are preserved exactly; this document layers architecture **on top** of them.

---

## Executive Summary

Kaggriculture is a deterministic-ish, two-player, full-information+private-inventory farming simulation shipped by Kaggle in the `kaggle-environments` package. Two agents each manage a 10×10 farm partitioned into four 5×5 quadrants, buy seeds/livestock, grow one-time or ongoing crops, raise animals, hire daily farmhands, buy land, feed/water/care, and sell produce into a shared dynamic market over 720 turns (24 ⊥ 30). Victory is the highest bank balance at season end.

This document is the **Stage 0 deliverable**: a complete reverse-engineering of the official engine, a full game-mechanics analysis, an Observation/Action adapter + Domain-Driven Design model, a layered Clean Architecture, an AI decision pipeline, a 9-stage strategy roadmap, engineering standards, a test strategy, and a risk register. **Zero production AI is written here.** The architecture is deliberately built so that Stages 1–4 (deterministic → heuristic → economic → utility/MCTS) can be swapped behind stable interfaces without touching official code.

**Key strategic insight for later stages:** the market price function is fully known and invertible, town demand is deterministic per seed, and crop/animal yield math is closed-form. This makes the game unusually amenable to **planned, model-based** optimization long before any RL is needed. The dominant design constraints are (a) the two *simultaneous-but-per-unit-lockstep* market clearing rule, (b) the shed-capacity bottleneck of 100, and (c) finite farmer/hand *movement* latency on the board.

---

## 1. Repository Analysis

### 1.1 Overall architecture

The official repository is `Kaggle/kaggle-environments`, and the game lives in `kaggle_environments/envs/kaggriculture/`:

```
kaggriculture/
├── AGENTS.md              # onboarding + git workflow (agent-facing guide)
├── README.md              # canonical rules doc (mirrors this analysis)
├── kaggriculture.py       # THE ENGINE (interpreter/renderer/agents/config)
├── kaggriculture.json     # environment `specification` metadata (name, how to run, etc.)
└── visualizer/default/…   # optional browser HTML renderer
```

The framework (`kaggle_environments`) runs an **`interpreter(state, env)`** function each step: it takes the prior step's state/actions and returns the next state. Agents are plain callables `agent(obs) -> action_dict`. This is the Kaggle Environment protocol. We must not alter it.

### 1.2 Entry point

- `make("kaggriculture", configuration={...})` → environment object.
- `env.run([agent0, agent1])` runs the full episode. Agent may be a callable, a string name (`"pass"`, `"random"`, `"starter"`), or a path to a `.py` file containing `agent(obs)`.
- The submission contract (Kaggle): a `main.py` at archive root exposing `agent(obs)`.

### 1.3 File-by-file analysis

| File | Purpose | Responsibilities | Dependencies | Extension points |
|---|---|---|---|---|
| `kaggriculture.py` | Engine | Game state init, action application, market lockstep, town demand, day refresh, decay, weeds, end-of-day, reward, renderer, built-in agents | `json`, `math`, `random`, `os.path`, `kaggle_environments.utils.resolve_episode_seed` | The three built-in agents (`pass`, `random`, `starter`) are **extensible baselines**. `MARKET_PARAMS`, `CROPS`, `ANIMALS`, `SHOPS` are data tables — configuration seams, not code to copy. |
| `AGENTS.md` | Onboarding | Rules summary + local/Kaggle workflow | README | — (documentation) |
| `README.md` | Rules | Canonical game rules + tables | — | Source for domain constants (mirrored, not duplicated). |
| `kaggriculture.json` | Env metadata | Framework spec file (name, version, `interpreter`/`renderer` pointers, `agents`) | framework | Registers built-in agents. |

### 1.4 Agent lifecycle (per step)

1. Framework reads each agent's last action.
2. `interpreter(state, env)` is called with the raw state.
3. `_initialize` runs only on step 0 (builds `farms`, `private`, `market`, `town`, seeds RNG).
4. Farmer + each hand action applied via `_apply_unit_action` (with atomic PLANT dedup block).
5. `_process_market` runs the per-unit lockstep clearing for both players.
6. `_town_consume` drains market inventory (shops + town center), then `_refresh_prices`.
7. `_decay_plants` applies over-mature decay.
8. On the last turn of a day, `_end_of_day` refreshes plants/animals, spawns weeds, drops inventories to shed, resets farmers/hands/hires, and unlocks a town shop.
9. `day`/`hour`/`step` advance; on the final recorded step, each player's **`reward` is set to their float `money`** and `status="DONE"`.

### 1.5 Pre-existing constants & helpers we must USE (not reinvent)

- `CROPS`, `ANIMALS`, `PRODUCTS`
- `MARKET_I0 = 10000`, `PRICE_FLOOR = 1`
- `MARKET_PARAMS` (per-resource `base/I0/T/below_func/below_target/above_func/above_target`)
- `FARMER_MOVES`, `LAND_ORDER=["NE","SW","SE"]`, `LAND_PRICES=[1000,2000,4000]`
- `FARM_HAND_COST_MULT=1`
- `SHOPS` (8 shops + `TOWN_CENTER_PRODUCTS` + `TOWN_CENTER_DEMAND_SCHEDULE`)
- `market_price(item, inventory, params)`, `_shape(func, x)` — **public-ish math we mirror in our own `economy` module** (see 1.6).
- Helpers `get`, `_quadrant_of`, `_shed_access_tiles`, `_is_shed_adjacent`, `_fib`, `_hire_cost`, `_spawn_hand`.

> **Rule:** never re-implement engine internals; parse/observe their outputs and reproduce *only* pure-math models (price, yield) that the engine itself documents. Any engine constant we need downstream is derived from the observation or read from config, never hard-coded twice.

### 1.6 Critical engine mechanics confirmed from source (reverse-engineered)

Below are behaviors that the docs under-specify but the source proves. Build future logic on these facts.

- **Planting day counts as unwatered**: `_new_plant` sets `consecutive_unwatered=1`.
- **One-time crop water bonus window** = `ceil(max_yield_day/2) … max_yield_day`; bonus = `+1/day`, or `+2` if `fertilized_until_day >= day` AND watered. Capped at `max_yield`. `_new_plant` gives one-time crops `yield_units=1` at birth.
- **`FERTILIZE`** consumes 1 fertilizer from inventory, sets `fertilized_until_day = day+2` (3 days inclusive). Player must carry fertilizer to the tile.
- **Ongoing crops**: base scheduled yield `+1` (or `+2` if watered AND fertilized) on each interval anniversary; `yield_units` capped at `max_yield`; `max_lifespan_step` becomes `(next_day+1)*turns_per_day` once `production_count == max_yield`. Holdings never exceed `max_yield`.
- **Decay (one-time)** begins at `max_lifespan_step = (planted_day + max_yield_day + 1)*turns_per_day` and drops `yield_units` by 1 every **2 steps** (`(step-mls)%2==0`).
- **Animals**: production on each `interval` anniversary *after* `first_yield_day`; yield = `min(max_held, current + base1 + bonus)`. Care bonus requires `fed_today`; if unfed on a production day the bank (`pending_care_bonus`) resets to 0. `CARE` on a fed day adds `+1` to the bank. `fertilizer_available=True` set at every end-of-day, cleared by `COLLECT_FERTILIZER` (+1 fertilizer).
- **Animal escape** on `consecutive_unfed>=2` → tile becomes empty `{kind:<structure>}` (structure survives).
- **Market clearing is per-unit lockstep across both players**, quoted at the *same* pre-commit inventory. SELL quotes pre-sell price and adds supply; BUY_PRODUCT quotes post-buy price (`-1`) and removes supply. `$1` sales do **not** add supply. Orders beyond `maxMarketOrdersPerTurn` (10) are truncated **up-front**.
- **HIRE / BUY_LAND are atomic** and processed before per-unit orders each turn, in player order.
- **BUY_SEED/BUY_ANIMAL** respect money; **BUY_PRODUCT/BUY_ANIMAL** also respect `shedCapacity` (bought goods land in shed).
- **Movement onto LOCKED tiles is allowed** (hands may spawn there); tile-ops no-op on LOCKED.
- **Weed spawn** uses a seeded `random.Random((seed*1_000_003)^day)` per day — reproducible.
- **Town shop unlock** at `next_day % shop_interval == 0`, random among unused, stable RNG.
- Player `reward` (non-normalized) = final float `money`. Win/Tie = compare rewards; ties allowed.

### 1.7 Security / robustness constraints for our agents

- Invalid actions are **silent no-ops** — our validator must pre-filter rather than rely on the engine.
- Agent submission runs untrusted-feeling, resource-limited; our agent must be **bounded-time and bounded-memory** per step (budget ~sub-second; see §13 latency risk).
- Only `kaggle_environments` (and stdlib + a tiny allowed ML stack at later stages) is available in the remote runtime.

---

## 2. Game Analysis (Mechanics Reverse-Engineering)

### 2.1 Episode lifecycle

```
Initialize(farms, private, market=I0 base, town={})   [step 0]
   └─ repeat 720 times (default):
        day = step // 24,  hour = step % 24
        read actions → validate → apply unit actions (lockstep)
        → market lockstep → town consume → refresh prices
        → decay plants
        → (if last hour) end-of-day refresh
        → advance step/day/hour
   └─ terminal: reward = money, status = DONE
Winner = max(last money); tie is a tie.
```

### 2.2 Daily cycle

- 24 turns/day. `hour` 0…23. `day` 0…29.
- End-of-day (hour 23): water/feed reset, unwatered/unfed counters increment, weeds spawn, inventories dropped to shed, farmer+hands return to shed-adjacent spawn, `hires_today=0`, hands cleared, one town shop may unlock.
- **Replanting cadence matters**: one-time crops die (→weed) if unwatered two *consecutive end-of-days*.

### 2.3 Turn-processing order (authoritative)

1. Validate + record simultaneous unit actions (with atomic PLANT guard).
2. Apply player unit actions (farmer idx 0, then hands idx 1..n).
3. Process market queue (atomic HIRE/BUY_LAND first, then per-unit lockstep SELL/BUY).
4. Town consumes (shops every `townShopSellInterval`, center every `townCenterSellInterval`), refresh prices.
5. Decay plants.
6. End-of-day refresh if last hour.
7. Advance counters; on terminal step assign rewards + DONE.

### 2.4 Movement / energy

- **No energy system.** Each unit independently gets exactly **one** op per turn.
- Movement is 4-dir (N/S/E/W), 1 cell/turn, on/off-board clamp, LOCKED ok.
- The binding constraint is **latency**: a farmer/hand must physically travel to a tile to plant/water/harvest/build, and to the shed-adjacent ring to pickup/place/drop. Pie-of-latency vs. yield is the core scheduling problem solved in Stages 3–4.

### 2.5 Crop lifecycle

| Crop | Type | Seed $ | Day first | Interval | Max yield | Base $ | Water-bonus |
|---|---|---|---|---|---|---|---|
| WHEAT | one-time | 10 | 2 | — | 6 | 25 | window 2–4 |
| CARROT | one-time | 20 | 2 | — | 4 | 35 | window 2–3 |
| TOMATO | ongoing | 50 | 8 | 1 | 4 | 60 | 2 if fert+water |
| STRAWBERRY | ongoing | 100 | 10 | 2 | 4 | 120 | 2 if fert+water |
| MELON | one-time | 80 | 10 | — | 6 | 250 | window 6–12 |

One-time: plant → water in bonus window (+1·days, +2 if fertilized, capped) → harvest any day ≥ first_yield → tile cleared. Decay after `(planted+max_yield+1)` days at −1/2steps.
Ongoing: plant → interval production (+1, or +2 if watered+fertilized, capped max_yield) → harvest anytime; decay begins one day after reaching max_yield production count.

### 2.6 Animal lifecycle

| Animal | Cost $ | Structure | Day first | Interval | Max held | Product $ |
|---|---|---|---|---|---|---|
| GOOSE | 300 | COOP | 4 | 1 | 4 | EGG 50 |
| COW | 400 | PASTURE | 8 | 2 | 6 | MILK 160 |
| SHEEP | 500 | PASTURE | 6 | 3 | 6 | WOOL 200 |

Build structure → buy animal → PLACE (standing on structure) → feed wheat daily → CARE to bank bonus → production on anniversary → HARVEST product → COLLECT_FERTILIZER. Escape on 2 unwatered/unfed end-of-days (structure remains). Animals require ongoing wheat feed (a recurring wheat sink and a reason to keep a wheat ramp alive).

### 2.7 Worker lifecycle

- Main farmer: permanent. Hands: hired daily via `HIRE` (market, atomic), cost `fib(hires_today)` × mult (1,1,2,3,5,8,13,21,…), **reset each morning**. Hands spawn on a shed-access tile (NWSE preference, min-occupancy tie-break), vanish at end of day. Each hand has its own inventory, dropped to shed at night.

### 2.8 Hiring system

- `HIRE` is a market order; cheap early (1¢,1¢,2¢…), Fibonacci-escalating, so bulk hiring is a non-starter; 3–5 hands/day is a typical economic sweet spot. Hands drastically cut movement latency (parallel tile work) at the cost of a daily recurring fee that **resets** — so hiring is a per-day decision, not a per-season one.

### 2.9 Market system

Seeds/animals: unlimited, fixed price. Sell prices: dynamic, persistent, deterministic function of shared inventory:
```
price(inv) = base ± amp·f(|inv−I0|),  amp = target·base/f(T),  floor $1, round
sign = + scarcity (inv<I0), − glut (inv>I0)
f ∈ {linear, sq, sqrt, log, log10}; log = ln(1+x)
```
- `I0 = 10,000`. Inventory drains via town (free) + player `BUY_PRODUCT`(wheat/fert only); rises via player sells.
- **Quote convention:** BUY quotes post-inventory (so buy→sell round-trip nets zero); SELL quotes pre-inventory. Per-unit, simultaneous, both players see same pre-commit inventory.
- **Premium goods** (base>100: strawberry, melon, milk, wool) have `above_target>1` → even mild gluts crash to $1. Timing/bundling sells matters far more for these.
- WHEAT/FERT are the only buyable products. FERT can never be sold.

### 2.10 Town demand

- Town center: 1 of each non-FERT product every 12 turns; ×2 after day 10, ×4 after day 20 (schedule thresholds `(20,4),(10,2),(0,1)`).
- Shops unlock every 3 days (random, stable RNG), stay forever, consume every demanded product every 4 turns; single-product shops consume 2×.

| Shop | Demands |
|---|---|
| BAKERY | egg, wheat |
| PIZZA_SHOP | milk, tomato, wheat |
| BRUNCH_SPOT | egg, wheat, strawberry |
| YARN_STORE | wool (2×) |
| ICE_CREAM_SHOP | strawberry, milk, wheat |
| PET_CAFE | carrot (2×) |
| SMOOTHIE_SHOP | strawberry, milk |
| FARMERS_MARKET | wheat, carrot, tomato, strawberry |

Town monotonically grows demand → steady downward drift of prices over the season; agents must sell into an *ever-softening* market.

### 2.11 Inventory / storage

- Three storage loci: **seeds** (separate, no cap, consumed by PLANT), **shed** (cap 100 non-seed items), and per-unit **field inventories** (carried). Field inv + shed both capped at shedCapacity aggregate — the 100-item shed is the binding constraint. Overflow is silently discarded (both on PLACE-shed-drop and end-of-day drop). `BUY_PRODUCT`/`BUY_ANIMAL` also require shed room.

### 2.12 Land expansion / quadrants

- 10×10, four 5×5 quadrants (NW/NE/SW/SE by x<5,y<5). NW unlocked. Order `NE→SW→SE`, costs `1000/2000/4000`. Unlocking flips LOCKED→None tiles. Expansion is a strategic pacing decision (capital vs. production surface vs. near-end uselessness).

### 2.13 Fertilizer

Buy-only (never sellable), `$100` each (variable). +2/day water bonus on one-time crops for 3 days; doubles ongoing daily production if watered. Must be purchased, carried to tile, applied.

### 2.14 Selling / buying

- Selling: SELL N units from shed, per-unit lockstep, price drifts down as you contribute supply (self-induced glut). Split large sales across turns *or* time them to premium window.
- Buying: BUY_SEED(crops), BUY_ANIMAL, BUY_PRODUCT(WHEAT/FERT only), plus atomic HIRE/BUY_LAND.

### 2.15 Weeds

- `weedSpawnChance=0.005`/empty-tile/day, stable RNG. Must `DIG` to clear (costs a unit-turn but no money). Early mornings after a day of high farm utilization accumulate weeds; hidden opportunity cost of idle tiles.

### 2.16 Resource generation / consumption summary

- Generate: harvested produce, animal products, fertilizer (1/animal/day via COLLECT).
- Consume: seeds (PLANT), wheat (FEED, 1/animal/day), fertilizer (FERTILIZE), money (buy/hire/land), tile-time (no energy, but one op/turn/unit).
- Wheat is a **dual resource**: a plantable crop **and** a feed input → strategic requirement to sustain animals.

### 2.17 Winning / losing

- Win = max final money. No mid-game elimination; "losing" is only relative score at the end. Unsold shed inventory is worthless at termination. Therefore convert-on-time terminal selling is critical.

### 2.18 Unknown mechanics & assumptions (to re-verify against frozen engine tag)

- Task expects a **frozen official snapshot**; we pin the `kaggle-environments` version and reference that tag (risk §13.1).
- Assumed default config everywhere unless `configuration` overrides are observed.
- Assumed no invisible random events beyond weeds + shop selection (both seeded/reproducible).
- `LOG10` shape exists in `_shape` but no product uses it — keep for parity.
- Movement allowed on LOCKED; tile ops blocked. We encode this in the action validator.

---

## 3. Observation Model + Adapter

We do **not** redesign the observation. We build an **ObservationAdapter** that converts the raw official `obs` into rich, typed, validated **domain objects** (§5). The adapter is the only place that touches raw dicts; everything downstream works on domain objects.

### 3.1 Official observation schema (field reference)

| Field | Type | Owner | Lifecycle | Change freq | Meaning |
|---|---|---|---|---|---|
| `player` | int | per-agent | constant | never | 0 or 1 index into `farms` |
| `step` | int | shared | rises | every turn | global turn counter (framework) |
| `day` | int | shared | rises | per 24 turns | season day |
| `hour` | int | shared | rises | every turn | turn within day |
| `farms[]` | list | shared | per-player state | any | public farms: `money`,`tiles[][],`farmer`,`hands`,`unlocked_quadrants`,`hires_today` |
| `farms[i].money` | float | public | — | on buys/sells | bank balance |
| `farms[i].tiles` | 2D | public | set by engine | per actions/refresh | per-tile state (None/LOCKED/plant/weed/structure) |
| `farms[i].farmer` | [x,y] | public | — | per move | main farmer pos |
| `farms[i].hands` | [[x,y]] | public | — | per move/hire | hired-hand positions (today) |
| `farms[i].unlocked_quadrants` | list[str] | public | monotonic | on BUY_LAND | NW, then NE/SW/SE |
| `farms[i].hires_today` | int | public | — | per HIRE | drives next HIRE cost |
| `market.inventory` | dict[str,int] | shared | — | per sell/buy/town | supply by product |
| `market.prices` | dict[str,int] | shared | — | refreshed | current rounded sell price |
| `town.unlocked_shops` | list[str] | shared | monotonic | per unlock | active shops today |
| `private.shed` | dict[str,int] | private | — | per pickup/place/drop/sell | non-seed storage (cap 100) |
| `private.seeds` | dict[crop,int] | private | — | per buy/plant | seed bank (uncapped) |
| `private.inventories` | list[dict] | private | — | per pickup/harvest | [farmer,*hands] carried items |

Tile variants (tiles[y][x]):
- `None` empty unlocked; `"LOCKED"` locked quadrant.
- Plant: `{kind, crop, planted_day, watered_today, consecutive_unwatered, yield_units, max_lifespan_step, fertilized_until_day}`.
- Weed: `{kind:"WEED"}`.
- Structure: `{kind:"COOP"|"PASTURE", animal?, placed_day, yield_units, fed_today, consecutive_unfed, cared_today, fertilizer_available, pending_care_bonus}`.

### 3.2 Adapter contract

```python
# interfaces/observation.py (design only — interface, no impl logic)
class IObservationSource(Protocol):
    def raw(self) -> dict: ...
    def to_domain(self) -> "GameState": ...

class ObservationAdapter:
    """Only component that reads the official obs. Pure, deterministic, cached off."""
    def __init__(self, config: "Config"): ...
    def adapt(self, raw: dict) -> "GameState": ...
    def last_raw(self) -> dict: ...
```

Responsibilities: type-coerce with a lenient read (tolerate keys via `.get`), map `farms` → `Player`/`Farm` domain graphs, preserve **all** fields verbatim for round-trip fidelity, and expose provenance (which fields came from where). It must throw a typed `InvalidObservationError` if the schema drifts (see §11 exceptions) so we fail loudly on repo-rule changes.

### 3.3 Extension note

Later stages add **inferred fields** (opponent production estimates, market-price model outputs) on separate read-only attributes of the domain state — never on the raw observation.

---

## 4. Action Model + Adapter

### 4.1 Official action catalog

Unit actions (farmer/hand), `[op, ...args]`:

| Op | Inputs | Preconditions | Postconditions | Failure cases |
|---|---|---|---|---|
| NORTH/SOUTH/EAST/WEST | — | in-bounds dest (LOCKED ok) | move unit | out-of-bounds no-op |
| PASS | — | — | nothing | — |
| PICKUP | item[, n] | shed-adjacent; shed has item | transfers to inventory | not adjacent / empty |
| DROP | — | shed-adjacent | dumps inventory→shed (cap) | not adjacent |
| PLACE | item[, n] | animal→matching empty structure OR shed-adjacent | place animal / shed-drop | wrong tile / full |
| PLANT | crop | empty tile; seeds>0; atomic-block passes | seed consumed, plant born (unwatered=1) | tile occupied / no seed / blocked |
| WATER | — | plant; not already watered | watered_today=True, yield bonus | non-plant / already watered |
| HARVEST | — | yield_units>0; mature if ongoing | produce→inv; one-time tile cleared | none / immature |
| FERTILIZE | — | plant; inventory has fertilizer | fertilized_until_day=day+2 | no fertilizer/non-plant |
| BUILD_COOP / BUILD_PASTURE | — | empty tile | structure placed | occupied |
| FEED | — | animal; inventory has wheat; not fed | fed_today=True | no wheat / not animal |
| COLLECT_FERTILIZER | — | animal has fertilizer_available | +1 FERT, cleared | none available |
| CARE | — | animal; not cared today | cared_today=True (banks bonus tonight) | not animal / already cared |
| DIG | — | non-empty non-animal tile | tile→None | empty / animal tile |

Market orders `[op, ...args]` (∩ 10/turn before truncation):

| Op | Inputs | Preconditions | Postconditions | Failure |
|---|---|---|---|---|
| BUY_SEED | crop, n | money≥n·seed$ | seeds+=n | insufficient money (partial stop) |
| BUY_PRODUCT | item, n | WHEAT/FERT; money; shed room | shed+=n; inv drain | money/shed full |
| BUY_ANIMAL | animal, n | money; shed room | shed+=n | money/shed full |
| SELL | item, n | shed has item | money+=price·units; supply+= (unless $1) | none in shed |
| HIRE | — | money≥fib(hires_today) | hires_today+, hand spawned | insufficient money |
| BUY_LAND | — | money≥next land price | unlock quadrant | insufficient money / all owned |

### 4.2 Opportunity cost & expected ROI (analytical summaries to feed later ROICalculator)

- **Movement**: 1 action/unit/turn = 1 tile-token. A hand cycles ~travel distance; ROI on a hand ≈ throughput gained / fib-cost.
- **Watering window** for one-time crops: water on *every* window day adds +1 yield (fertilized +2) → the biggest low-capex lever. Missed water = lost yield, not just weed risk.
- **HARVEST early** on one-time crops frees the tile for the next planting (higher cadence) but with smaller bundle; for ongoing crops harvest is a storage/liquidity timing choice.
- **FERTILIZE** ($100, 3 days) → up to +2/day vs +1 → ~+$ over the window on melon/strawberry; marginal but decisive on premium crops.
- **Selling timing**: SELL quote is pre-inventory and self-supply pushes price down; premium goods → $1 floor after mild glut; **sell in small batches across turns** or before town glut.
- **BUY vs SELL round-trip nets zero** on unchanged market → don't churn wheat.

### 4.3 Action adapter (design)

```python
# interfaces/actions.py
class BoardAction(Protocol):          # a validated domain intent
    def to_official(self) -> list: ...   # emits [op,*args]
    def desc(self) -> str: ...           # explainability
    def cost_probe(self, state) -> float: ...
class MarketOrder(Protocol):
    def to_official(self) -> list: ...
    def budget(self, state) -> int: ...

class ActionSerializer:
    """Converts validated domain actions → official action dict"""
    def serialize(self, farmer: BoardAction,
                  hands: list[BoardAction],
                  market: list[MarketOrder],
                  *, plan: "Plan") -> dict: ...
```

Pipeline for each candidate: **official intent → domain BoardAction → `ActionValidator` (§8) → `ActionSerializer` → official op**. Validation mirrors engine preconditions 1:1 (§4.1) so we never rely on silent no-ops.

---

## 5. Domain Model (DDD)

Pure domain layer — **no serialization, no Kaggle API, no I/O**. Everything is methodless-ish value/entity objects with invariants enforced in `__post_init__` / factory builders.

### 5.1 Aggregate & entities

- **`Season`** (value): `turn_count`, `turns_per_day`, `days`; helpers `turn_of(day,hour)`, `day_of(turn)`, `is_last_hour(turn)`, `ends_at`.
- **`Turn`** (value): `day`, `hour`, `step`.
- **`GameState`** (AggregateRoot): owns `self`, `opponent`, `market`, `town`, `turn`, `season`, `config`. Root metering: identity is the full state (immutable per turn for simulation; snapshotable).
- **`PlayerState`** (entity): `farm: Farm`, `inventory: PlayerInventory`.
- **`Farm`** (entity): `owner`, `board_size`, `grid: Grid`, `farmer`, `hands`, `unlocked_quadrants`, `hires_today`, `money`.
- **`Grid`** (value, internal aggregate): maps (x,y)→`TileState`.
- **`TileState`** (abstract) + **`EmptyTile`**, **`LockedTile`**, **`PlantTile`**, **`WeedTile`**, **`StructureTile`** (with optional `Animal`), typed by `kind`.
- **`Crop`** (value): COW constants mirrored from `CROPS` + lifecycle rules (window, cap).
- **`Animal`** (value): from `ANIMALS`.
- **`PlayerInventory`** (entity): `shed: dict[Resource,Qty]` (cap), `seeds: dict[Crop,Qty]`, `field: list[dict]` (per-unit carried). Business rules: shed cap invariant.
- **`AgentUnit`**: `pos`, `field_inventory`, `role` (farmer|hand, index).
- **`Market`** (entity): `inventory: dict`, `prices: dict`, plus a `PriceModel` (economy) object for prediction.
- **`Town`** (entity): `unlocked_shops: set`, computes demand schedule.
- **`Shop`** (value): `name`, `demand_map`, `interval`, `multiplier`.
- **`Quadrant`** (enum): `NW,NE,SW,SE`; `price()`, `is_unlocked`.
- **`BoardAction`/`MarketOrder`** as in §4.3.

### 5.2 Invariants (enforced in domain)

- `0≤money`; shed sum ≤ shedCapacity; seeds ≥0; yield_units ∈[0, max_yield/max_held]; `fed_today/watered_today/cared_today` booleans reset each day; a tile is exactly one of the four states; quadrant NW always unlocked; hires_today ≥0; hands length == hires_today.

### 5.3 Relationships diagram

```
GameState
 ├─ Turn ── Season
 ├─ self ─ PlayerState ─ Farm(assets,money) + Inventory(shed,seeds,field)
 │                   └ Grid→TileState[kind]; Crop/Animal value objects
 ├─ opponent ┴ (seen from public obs; private hidden)
 ├─ Market ─ Market.PriceModel
 └─ Town ─ set<Shop>
```

---

## 6. System Architecture (Clean, layered — extending, not replacing)

```
┌────────────────────────────────────────────────────────────┐
│ Kaggle Agent Boundary (main.py) — submission surface        │
│   agent(obs) -> {farmer, hands, market}                     │
└──────────────────────────┬─────────────────────────────────┘
                           │ raw obs / official action dict
┌──────────────────────────▼─────────────────────────────────┐
│ L1  Adapters   (observation_adapter, action_serializer)     │
│     ONLY layer that touches official dict protocol          │
└──────────────────────────┬─────────────────────────────────┘
                           │ rich domain objects
┌──────────────────────────▼─────────────────────────────────┐
│ L2  Domain Model  (entities, invariants, value objects)     │
└──────────────────────────┬─────────────────────────────────┘
                           │ state + config
┌──────────────────────────▼─────────────────────────────────┐
│ L3  Decision Engine  (planners) → CandidateAction[]         │
│     crop/animal/market/expansion/worker planners            │
└──────────────────────────┬─────────────────────────────────┘
                           │ candidates (domain intentions)
┌──────────────────────────▼─────────────────────────────────┐
│ L4  Strategy Manager  (select strategy, tune weights)       │
│     - evaluation policy / utility functions / lookahead     │
└──────────────────────────┬─────────────────────────────────┘
                           │ scored, ranked intents
┌──────────────────────────▼─────────────────────────────────┐
│ L5  Action Validator  (mirror engine preconditions)         │
└──────────────────────────┬─────────────────────────────────┘
                           │ legal intents
┌──────────────────────────▼─────────────────────────────────┐
│ L6  Action Ranker  (aggregate scores, choose best per unit) │
└──────────────────────────┬─────────────────────────────────┘
                           │ chosen BoardAction / MarketOrder
┌──────────────────────────▼─────────────────────────────────┐
│ L7  Serializer → official action dict → back to Kaggle      │
└────────────────────────────────────────────────────────────┘
```

**Why each layer exists**
- **L1 Adapters** — both agents and engine speak the raw protocol; isolating it means a schema/rule change touches one module, and the domain stays stable.
- **L2 Domain** — the single source of truth for game facts; drives planners, validators, simulation, and tests from one model.
- **L3 Decision Engine** — produces candidate intents per planning concern; swappable planners.
- **L4 Strategy Manager** — the policy: "what kind of agent am I today" (timid wheat eco vs. aggressive melon gambler) with tunable utility weights.
- **L5 Validator** — mirrors official topology so we never emit a silent no-op.
- **L6 Ranker** — converts multi-objective scores into a single chosen action per unit (farmer + each hand + market list).
- **L7 Serializer** — emits the exact official dict.

**Compatibility guarantee:** `agent(obs)` in `main.py` is the only function the framework calls; it returns the official schema always. If any stage's internals change, `main.py` + serializers are unchanged.

---

## 7. Project Structure (modular extensions)

```
kaggriculture/                       ← official (unnamed) env inside kaggle-environments
├── main.py                          ← OFFICIAL submission surface (thin: agent(obs))
vendor/kaggle_environments/          ← pinned official engine (reference, read-only)

kaggriculture_ai/                    ← our package (extension root)
├── interfaces/                      ← protocols only (decision, planner, sim, rl, mcts, evolution)
├── adapters/
│   ├── observation_adapter.py
│   └── action_serializer.py
├── domain/
│   ├── entities.py  value_objects.py  invariants.py
│   ├── resources.py  quadrants.py  season.py
├── decision/
│   ├── engine.py        # orchestrates planners → candidates
│   ├── planner.py       # base Planner protocol
│   ├── crop_planner.py  animal_planner.py  market_planner.py
│   ├── expansion_planner.py  worker_scheduler.py
├── strategies/          # evaluators: deterministic, heuristic, economic, utility, mcts
├── planning/            # mid/long-horizon plans, cadence scheduling
├── economy/
│   ├── price_model.py   # mirrors & predicts market_price
│   ├── ro_analyzer.py   risk_analyzer.py
├── market/              # order builder, sell batching, town-demand forecast
├── crops/  animals/  workers/  inventory/
│   ├── (per-domain logic delegating to planners)
├── inventory/           # shed manager (cap enforcement, drop scheduling)
├── analytics/           # episode telemetry, explainability, metrics export
├── simulation/          # sim interface + fast pure-python engine wrapper (see §9)
├── optimization/        # MCTS / beam / genetic backends (Stage 5+)
├── rl/                  # future RL interface + env wrapper + trainers
├── utilities/           # timing budget, rng seeding, pathfinding
├── config/
│   ├── defaults.yaml    # our tunable knobs (strategy weights, schedules)
├── tests/               # unit / integration / replay / perf / stress / seed
├── experiments/         # A/B harness, parameter sweeps
├── benchmarks/          # match vs pass/random/starter/self, leaderboard sim
├── packaging/           # submission tar.gz builder (main.py at root)
```

**Interface contracts (public):**
- `Planner.generate(state) -> list[CandidateIntent]`
- `Strategy.score(state, intents) -> list[ScoredIntent]`
- `ActionValidator.validate(state, intents) -> list[ValidIntent]`
- `ActionRanker.choose(state, valid) -> Plan` (farmer+hands+market)
- `Simulation.step(state, Plan) -> GameState` (fast clone for lookahead)
- `PriceModel.price(item, inventory) / predict(item, horizon)`
- `RLEnv.wrap(env)`, `MCTS.select(node)`, etc. (Stage 5+) behind protocols.

**Dependencies:** `interfaces` ← everything; `domain` ← `economy`(pure math, no engine); all planners depend on `domain`+`interfaces`; orchestrators depend on planners; `main.py` depends only on `adapters`+`decision`+`config`. No module imports `kaggle_environments` except `main.py` and the `simulation` wrapper (kept isolated).

**Extension points:** registering a new `Planner`, swapping `Strategy`, adding a `MarketOrder` type, adding a simulation backend, dropping in a Gym/`EnvPool`-style RL wrapper.

---

## 8. AI Architecture (components via interfaces, Stage 1–4 focus)

Components communicate only through the protocols in `interfaces/`. Each is a thin abstraction now, with a Stage-appropriate implementation negotiated at runtime via **dependency injection + a strategy registry** (`config/`).

| Component | Responsibility | Interface | Stage-1 impl |
|---|---|---|---|
| DecisionEngine | Orchestrate planners, hold budget, handle conflicts | `IDecisionEngine` | sequential planner run |
| StrategyManager | Select current policy + weights | `IStrategy` | deterministic |
| ActionGenerator | Produce candidate intents per domain planning concern | `Planner` + sub-planners | greedy crop loop |
| ActionValidator | Mirror engine legality | `IActionValidator` | precondition check |
| ActionRanker | Multi-objective→one action per unit | `IActionRanker` | utility sum |
| CropPlanner | Cadence, watering window, fertilizer, harvest timing | `Planner` | window-watering planner |
| AnimalPlanner | Build/purchase/feed/care/collect / wheat sink | `Planner` | feed-first caretaker |
| MarketPlanner | Order construction, sell batching, buy timing | `Planner` | sell-on-harvest |
| ExpansionPlanner | When to buy land | `Planner` | threshold rule |
| WorkerScheduler | Assign each hand a tile job | `Planner` | nearest-job greedy |
| InventoryManager | Shed cap enforcement, drop/pickup scheduling | `IInventoryManager` | lazy drop |
| ROI Analyzer | Cost/benefit of intents | `IRoiAnalyzer` | per-crop simple payback |
| RiskAnalyzer | Downside (weed/escape/glut-pricefloor) | `IRiskAnalyzer` | penalty terms |
| Simulation Interface | Clone+advance engine for lookahead | `ISimulation` | (none/light in S1) |
| Explainability Engine | Log why each action chosen | `IExplainer` | structured log |
| RL Interface | Future training/eval | `IRLEnv` | stub |
| MCTS Interface | Future tree search | `IMCTS` | stub |
| Evolutionary Interface | Future GA/CMA | `IEvolution` | stub |

**Composition root** (in `main.py`): `build_agent(config) -> agent`. Reads `config.yaml`, constructs StrategyManager with the Stage's Strategy, wires planners/validator/ranker/explainer/simulation. Later stages only add new registrations — no call-site change.

---

## 9. Decision Pipeline (per turn)

```
Official obs
  → 1. ObservationAdapter.adapt  →   GameState (typed, validated, provenance)
  → 2. Domain objects built
  → 3. Generate Candidate Actions   (planners emit intents per concern)
  → 4. Validate Actions             (mirror-engine preconditions; drop illegal)
  → 5. Evaluate Strategies          (StrategyManager scores intents: utility/ROI/risk + lookahead)
  → 6. Aggregate Scores             (weighted multi-objective → per-intent total)
  → 7. Rank Actions                 (per unit: farmer + each hand; build market list)
  → 8. Choose Best Action           (respect per-unit "one op" constraint)
  → 9. Convert to Official Kaggle Action (ActionSerializer)
  → 10. Return {farmer, hands, market}
```

**Stage details**
- **1–2** adapts once; cache `GameState`; budget enforced.
- **3** planners propose non-overlapping intents; a hand-job scheduler assigns tiles to units; market planner proposes orders.
- **4** validator runs the §4.1 precondition table against current state (incl. shed cap, seeds, money, adjacency).
- **5–6** each valid intent scores a vector {expected immediate money, payoff delay, risk, resource-fitting}; utilities from Strategy weights; lookahead (Stage ≥4) calls `Simulation.step` on top-N candidates.
- **7–8** unit-level selection: farmer gets the single highest-scoring unit action; each hand gets next-best non-conflicting action (mutual exclusion on a tile's water/harvest). Market orders built with batching and cap 10.
- **9–10** serializer emits official dict; explainer logs a compact reason string.

---

## 10. Strategy Roadmap

| Stage | Strategy | Purpose | Pros | Limitations | Complexity | Integration |
|---|---|---|---|---|---|---|
| 1 | Deterministic baseline | Correctness skeleton, parity with `starter` | Simple, testable, no models | No optimization | Low | Registry `strategy: deterministic` |
| 2 | Heuristic | Rules tuned to engine facts (window-watering, feed-first) | Fast, robust | Local, myopic | Low-Med | `strategy: heuristic` + planner rules |
| 3 | Economic | ROI/price-model-driven allocation, sell-batching, shed mgmt | Exploits known price fn | Ignores opponent dynamics | Med | `economy.*` wired into MarketPlanner/ROI |
| 4 | Utility scoring | Weighted multi-objective + short lookahead | Tunable, explainable | Weights need tuning | Med | `Strategy + ActionRanker` weights; optional 1-step SIM |
| 5 | Monte Carlo Tree Search | Explore play/turn choices w/ simulated futures | Global horizon, opp-aware | Costly; needs fast SIM | High | `optimization/mcts` behind `IMCTS` |
| 6 | Beam Search | Deterministic k-best futures | Good tradeoff, lower noise than MCTS | Opponent model crude | Med-High | `optimization/beam` |
| 7 | Genetic / CMA | Evolve planner+strategy weights | Auto-tune, robust to rule drift | Needs many sims | Med | `optimization/genetic` tunes config |
| 8 | Reinforcement Learning | Learn policy from replay/self-play | SOTA potential, handles dynamics | Sample-hungry, unstable, expensive | High | `rl/` env wrapper + replay buf |
| 9 | Hybrid AI | RL critic + model-based planner + MCTS | Best of all | Integration complexity, latency | Very High | StrategyManager orchestrates |

**Integration plan:** all stages share `main.py`, adapters, and domain. Each adds a registered `Strategy`/`Planner`/`Simulation` behind the same protocols; a config flag switches stage. Self-play/eval harness runs any two strategies head-to-head in `benchmarks/`. MCTS/RL re-use the *same* simulation wrapper and domain model, so rules correlation is single-sourced.

---

## 11. Software Engineering Standards

- **Python:** 3.11+ (remote runtime compat; use `pyproject.toml`; `uv`/poetry optional).
- **Style:** PEP 8; **typing**: full type hints on all public signatures; `dataclasses`/`TypedDict` for domain.
- **Docstrings:** Google style on every public class/function; module docstrings state purpose.
- **Naming:** `snake_case` funcs/vars, `CamelCase` classes, `UPPER_SNAKE` constants, private `_`. File/module names singular, lowercase.
- **Logging:** stdlib `logging`; structured fields; never print in library code except debug. Error path uses a dedicated logger.
- **Exception hierarchy:** root `KaggricultureAIError`; children `InvalidObservationError`, `IllegalActionError`, `ConfigError`, `SimulationError`, `BudgetExceededError`.
- **Configuration:** YAML under `config/`; STRICT keys; runtime `configuration` overrides win; immutable after build.
- **Dependencies:** minimal pinned set; dev deps separated. Vendored engine referenced read-only.
- **Lint/format:** `ruff` (lint+format), `mypy` (type check) — CI gates.
- **Testing:** `pytest` (+ `pytest-benchmark`, `pytest-cov`). See §12.
- **CI/CD:** GitHub Actions: lint/type → unit → integration → replay/seed → (nightly) benchmarks + A/B. Software only; reviewer-controlled fit-releases.
- **Docker:** reproducibility for local experiments; not for remote submission.
- **Git workflow:** `main` protected; feature branches; semantic PRs; conventional commits.
- **Versioning:** SemVer on our package; **pin exact `kaggle-environments` version** + archive frozen reference.
- **Docs:** README + `DESIGN.md`; architecture decisions recorded in `decisions/`.
- **Profiling:** `cProfile`/`py-spy`; a per-step timing-budget hook; alert if `p95_step_ms > threshold`.
- **Benchmarking:** deterministic seed suites; compare score deltas vs baselines; store JSON artifacts.

---

## 12. Testing Strategy

| Level | Scope | Key cases |
|---|---|---|
| Unit | adapters, domain invariants, validators, price model, calendar | shed-cap, quadrant math, price floor/inversion, config merge |
| Integration | full `make` run vs `pass/random/starter` | reward monotonic, no exceptions, valid output schema |
| Replay | fixed seeds → byte-diff state/score baselines | reproducibility vs official tag |
| Regression | re-run old scenarios after each change | no score/behavior regressions vs stored snapshots |
| Performance | per-step latency, memory | budget < target; no leak over 720 steps |
| Stress | pathological configs (tiny board, huge capacity, extreme money) | no crash; bounded time |
| Simulation | `Simulation.step` parity vs official engine on random+planned states | exact disagreement = 0 |
| Deterministic seed | same `seed` + config → identical trajectories | RNG parity with engine RNG scheme |
| Acceptance | submission contract: `main.py` has `agent`; runs against `random` and self | passes local `make` and archive build |

**Parity harness** (most valuable): replay official replays + a phase-space of states through our `Simulation.step` and diff against the engine's `.toJSON()`. This single test de-risks search/RL stages.

---

## 13. Risk Analysis

| # | Risk | Impact | Mitigation |
|---|---|---|---|
| R1 | Official repo/engine changes mid-project | High | Pin version + freeze reference; parity harness signature over frozen tag; isolate protocol in adapters; re-fetch+diff on updates. |
| R2 | Competition rule/market-param changes | Med | Config-driven `MARKET_PARAMS`/shops; read from observation; re-derive model; fail-loud adapter on unknown schema. |
| R3 | Incorrect mechanic assumptions | High | Reverse-engineering recorded in §1.6; unit tests mirror engine; NEVER trust docs alone — corroborate via parity harness. |
| R4 | Market misunderstanding (price/supply interaction) | Med | Analytic price model + tests; simulate self-glut & town drain; per-unit lockstep modeled in SIM. |
| R5 | Architecture drift / duplicated official logic | Med | Dependency rule; single adapter/protocols; lint gates; review. |
| R6 | Performance bottleneck / decision latency | High (remote) | Step-budget hook; lazy adapters; fast pure-python SIM; early-return pruning in search; pre-compute price tables. |
| R7 | Memory growth over 720 steps / replay bloat | Med | Reuse snapshots; no unbounded per-turn caches; bounded experiment store. |
| R8 | Simulation mismatch → RL/MCTS path bad | High | SI parity harness must be 0-diff gated before RL/MCTS enablement. |
| R9 | RL instability / sample cost | High | Value-based warm-start from model-based Stages; off-policy replay; curriculum; late-stage only. |
| R10 | Shed-capacity under-management (silent discard) | Med | InventoryManager cap invariant + validator checks; telemetry of discards. |
| R11 | Overfit to town-shop RNG seed of a test run | Med | Multiseed eval; distributional benchmarks; seed-robust strategies. |
| R12 | Wheat sink deadlock (animals unfed→escape) | Med | Feed-first planner priority; wheat reserve rule; escape alert telemetry. |

---

## 14. Final Technical Design Document (Index)

This file IS the technical design document. Section map:

1. Repository Analysis (§1) — engine internals, lifecycle, constants, reverse-engineered facts.
2. Game/Competition Analysis (§2) — mechanics, episodes, cycles, economy, unknowns/assets.
3. Observation Model + Adapter (§3).
4. Action Model + Adapter (§4).
5. Domain Model (§5, DDD).
6. System Architecture (§6, Clean layers + component diagram).
7. Project Structure (§7, modules + interfaces).
8. AI Architecture (§8, components via interfaces).
9. Decision Pipeline (§9, sequence/data-flow for one turn).
10. Strategy Roadmap (§10, Stage 1→9).
11. Engineering Standards (§11).
12. Testing Strategy (§12).
13. Risk Analysis (§13).
Future sections placeholders: Implementation Roadmap & Future AI Roadmap to be appended per stage in `DECISIONS.md`.

---

## 15. Implementation Roadmap (Stage 1 → 4)

- **Stage 1 (deterministic):** scaffold package; `ObservationAdapter`+`ActionSerializer`+`domain`; `main.py`; parity harness; a deterministic crop loop matching `starter`; CI + benchmarks vs baselines.
- **Stage 2 (heuristic):** window-watering, feed-first, nearest-job hand scheduler, shed management; multiseed benchmark.
- **Stage 3 (economic):** `economy/price_model` + `ROI Analyzer`; sell-batching + town-demand forecast; expansion and worker-payback rules; simulator for ROI lookahead.
- **Stage 4 (utility):** multi-objective `ActionRanker` with tunable weights; 1-step optional lookahead; explainer logging; parameter sweep via `experiments/`.

**Future AI Roadmap (5–9):** enable MCTS (5), Beam (6), Genetic tuning (7), RL (8) reusing SIM+domain, then Hybrid (9). Each gated by the SI-parity and performance budgets per §12/§13.

---

*Prepared by the elite engineering organization. This document is the authoritative blueprint; future stages must not contradict it and must update it via versioned decisions.*