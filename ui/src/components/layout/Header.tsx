import React from "react";
import { Circle, Coins, Crown, MessageSquare, AlertTriangle } from "lucide-react";
import { useStore, aiStateFromTurn } from "../../lib/store";
import { getTurn } from "../../lib/sim";
import { fmt } from "../../lib/format";
import { StatusPill } from "../common";

export function Header() {
  const { game, cursor, dataset, setChatOpen, developer, setDeveloper } = useStore();
  const turn = getTurn(game, cursor);
  const { state, label } = aiStateFromTurn(turn);

  const offline = !dataset?.championship?.data;
  const sourceBadge = turn ? (game?.real ? "REPLAY" : "DEMO") : "—";

  return (
    <header className="z-20 flex flex-wrap items-center gap-3 border-b border-border bg-forest/50 px-5 py-3 backdrop-blur">
      <div className="flex items-center gap-2">
        <h1 className="text-sm font-bold tracking-wide text-white">KAGGRICULTURE AI COMMAND CENTER</h1>
        <StatusPill state={state} label={state} />
      </div>

      {!offline && (
        <span className="chip border border-amber/40 bg-amber/10 text-amber">
          <AlertTriangle size={12} /> OFFLINE · {sourceBadge} DATA
        </span>
      )}

      <div className="ml-auto flex flex-wrap items-center gap-2 text-xs">
        {turn && (
          <div className="flex items-center gap-3 rounded-xl border border-border bg-surface px-3 py-1.5">
            <span className="text-white/45">
              Season <span className="text-white/85">Day {turn.day + 1}/30</span>
            </span>
            <span className="text-white/20">|</span>
            <span className="text-white/45">
              Turn <span className="font-mono text-white/85">{turn.turn}/720</span>
            </span>
          </div>
        )}
        {turn && (
          <div className="flex items-center gap-1.5 rounded-xl border border-emerald/30 bg-emerald/10 px-3 py-1.5 text-emerald">
            <Coins size={14} />
            <span className="metric text-sm">{fmt(turn.money)}</span>
          </div>
        )}
        {game && (
          <div className="flex items-center gap-1.5 rounded-xl border border-border bg-surface px-3 py-1.5 text-white/70">
            <Crown size={14} className="text-amber" />
            <span className="text-white/55">Champion</span>
            <span className="font-mono text-white/90">{game.agent_version}</span>
          </div>
        )}

        <button
          onClick={() => setDeveloper(!developer)}
          className={`rounded-xl border px-2.5 py-1.5 text-[11px] ${
            developer
              ? "border-cyan/40 bg-cyan/15 text-cyan"
              : "border-border bg-surface text-white/45 hover:text-white"
          }`}
          title="Toggle Developer Mode"
        >
          DEV
        </button>

        <button
          onClick={() => setChatOpen(true)}
          className="btn btn-primary"
        >
          <MessageSquare size={15} /> Ask AI
        </button>
      </div>
    </header>
  );
}
