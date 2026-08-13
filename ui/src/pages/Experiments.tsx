import React, { useMemo, useState } from "react";
import { FlaskConical, Plus, BookOpen, Play, CheckCircle2, Clock, XCircle } from "lucide-react";
import { useStore } from "../lib/store";
import { Card, EmptyState, Badge } from "../components/common";

interface Experiment {
  name: string;
  hypothesis: string;
  challenger: string;
  games: number;
  status: "QUEUED" | "RUNNING" | "COMPLETED" | "FAILED";
}

const SEED_HYPOTHESES = [
  { id: "H-01", text: "Delaying land expansion until cash reserves exceed 5k improves final profitability.", status: "Testing", evidence: "Moderate" },
  { id: "H-02", text: "Market-timing sales during price upswings increases win rate vs liquidating immediately.", status: "Pending", evidence: "—" },
  { id: "H-03", text: "Higher worker hire frequency early accelerates catch-up against aggressive opponents.", status: "Testing", evidence: "Low" },
];

export function Experiments() {
  const { dataset } = useStore();
  const [list, setList] = useState<Experiment[]>([]);
  const [name, setName] = useState("");
  const [hyp, setHyp] = useState("");
  const [challenger, setChallenger] = useState("DelayedExpansion-v1");
  const [games, setGames] = useState(30);

  const hypotheses = useMemo(() => {
    const reg = (dataset?.championship?.data as any)?.["hypothesis_registry.json"];
    if (Array.isArray(reg)) return reg;
    return SEED_HYPOTHESES;
  }, [dataset]);

  function add() {
    if (!name.trim()) return;
    setList((l) => [
      { name, hypothesis: hyp || "—", challenger, games, status: "QUEUED" },
      ...l,
    ]);
    setName("");
    setHyp("");
  }

  const statusColor = (s: string) =>
    s === "COMPLETED" ? "#22C55E" : s === "RUNNING" ? "#00D4FF" : s === "FAILED" ? "#EF4444" : "#F5A623";

  return (
    <div className="space-y-4">
      <Card title="Experiment Lab" subtitle="Define a hypothesis and run a champion vs challenger matchup">
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
          <Field label="Experiment Name">
            <input className="inp" value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Delayed Expansion" />
          </Field>
          <Field label="Challenger">
            <input className="inp" value={challenger} onChange={(e) => setChallenger(e.target.value)} />
          </Field>
          <Field label="Hypothesis">
            <textarea className="inp min-h-[60px]" value={hyp} onChange={(e) => setHyp(e.target.value)} placeholder="Describe what you expect to learn…" />
          </Field>
          <Field label="Number of Games">
            <input className="inp" type="number" value={games} onChange={(e) => setGames(Number(e.target.value))} />
          </Field>
        </div>
        <button className="btn btn-primary mt-3" onClick={add}>
          <Plus size={15} /> Queue Experiment
        </button>
      </Card>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card title="Active Experiments" subtitle={`${list.length} queued`}>
          {list.length === 0 ? (
            <div className="py-6 text-center text-sm text-white/40">No experiments queued. Define one above.</div>
          ) : (
            <div className="space-y-2">
              {list.map((e, i) => (
                <div key={i} className="rounded-xl border border-border bg-surface p-3">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-white/90">{e.name}</span>
                    <Badge color={statusColor(e.status)}>{e.status}</Badge>
                  </div>
                  <p className="mt-1 text-xs text-white/55">{e.hypothesis}</p>
                  <div className="mt-2 flex gap-3 text-[11px] text-white/45">
                    <span>Challenger: <span className="text-white/70">{e.challenger}</span></span>
                    <span>Games: <span className="text-white/70">{e.games}</span></span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>

        <Card title="Hypothesis Register" subtitle="Tracked research questions">
          <div className="space-y-2">
            {hypotheses.map((h: any, i: number) => (
              <div key={i} className="rounded-xl border border-border bg-surface p-3">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs text-cyan">{h.id ?? `H-${i + 1}`}</span>
                  <Badge color="#F5A623">{h.status ?? "Pending"}</Badge>
                </div>
                <p className="mt-1 text-sm text-white/80">{h.text}</p>
                {h.evidence && <div className="mt-1 text-[11px] text-white/40">Evidence: {h.evidence}</div>}
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="card-title mb-1 block">{label}</span>
      {children}
    </label>
  );
}
