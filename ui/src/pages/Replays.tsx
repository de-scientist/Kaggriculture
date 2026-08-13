import React, { useMemo } from "react";
import { History, Play, Pause, SkipBack, SkipForward, Flag, Search } from "lucide-react";
import { useStore } from "../lib/store";
import { getTurn, detectEvents, type ReplayEvent } from "../lib/sim";
import { Card, EmptyState, Badge } from "../components/common";
import { FarmMap } from "../components/farm/FarmMap";
import { fmt } from "../lib/format";

const EVENT_COLOR: Record<ReplayEvent["type"], string> = {
  land: "#a855f7",
  hire: "#F5A623",
  plant: "#2E7D32",
  harvest: "#22C55E",
  animal: "#22C55E",
  sale: "#00D4FF",
  strategy: "#F5A623",
  swing: "#EF4444",
};

export function Replays() {
  const { dataset, game, gameId, setGame, cursor, setCursor, playing, play, pause, step } = useStore();
  const turn = getTurn(game, cursor);

  const events = useMemo(() => (game ? detectEvents(game) : []), [game]);

  if (!dataset || dataset.games.length === 0)
    return <EmptyState icon={<History size={40} />} title="No replays available" desc="Recorded games will appear here." />;

  const max = game ? game.turns.length - 1 : 0;

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-4">
        {/* GAME LIST */}
        <Card title="Games" subtitle={`${dataset.games.length} recorded`} bodyClass="space-y-2 max-h-[600px] overflow-y-auto">
          {dataset.games.map((g) => (
            <button
              key={g.id}
              onClick={() => setGame(g.id)}
              className={`w-full rounded-xl border p-3 text-left transition-colors ${
                g.id === gameId ? "border-cyan/40 bg-cyan/10" : "border-border bg-surface hover:bg-white/5"
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs text-white/80">{g.agent_version}</span>
                <Badge color={g.final.reward && g.final.reward > 0 ? "#22C55E" : "#EF4444"}>
                  {g.final.reward && g.final.reward > 0 ? "WIN" : "LOSS"}
                </Badge>
              </div>
              <div className="mt-1 text-[11px] text-white/45">vs {g.opponent} · seed {g.seed}</div>
              <div className="mt-0.5 font-mono text-[11px] text-white/55">{fmt(g.final.money)}c</div>
            </button>
          ))}
        </Card>

        <div className="space-y-4 lg:col-span-3">
          {/* CONTROLS */}
          <Card bodyClass="space-y-3">
            <div className="flex flex-wrap items-center gap-2">
              <button className="btn" onClick={() => step(-1)}><SkipBack size={16} /></button>
              {playing ? (
                <button className="btn btn-primary" onClick={pause}><Pause size={16} /> Pause</button>
              ) : (
                <button className="btn btn-primary" onClick={play}><Play size={16} /> Play</button>
              )}
              <button className="btn" onClick={() => step(1)}><SkipForward size={16} /></button>
              <input
                type="range" min={0} max={max} value={cursor}
                onChange={(e) => setCursor(Number(e.target.value))}
                className="ml-2 flex-1 accent-cyan"
              />
              <span className="font-mono text-xs text-white/55">T{turn?.turn} · D{turn?.day ? turn.day + 1 : 1}/30</span>
            </div>
          </Card>

          {turn && (
            <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
              <Card title="Board" className="lg:col-span-2">
                <FarmMap turn={turn} />
              </Card>
              <Card title="Turn Detail">
                <Section label="Observation">
                  <Line k="Coins" v={fmt(turn.money)} />
                  <Line k="Opponent" v={fmt(turn.opp_money)} />
                  <Line k="Quadrants" v={`${turn.farm.unlocked_quadrants.length}/4`} />
                </Section>
                <Section label="AI Decision">
                  <div className="text-sm text-white/85">{turn.decision.summary}</div>
                  <Line k="Expected" v={`${turn.decision.expected_value >= 0 ? "+" : ""}${turn.decision.expected_value}`} />
                  <Line k="Confidence" v={`${Math.round(turn.decision.confidence.value * 100)}%`} />
                </Section>
                <Section label="Result">
                  <Line k="Action" v={turn.action.farmer[0] ?? "PASS"} />
                  <Line k="Market ops" v={`${turn.action.market.length}`} />
                </Section>
              </Card>
            </div>
          )}
        </div>
      </div>

      {/* EVENT TIMELINE */}
      <Card title="Replay Timeline" subtitle="Click an event to jump" bodyClass="max-h-[300px] overflow-y-auto">
        <div className="space-y-1">
          {events.map((e, i) => (
            <button
              key={i}
              onClick={() => setCursor(e.turn)}
              className="flex w-full items-center gap-3 rounded-lg px-2 py-1.5 text-left hover:bg-white/5"
            >
              <span className="h-2 w-2 shrink-0 rounded-full" style={{ background: EVENT_COLOR[e.type] }} />
              <Flag size={12} className="shrink-0 text-white/30" />
              <span className="w-16 shrink-0 font-mono text-[11px] text-white/40">T{e.turn}</span>
              <span className="w-32 shrink-0 text-xs font-medium" style={{ color: EVENT_COLOR[e.type] }}>{e.label}</span>
              <span className="truncate text-xs text-white/60">{e.detail}</span>
            </button>
          ))}
        </div>
      </Card>
    </div>
  );
}

function Section({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="mb-3">
      <div className="card-title mb-1.5">{label}</div>
      <div className="space-y-1">{children}</div>
    </div>
  );
}

function Line({ k, v }: { k: string; v: string }) {
  return (
    <div className="flex justify-between text-sm">
      <span className="text-white/55">{k}</span>
      <span className="font-mono text-white/85">{v}</span>
    </div>
  );
}
