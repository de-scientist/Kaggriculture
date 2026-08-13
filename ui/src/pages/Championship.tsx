import React, { useMemo, useState } from "react";
import { Trophy, Crown, Users2, TrendingUp, GitCompare, ShieldCheck } from "lucide-react";
import { useStore } from "../lib/store";
import { getTournamentSummary } from "../lib/sim";
import { Card, EmptyState, Badge } from "../components/common";
import { ProgressBar } from "../lib/charts";
import { fmt, pct } from "../lib/format";

export function Championship() {
  const { dataset } = useStore();
  const champ = useMemo(() => getTournamentSummary(dataset), [dataset]);
  const data = dataset?.championship?.data as any;

  const challengers = useMemo(() => {
    const list = data?.["challenger_registry.json"];
    if (!Array.isArray(list)) return [];
    return list;
  }, [data]);

  const matrix = useMemo(() => {
    const list = data?.["CHAMPION_TOURNAMENT_RESULTS.json"];
    if (!Array.isArray(list)) return [];
    const byOpp: Record<string, { w: number; l: number; t: number }> = {};
    for (const e of list) {
      const o = e.opponent ?? "unknown";
      byOpp[o] = byOpp[o] ?? { w: 0, l: 0, t: 0 };
      if (e.winner === 0) byOpp[o].w++;
      else if (e.winner === 1) byOpp[o].l++;
      else byOpp[o].t++;
    }
    return Object.entries(byOpp).map(([opp, s]) => ({ opp, ...s, total: s.w + s.l + s.t }));
  }, [data]);

  if (!dataset || !champ) return <EmptyState icon={<Trophy size={40} />} title="No championship data" desc="Championship telemetry is not present in the loaded dataset." />;

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        {/* CHAMPION */}
        <Card className="lg:col-span-1" bodyClass="text-center">
          <div className="mx-auto grid h-14 w-14 place-items-center rounded-2xl bg-amber/15 text-amber">
            <Crown size={28} />
          </div>
          <div className="mt-2 text-lg font-bold text-white">CHAMPION v1.0</div>
          <Badge color="#22C55E" solid className="mt-1">ACTIVE</Badge>
          <div className="mt-4 space-y-3 text-left">
            <Stat label="Win Rate" value={`${Math.round(champ.winRate * 100)}%`} color="#22C55E" />
            <Stat label="Average Coins" value={fmt(champ.avgCoins)} color="#00D4FF" />
            <Stat label="Games" value={`${champ.episodes}`} color="#F5A623" />
            <Stat label="Fallbacks" value={`${champ.fallbackCount}`} color={champ.fallbackCount === 0 ? "#22C55E" : "#EF4444"} />
            <Stat label="Avg Decision" value={`${champ.avgDecisionMs.toFixed(2)}ms`} color="#a855f7" />
          </div>
        </Card>

        {/* COMPARISON */}
        <Card title="Champion vs Field" subtitle="Tournament performance" className="lg:col-span-2">
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            <Big label="Wins" value={champ.wins} color="#22C55E" />
            <Big label="Losses" value={champ.losses} color="#EF4444" />
            <Big label="Ties" value={champ.ties} color="#94a3b8" />
            <Big label="Avg Margin" value={fmt(champ.avgMargin)} color="#00D4FF" />
          </div>
          <div className="mt-4">
            <div className="mb-1 flex justify-between text-xs text-white/45">
              <span>Overall win rate</span>
              <span>{Math.round(champ.winRate * 100)}%</span>
            </div>
            <ProgressBar value={champ.winRate * 100} color="#22C55E" />
          </div>
          <div className="mt-4 grid grid-cols-2 gap-2">
            <Health label="Invalid Actions" value={champ.invalidActions} good={champ.invalidActions === 0} />
            <Health label="Runtime Errors" value={0} good />
          </div>
        </Card>
      </div>

      {/* CHALLENGERS */}
      <Card title="Challengers" subtitle="Candidate agents under evaluation">
        {challengers.length === 0 ? (
          <div className="text-sm text-white/40">No challenger candidates registered.</div>
        ) : (
          <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
            {challengers.map((c: any, i: number) => {
              const r = c.results ?? {};
              const status = (c.decision ?? "TESTING").toUpperCase();
              const statusColor = status === "PROMOTE" ? "#22C55E" : status === "RETIRE" ? "#EF4444" : "#F5A623";
              return (
                <div key={i} className="rounded-2xl border border-border bg-surface p-3">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-white/90">{c.candidate_id ?? `C${i + 1}`}</span>
                    <Badge color={statusColor}>{status}</Badge>
                  </div>
                  <div className="mt-2 space-y-1.5 text-sm">
                    <Row k="Avg Coins" v={r.avg_coins != null ? fmt(r.avg_coins) : "—"} />
                    <Row k="Games" v={`${r.games ?? 0}`} />
                    <Row k="Wins" v={`${r.wins ?? 0}`} />
                  </div>
                  {r.decision_reason && (
                    <p className="mt-2 text-[11px] text-white/45">{r.decision_reason}</p>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </Card>

      {/* MATCHUP MATRIX */}
      <Card title="Matchup Matrix" subtitle="Champion performance by opponent">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-[11px] uppercase tracking-wide text-white/40">
                <th className="py-2">Opponent</th>
                <th className="py-2">Win</th>
                <th className="py-2">Loss</th>
                <th className="py-2">Tie</th>
                <th className="py-2">Win Rate</th>
              </tr>
            </thead>
            <tbody>
              {matrix.map((m) => (
                <tr key={m.opp} className="border-t border-border">
                  <td className="py-2 text-white/85">{m.opp}</td>
                  <td className="py-2 font-mono text-emerald">{m.w}</td>
                  <td className="py-2 font-mono text-danger">{m.l}</td>
                  <td className="py-2 font-mono text-white/50">{m.t}</td>
                  <td className="py-2">
                    <div className="flex items-center gap-2">
                      <div className="w-24"><ProgressBar value={(m.w / m.total) * 100} color="#22C55E" /></div>
                      <span className="font-mono text-white/70">{Math.round((m.w / m.total) * 100)}%</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}

function Stat({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <div className="flex items-center justify-between border-b border-border pb-2 last:border-0">
      <span className="text-xs text-white/50">{label}</span>
      <span className="metric text-base" style={{ color }}>{value}</span>
    </div>
  );
}

function Big({ label, value, color }: { label: string; value: React.ReactNode; color: string }) {
  return (
    <div className="rounded-xl border border-border bg-surface p-3 text-center">
      <div className="metric text-2xl" style={{ color }}>{value}</div>
      <div className="card-title mt-1">{label}</div>
    </div>
  );
}

function Health({ label, value, good }: { label: string; value: number; good: boolean }) {
  return (
    <div className="flex items-center justify-between rounded-xl border border-border bg-surface p-2.5">
      <span className="text-xs text-white/55">{label}</span>
      <span className="flex items-center gap-1.5 font-mono text-sm" style={{ color: good ? "#22C55E" : "#EF4444" }}>
        <ShieldCheck size={14} /> {value}
      </span>
    </div>
  );
}

function Row({ k, v }: { k: string; v: string }) {
  return (
    <div className="flex justify-between">
      <span className="text-white/55">{k}</span>
      <span className="font-mono text-white/85">{v}</span>
    </div>
  );
}
