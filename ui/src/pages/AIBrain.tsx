import React, { useMemo } from "react";
import { BrainCircuit, Sparkles, GitBranch, ShieldCheck, Activity, ChevronRight } from "lucide-react";
import { useStore } from "../lib/store";
import { getTurn } from "../lib/sim";
import { timeOfDay } from "../lib/format";
import { Card, EmptyState, Badge, StatusPill } from "../components/common";
import { ProgressBar } from "../lib/charts";
import { aiStateFromTurn } from "../lib/store";

const RISK = ["Low", "Medium", "High"];

export function AIBrain() {
  const { game, cursor } = useStore();
  const turn = getTurn(game, cursor);
  const { state, label } = aiStateFromTurn(turn);

  const timeline = useMemo(() => {
    if (!game) return [];
    return game.actions_log.slice(Math.max(0, cursor - 18), cursor + 1).reverse();
  }, [game, cursor]);

  if (!game || !turn) return <EmptyState icon={<BrainCircuit size={40} />} title="No decision data" />;

  const d = turn.decision;
  const conf = Math.round(d.confidence.value * 100);
  const risk = d.expected_value > 0 ? "Low" : "Medium";

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <StatusPill state={state} label={label} />
        <Badge color="#00D4FF"><Sparkles size={11} /> Strategy: {d.strategy_mode}</Badge>
        <Badge color="#F5A623">Policy: {d.policy ?? "champion"}</Badge>
        {d.confidence.value < 0.5 && <Badge color="#F5A623">⚠ AI is uncertain</Badge>}
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        {/* DECISION CARD */}
        <Card title="AI Decision" subtitle={`Turn ${turn.turn} · Day ${turn.day + 1}`}>
          <div className="rounded-2xl border border-cyan/20 bg-cyan/[0.06] p-4">
            <div className="card-title">Action</div>
            <div className="mt-1 text-2xl font-bold text-white">
              {d.summary}
            </div>
            <div className="mt-2 flex items-center gap-2">
              <Badge color="#00D4FF" solid>
                {d.type.toUpperCase()}
              </Badge>
              <span className="text-xs text-white/45">Expected {d.expected_value >= 0 ? "+" : ""}{d.expected_value} coins</span>
            </div>

            <div className="mt-4">
              <div className="mb-1 flex justify-between text-xs">
                <span className="text-white/55">Confidence</span>
                <span className="font-mono text-white/85">{conf}%</span>
              </div>
              <ProgressBar value={conf} color={conf > 70 ? "#22C55E" : conf > 45 ? "#F5A623" : "#EF4444"} />
              <div className="mt-1 text-[11px] text-white/40">Level: {d.confidence.level}</div>
            </div>

            <div className="mt-4 grid grid-cols-2 gap-3">
              <Mini label="Strategy" value={d.strategy_mode} />
              <Mini label="Risk" value={risk} color={risk === "Low" ? "#22C55E" : "#F5A623"} />
            </div>
          </div>
        </Card>

        {/* EXPLANATION */}
        <Card title="Why this decision?" subtitle="Structured reasoning (no hidden chain-of-thought)">
          <ul className="space-y-2">
            {d.factors.map((f, i) => (
              <li key={i} className="flex gap-2 text-sm text-white/75">
                <span className="mt-1 text-cyan">•</span>
                <span>{f}</span>
              </li>
            ))}
          </ul>
          <div className="mt-4 rounded-xl border border-border bg-surface p-3">
            <div className="card-title mb-2">Alternative Actions</div>
            <div className="space-y-1.5">
              {d.alternatives.length === 0 && <div className="text-xs text-white/40">No alternatives recorded.</div>}
              {d.alternatives.map((a, i) => (
                <div key={i} className="flex items-center justify-between rounded-lg bg-white/5 px-3 py-1.5 text-sm">
                  <span className="text-white/70 capitalize">{a.type}</span>
                  <span className="text-[11px] text-white/40">{a.label}</span>
                </div>
              ))}
              <div className="flex items-center justify-between rounded-lg border border-cyan/30 bg-cyan/10 px-3 py-1.5 text-sm">
                <span className="font-medium text-cyan">Selected</span>
                <span className="font-mono text-cyan">{d.type}</span>
              </div>
            </div>
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card title="Decision Timeline" subtitle="Most recent first" className="lg:col-span-2" bodyClass="max-h-[340px] overflow-y-auto space-y-2">
          {timeline.map((a, i) => (
            <div key={i} className="flex items-start gap-3 rounded-lg border border-border bg-surface px-3 py-2">
              <div className="flex flex-col items-center pt-0.5">
                <span className="h-2 w-2 rounded-full bg-cyan" />
                {i < timeline.length - 1 && <span className="mt-1 w-px flex-1 bg-white/10" />}
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-[11px] text-white/40">
                    {timeOfDay(a.hour)} · T{a.turn}
                  </span>
                  <span className="text-[11px] text-white/45">{a.decision.strategy_mode}</span>
                </div>
                <div className="truncate text-sm text-white/85">{a.decision.summary}</div>
              </div>
            </div>
          ))}
        </Card>

        <Card title="Strategy Mode" subtitle="Current phase">
          <div className="rounded-2xl border border-border bg-surface p-4 text-center">
            <Activity className="mx-auto text-cyan" size={28} />
            <div className="mt-2 text-lg font-bold text-white">{d.strategy_mode}</div>
            <div className="text-xs text-white/45">Phase-appropriate allocation</div>
          </div>
          <div className="mt-3 space-y-1.5 text-sm">
            <div className="flex justify-between">
              <span className="text-white/55">Candidates evaluated</span>
              <span className="font-mono text-white/85">{d.n_candidates ?? "—"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-white/55">Policy</span>
              <span className="font-mono text-white/85">{d.policy ?? "champion"}</span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}

function Mini({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div className="rounded-xl bg-white/5 p-2.5">
      <div className="text-[10px] uppercase tracking-wide text-white/40">{label}</div>
      <div className="text-sm font-semibold" style={{ color: color ?? "#fff" }}>
        {value}
      </div>
    </div>
  );
}
