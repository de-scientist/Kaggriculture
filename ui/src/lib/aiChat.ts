import { GameRecord, Turn } from "../types";
import { coinGap, deriveMarket, getTurn, PRODUCTS } from "./sim";
import { fmt, signed } from "./format";

export interface ChatResponse {
  answer: string;
  structured?: { label: string; value: string }[];
  suggested_actions?: string[];
  relevant_turns?: number[];
  confidence: number;
}

function topHolding(t: Turn): { item: string; qty: number } | null {
  let best: { item: string; qty: number } | null = null;
  for (const [k, v] of Object.entries(t.private.shed)) {
    const q = v as number;
    if (!best || q > best.qty) best = { item: k, qty: q };
  }
  return best;
}

function bestPriceProduct(t: Turn): { p: string; price: number } {
  let best = { p: "WHEAT", price: 0 };
  for (const p of PRODUCTS) {
    const price = t.market.prices[p] ?? 0;
    if (price > best.price) best = { p, price };
  }
  return best;
}

export function respond(
  raw: string,
  game: GameRecord | null,
  cursor: number
): ChatResponse {
  const msg = raw.toLowerCase();
  const fallback: ChatResponse = {
    answer:
      "I can answer questions about the current farm, market, decisions, and performance using the loaded replay data. Try: 'Why did you sell?', 'Are we winning?', or 'Analyze the market'.",
    confidence: 0.6,
  };
  if (!game) return fallback;
  const t = getTurn(game, cursor)!;
  const gap = coinGap(t);
  const ahead = gap >= 0;

  const ask = (keys: string[]) => keys.some((k) => msg.includes(k));

  if (ask(["behind", "losing", "loosing", "ahead", "winning", "win", "margin", "advantage", "score"])) {
    return {
      answer: ahead
        ? `We are currently AHEAD by ${fmt(gap)} coins versus the opponent. Healthy cash and production are maintaining the lead. Keep liquidating inventory when prices are favorable to widen the margin.`
        : `We are currently BEHIND by ${fmt(Math.abs(gap))} coins. The priority is efficient production and catching up on cash before the opponent's lead compounds.`,
      structured: [
        { label: "Our Coins", value: fmt(t.money) },
        { label: "Opponent", value: fmt(t.opp_money) },
        { label: "Gap", value: `${signed(gap)}` },
        { label: "Day", value: `${t.day + 1} / 30` },
      ],
      confidence: 0.92,
    };
  }

  if (ask(["sell", "sold", "sale", "market", "price", "corn", "wheat", "carrot", "tomato", "melon", "strawberry", "egg", "milk", "wool", "trade"])) {
    const rows = deriveMarket(game, cursor);
    const top = [...rows].sort((a, b) => b.price - a.price)[0];
    const holding = topHolding(t);
    return {
      answer: `Market conditions: the strongest price right now is ${top.product} at ${top.price}c (trend ${top.trend}). ${
        holding ? `We are holding ${holding.qty} ${holding.item}; consider selling into strength.` : "We hold little inventory to sell."
      }`,
      structured: rows.slice(0, 5).map((r) => ({
        label: r.product,
        value: `${r.price}c ${r.change >= 0 ? "+" : ""}${r.change.toFixed(1)}%`,
      })),
      confidence: 0.88,
    };
  }

  if (ask(["weakness", "risk", "problem", "wrong", "mistake", "improve"])) {
    const inv = Object.values(t.private.shed).reduce((s, v) => s + (v as number), 0);
    const lowCash = t.money < 2000;
    return {
      answer: `Current risk factors:\n• Inventory on hand: ${inv} units${inv > 120 ? " (accumulating — liquidate)" : ""}\n• Cash reserves: ${fmt(t.money)}${lowCash ? " (thin — limit expansion)" : ""}\n• Land utilized: ${t.farm.unlocked_quadrants.length}/4 quadrants.`,
      structured: [
        { label: "Inventory", value: `${inv} units` },
        { label: "Cash", value: fmt(t.money) },
        { label: "Land", value: `${t.farm.unlocked_quadrants.length}/4` },
      ],
      confidence: 0.7,
    };
  }

  if (ask(["strategy", "mode", "plan", "phase", "why are we", "approach"])) {
    const d = t.decision;
    return {
      answer: `Current strategy mode: ${d.strategy_mode}. The agent selected a ${d.type} action — "${d.summary}". Confidence ${Math.round(
        d.confidence.value * 100
      )}%.`,
      structured: [
        { label: "Mode", value: d.strategy_mode },
        { label: "Action", value: d.type },
        { label: "Confidence", value: `${Math.round(d.confidence.value * 100)}%` },
      ],
      confidence: d.confidence.value,
    };
  }

  if (ask(["last", "decision", "decide", "did you", "why did"])) {
    const d = t.decision;
    return {
      answer: `Most recent decision (turn ${t.turn}): ${d.summary}\nReason: ${d.factors.join(" ")}`,
      structured: [
        { label: "Action", value: d.type },
        { label: "Expected", value: `${signed(d.expected_value)}` },
        { label: "Candidates", value: `${d.n_candidates ?? "?"}` },
      ],
      relevant_turns: [t.turn],
      confidence: d.confidence.value,
    };
  }

  if (ask(["worker", "hand", "labor", "hire", "animal", "cow", "goose", "sheep", "farm state", "farm"])) {
    let animals = 0;
    for (const row of t.farm.tiles)
      for (const tile of row)
        if (tile && typeof tile === "object" && (tile.kind === "COOP" || tile.kind === "PASTURE") && tile.animal) animals++;
    return {
      answer: `Farm state: ${1 + t.farm.hands.length} worker units active, ${animals} animals, ${t.farm.unlocked_quadrants.length}/4 quadrants unlocked. Farmer at (${t.farm.farmer[0]},${t.farm.farmer[1]}).`,
      structured: [
        { label: "Workers", value: `${1 + t.farm.hands.length}` },
        { label: "Animals", value: `${animals}` },
        { label: "Quadrants", value: `${t.farm.unlocked_quadrants.length}/4` },
      ],
      confidence: 0.85,
    };
  }

  if (ask(["endgame", "finish", "close", "final", "predict"])) {
    return {
      answer: `With ${30 - (t.day + 1)} days remaining and ${ahead ? "a lead" : "a deficit"} of ${fmt(Math.abs(gap))} coins, the endgame focuses on ${
        ahead ? "converting assets to cash and defending the lead." : "high-efficiency liquidation to close the gap."
      }`,
      confidence: 0.75,
    };
  }

  return fallback;
}
