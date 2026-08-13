import {
  GameDataset,
  GameRecord,
  Turn,
  Decision,
  Product,
} from "../types";

export const PRODUCTS: Product[] = [
  "WHEAT",
  "CARROT",
  "TOMATO",
  "STRAWBERRY",
  "MELON",
  "EGG",
  "MILK",
  "WOOL",
  "FERTILIZER",
];

export const CROPS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON"];
export const ANIMALS = ["GOOSE", "COW", "SHEEP"];

export const STARTING_MONEY = 3000;
export const TURNS_PER_DAY = 24;
export const TOTAL_DAYS = 30;

export function getTurn(game: GameRecord | null, cursor: number): Turn | null {
  if (!game) return null;
  const i = Math.max(0, Math.min(cursor, game.turns.length - 1));
  return game.turns[i] ?? null;
}

export interface Kpis {
  coins: number;
  netProfit: number;
  farmValue: number;
  landOwned: number;
  workers: number;
  animals: number;
  inventoryValue: number;
  winRate: number | null;
}

function estimateTileValue(turn: Turn, x: number, y: number): number {
  const tile = turn.farm.tiles[y]?.[x];
  if (!tile || typeof tile !== "object") return 0;
  if (tile.kind === "PLANT") {
    const price = turn.market.prices[tile.crop] ?? 10;
    return tile.yield_units * price;
  }
  if (tile.kind === "COOP" || tile.kind === "PASTURE") {
    return tile.animal ? 250 : 100;
  }
  return 0;
}

export function deriveKpis(
  game: GameRecord | null,
  cursor: number,
  winRate: number | null
): Kpis {
  if (!game) {
    return {
      coins: 0,
      netProfit: 0,
      farmValue: 0,
      landOwned: 0,
      workers: 0,
      animals: 0,
      inventoryValue: 0,
      winRate: null,
    };
  }
  const t = getTurn(game, cursor)!;
  let farmValue = 0;
  let animals = 0;
  for (let y = 0; y < t.farm.tiles.length; y++) {
    for (let x = 0; x < t.farm.tiles[y].length; x++) {
      farmValue += estimateTileValue(t, x, y);
      const tile = t.farm.tiles[y][x];
      if (tile && typeof tile === "object" && (tile.kind === "COOP" || tile.kind === "PASTURE") && tile.animal) {
        animals += 1;
      }
    }
  }
  let inventoryValue = 0;
  for (const [k, v] of Object.entries(t.private.shed)) {
    inventoryValue += (v as number) * (t.market.prices[k] ?? 1);
  }
  const landOwned = t.farm.unlocked_quadrants.length;
  const workers = 1 + t.farm.hands.length;
  return {
    coins: t.money,
    netProfit: t.money - STARTING_MONEY,
    farmValue,
    landOwned,
    workers,
    animals,
    inventoryValue,
    winRate,
  };
}

export function coinGap(turn: Turn | null): number {
  if (!turn) return 0;
  return turn.money - turn.opp_money;
}

export interface MarketRow {
  product: Product;
  price: number;
  prev: number;
  change: number;
  supply: number;
  demand: number;
  trend: "up" | "down" | "flat";
  level: "HIGH" | "MEDIUM" | "LOW";
}

export function deriveMarket(game: GameRecord | null, cursor: number): MarketRow[] {
  if (!game) return [];
  const t = getTurn(game, cursor)!;
  const prevIdx = Math.max(0, cursor - TURNS_PER_DAY);
  const prev = game.turns[prevIdx];
  const shops = t.town.unlocked_shops.length;
  return PRODUCTS.filter((p) => p !== "FERTILIZER").map((p) => {
    const price = t.market.prices[p] ?? 0;
    const prevPrice = prev.market.prices[p] ?? price;
    const change = prevPrice ? ((price - prevPrice) / prevPrice) * 100 : 0;
    const supply = t.market.inventory[p] ?? 0;
    const trend: MarketRow["trend"] =
      change > 1.5 ? "up" : change < -1.5 ? "down" : "flat";
    const level: MarketRow["level"] =
      supply < 20 ? "HIGH" : supply < 60 ? "MEDIUM" : "LOW";
    return {
      product: p,
      price,
      prev: prevPrice,
      change,
      supply,
      demand: shops,
      trend,
      level,
    };
  });
}

export interface ReplayEvent {
  turn: number;
  day: number;
  type:
    | "land"
    | "hire"
    | "plant"
    | "harvest"
    | "animal"
    | "sale"
    | "strategy"
    | "swing";
  label: string;
  detail: string;
}

export function detectEvents(game: GameRecord): ReplayEvent[] {
  const events: ReplayEvent[] = [];
  let prevQuadrants = new Set<string>();
  let prevHands = 0;
  let prevStrategy = "";
  for (let i = 0; i < game.turns.length; i++) {
    const t = game.turns[i];
    const quads = new Set(t.farm.unlocked_quadrants);
    if (quads.size > prevQuadrants.size) {
      const added = [...quads].filter((q) => !prevQuadrants.has(q));
      events.push({
        turn: i,
        day: t.day,
        type: "land",
        label: "Land Acquired",
        detail: `Unlocked quadrant ${added.join(", ")}`,
      });
    }
    prevQuadrants = quads;

    if (t.farm.hands.length > prevHands) {
      events.push({
        turn: i,
        day: t.day,
        type: "hire",
        label: "Worker Hired",
        detail: `Hired farm hand (total ${1 + t.farm.hands.length} units)`,
      });
    }
    prevHands = t.farm.hands.length;

    const d = t.decision;
    if (d.strategy_mode && d.strategy_mode !== prevStrategy) {
      if (prevStrategy !== "") {
        events.push({
          turn: i,
          day: t.day,
          type: "strategy",
          label: "Strategy Shift",
          detail: `Mode → ${d.strategy_mode}`,
        });
      }
      prevStrategy = d.strategy_mode;
    }

    const marketActs = t.action.market.map((a) => a[0]);
    if (marketActs.includes("SELL")) {
      const total = t.action.market
        .filter((a) => a[0] === "SELL")
        .reduce((s, a) => s + (Number(a[2]) || 0), 0);
      events.push({
        turn: i,
        day: t.day,
        type: "sale",
        label: "Market Sale",
        detail: `Sold ${total} units`,
      });
    }

    // major economic swing
    if (i > 0) {
      const delta = t.money - game.turns[i - 1].money;
      if (Math.abs(delta) >= 800) {
        events.push({
          turn: i,
          day: t.day,
          type: "swing",
          label: "Economic Swing",
          detail: `${delta >= 0 ? "+" : ""}${Math.round(delta)} coins in one turn`,
        });
      }
    }
  }
  return events;
}

export interface TournamentSummary {
  episodes: number;
  wins: number;
  losses: number;
  ties: number;
  avgCoins: number;
  avgMargin: number;
  winRate: number;
  fallbackCount: number;
  invalidActions: number;
  avgDecisionMs: number;
}

export function getTournamentSummary(
  dataset: GameDataset | null
): TournamentSummary | null {
  const data = dataset?.championship?.data as
    | { "CHAMPION_TOURNAMENT_RESULTS.json"?: any[] }
    | undefined;
  const list = data?.["CHAMPION_TOURNAMENT_RESULTS.json"];
  if (!list || !Array.isArray(list) || list.length === 0) return null;
  let wins = 0,
    losses = 0,
    ties = 0,
    coins = 0,
    margin = 0,
    fb = 0,
    inv = 0,
    dms = 0;
  for (const e of list) {
    if (e.winner === 0) wins++;
    else if (e.winner === 1) losses++;
    else ties++;
    coins += e.our_final_coins ?? 0;
    margin += e.coin_margin ?? 0;
    fb += e.fallback_count ?? 0;
    inv += e.invalid_actions ?? 0;
    dms += e.avg_decision_ms ?? 0;
  }
  const n = list.length;
  return {
    episodes: n,
    wins,
    losses,
    ties,
    avgCoins: coins / n,
    avgMargin: margin / n,
    winRate: wins / n,
    fallbackCount: fb,
    invalidActions: inv,
    avgDecisionMs: dms / n,
  };
}

export function getChampionWinRate(dataset: GameDataset | null): number | null {
  return getTournamentSummary(dataset)?.winRate ?? null;
}

// Build a per-turn series for a crop's planted count (living plants)
export function cropTimeline(game: GameRecord, crop: string): number[] {
  return game.turns.map((t) => {
    let n = 0;
    for (const row of t.farm.tiles) {
      for (const tile of row) {
        if (tile && typeof tile === "object" && tile.kind === "PLANT" && tile.crop === crop)
          n++;
      }
    }
    return n;
  });
}

export function animalCount(game: GameRecord, cursor: number, animal: string): number {
  const t = getTurn(game, cursor);
  if (!t) return 0;
  let n = 0;
  for (const row of t.farm.tiles) {
    for (const tile of row) {
      if (
        tile &&
        typeof tile === "object" &&
        (tile.kind === "COOP" || tile.kind === "PASTURE") &&
        tile.animal === animal
      )
        n++;
    }
  }
  return n;
}

export function shedTotal(turn: Turn | null): number {
  if (!turn) return 0;
  return Object.values(turn.private.shed).reduce((s, v) => s + (v as number), 0);
}

export function decisionConfidence(d: Decision): string {
  return `${Math.round(d.confidence.value * 100)}%`;
}
