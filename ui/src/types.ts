export type Crop =
  | "WHEAT"
  | "CARROT"
  | "TOMATO"
  | "STRAWBERRY"
  | "MELON";

export type Animal = "GOOSE" | "COW" | "SHEEP";
export type Product =
  | "WHEAT"
  | "CARROT"
  | "TOMATO"
  | "STRAWBERRY"
  | "MELON"
  | "EGG"
  | "MILK"
  | "WOOL"
  | "FERTILIZER";

export interface PlantTile {
  kind: "PLANT";
  crop: Crop;
  planted_day: number;
  watered_today: boolean;
  consecutive_unwatered: number;
  yield_units: number;
  max_lifespan_step: number;
  fertilized_until_day: number;
}

export interface WeedTile {
  kind: "WEED";
}

export interface StructureTile {
  kind: "COOP" | "PASTURE";
  animal?: Animal;
  placed_day?: number;
  yield_units?: number;
  fed_today?: boolean;
  consecutive_unfed?: number;
  cared_today?: boolean;
  fertilizer_available?: number;
  pending_care_bonus?: number;
}

export type Tile = null | "LOCKED" | PlantTile | WeedTile | StructureTile;

export interface FarmSnapshot {
  tiles: Tile[][];
  farmer: [number, number];
  hands: [number, number][];
  unlocked_quadrants: string[];
  hires_today: number;
}

export interface MarketState {
  inventory: Record<string, number>;
  prices: Record<string, number>;
}

export interface Decision {
  type: "trade" | "farm" | "expand" | "move" | "wait";
  summary: string;
  expected_value: number;
  strategy_mode: string;
  confidence: { value: number; level: "High" | "Medium" | "Low" };
  factors: string[];
  policy?: string;
  n_candidates?: number;
  alternatives: { type: string; label: string }[];
}

export interface Turn {
  turn: number;
  day: number;
  hour: number;
  money: number;
  opp_money: number;
  farm: FarmSnapshot;
  private: {
    shed: Record<string, number>;
    seeds: Record<string, number>;
    inventories: Record<string, number>[];
  };
  market: MarketState;
  town: { unlocked_shops: string[] };
  action: { farmer: string[]; hands: string[][]; market: string[][] };
  opp_action: unknown;
  decision: Decision;
}

export interface GameRecord {
  id: string;
  agent_version: string;
  opponent: string;
  seed: number;
  episode_steps: number;
  real: boolean;
  turns: Turn[];
  money_history: number[];
  opp_money_history: number[];
  price_history: Record<string, number[]>;
  actions_log: {
    turn: number;
    day: number;
    hour: number;
    action: Turn["action"];
    decision: Decision;
  }[];
  final: { money: number; opp_money: number; reward?: number | null; status?: string };
}

export interface GameDataset {
  generated_at: string;
  source: "real" | "synthetic" | "demo";
  games: GameRecord[];
  championship: { source: string; data: Record<string, unknown> | null };
}

export type AIState =
  | "THINKING"
  | "EXECUTING"
  | "WAITING"
  | "HARVESTING"
  | "TRADING"
  | "EXPANDING"
  | "OPTIMIZING"
  | "ENDGAME"
  | "WARNING"
  | "ERROR";

export type PageId =
  | "dashboard"
  | "farm"
  | "aibrain"
  | "market"
  | "simulation"
  | "analytics"
  | "championship"
  | "replays"
  | "experiments"
  | "logs"
  | "settings";
