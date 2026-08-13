import React, { useMemo, useState } from "react";
import { ScrollText, Copy, Download, Search, Terminal, AlertTriangle } from "lucide-react";
import { useStore } from "../lib/store";
import { getTurn } from "../lib/sim";
import { Card, EmptyState, Badge } from "../components/common";

type Cat = "AI" | "SIMULATION" | "MARKET" | "ACTIONS" | "ERROR" | "PERFORMANCE";

interface LogEntry {
  turn: number;
  hour: number;
  cat: Cat;
  msg: string;
}

const CAT_COLOR: Record<Cat, string> = {
  AI: "#00D4FF",
  SIMULATION: "#94a3b8",
  MARKET: "#F5A623",
  ACTIONS: "#22C55E",
  ERROR: "#EF4444",
  PERFORMANCE: "#a855f7",
};

export function Logs() {
  const { game, cursor, developer } = useStore();
  const turn = getTurn(game, cursor);
  const [cat, setCat] = useState<Cat | "ALL">("ALL");
  const [q, setQ] = useState("");

  const entries = useMemo<LogEntry[]>(() => {
    if (!game) return [];
    const out: LogEntry[] = [];
    for (let i = 0; i < game.turns.length; i++) {
      const t = game.turns[i];
      out.push({ turn: t.turn, hour: t.hour, cat: "SIMULATION", msg: `Turn ${t.turn} advanced (Day ${t.day + 1}).` });
      out.push({ turn: t.turn, hour: t.hour, cat: "AI", msg: `Decision: ${t.decision.summary} [${t.decision.type}]` });
      out.push({ turn: t.turn, hour: t.hour, cat: "ACTIONS", msg: `Farmer ${t.action.farmer.join(" ")}; market ops ${t.action.market.length}.` });
      if (i > 0) {
        const prev = game.turns[i - 1];
        for (const [k, v] of Object.entries(t.market.prices)) {
          const pv = (prev.market.prices as any)[k] ?? v;
          if (Math.abs((v as number) - (pv as number)) >= 20)
            out.push({ turn: t.turn, hour: t.hour, cat: "MARKET", msg: `Price ${k} moved to ${v}c (was ${pv}c).` });
        }
      }
    }
    return out;
  }, [game]);

  const filtered = useMemo(() => {
    return entries
      .filter((e) => (cat === "ALL" ? true : e.cat === cat))
      .filter((e) => (q ? e.msg.toLowerCase().includes(q.toLowerCase()) : true))
      .slice(-400)
      .reverse();
  }, [entries, cat, q]);

  const raw = useMemo(() => (turn ? JSON.stringify(turn, null, 2) : ""), [turn]);

  async function copy() {
    try {
      await navigator.clipboard.writeText(raw);
    } catch {
      /* ignore */
    }
  }
  function download() {
    const blob = new Blob([raw], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `observation_turn_${turn?.turn}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  if (!game || !turn) return <EmptyState icon={<ScrollText size={40} />} title="No logs" />;

  const cats: (Cat | "ALL")[] = ["ALL", "AI", "SIMULATION", "MARKET", "ACTIONS", "PERFORMANCE", "ERROR"];

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card title="Log Stream" subtitle={`${filtered.length} entries (capped)`} className="lg:col-span-2" bodyClass="space-y-2 max-h-[560px] overflow-y-auto">
          <div className="sticky top-0 z-10 -mx-1 mb-2 flex flex-wrap gap-1.5 bg-forest/80 pb-2 backdrop-blur">
            {cats.map((c) => (
              <button
                key={c}
                onClick={() => setCat(c)}
                className={`rounded-lg px-2 py-1 text-[11px] font-medium ${
                  cat === c ? "bg-white/10 text-white" : "text-white/45 hover:text-white"
                }`}
                style={cat === c && c !== "ALL" ? { color: CAT_COLOR[c as Cat] } : undefined}
              >
                {c}
              </button>
            ))}
            <div className="ml-auto flex items-center gap-1.5 rounded-lg border border-border bg-surface px-2">
              <Search size={12} className="text-white/40" />
              <input
                value={q}
                onChange={(e) => setQ(e.target.value)}
                placeholder="search…"
                className="w-28 bg-transparent text-xs text-white placeholder:text-white/30 focus:outline-none"
              />
            </div>
          </div>
          {filtered.map((e, i) => (
            <div key={i} className="flex items-start gap-2 rounded-lg bg-white/[0.02] px-2 py-1 font-mono text-[11px]">
              <span className="shrink-0 text-white/30">T{e.turn}</span>
              <span className="shrink-0 font-semibold" style={{ color: CAT_COLOR[e.cat] }}>
                {e.cat}
              </span>
              <span className="text-white/65">{e.msg}</span>
            </div>
          ))}
        </Card>

        <Card title="Raw Observation Inspector" subtitle="Current turn (JSON)">
          <div className="mb-2 flex gap-2">
            <button className="btn flex-1" onClick={copy}><Copy size={13} /> Copy</button>
            <button className="btn flex-1" onClick={download}><Download size={13} /> Download</button>
          </div>
          <pre className="max-h-[460px] overflow-auto rounded-xl border border-border bg-black/40 p-3 font-mono text-[10px] leading-relaxed text-emerald/80">
            {raw}
          </pre>
          {developer && (
            <div className="mt-2 flex items-center gap-2 rounded-lg border border-amber/30 bg-amber/10 p-2 text-[11px] text-amber">
              <AlertTriangle size={13} /> Developer mode: exposing private observation state.
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
