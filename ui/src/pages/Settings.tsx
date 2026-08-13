import React, { useState } from "react";
import { Settings as SettingsIcon, ShieldCheck, Cpu, Palette, Bell, Database, Bot, Gauge, Wrench } from "lucide-react";
import { useStore } from "../lib/store";
import { Card, EmptyState, Badge } from "../components/common";

export function Settings() {
  const { dataset, developer, setDeveloper } = useStore();
  const [champion, setChampion] = useState("champion-v1.0");
  const [speed, setSpeed] = useState(5);
  const [opponent, setOpponent] = useState("random");

  if (!dataset) return <EmptyState icon={<SettingsIcon size={40} />} title="No settings context" />;

  return (
    <div className="space-y-4">
      <div className="rounded-2xl border border-amber/30 bg-amber/10 p-3 text-xs text-amber">
        <ShieldCheck size={14} className="mr-1 inline" />
        <strong>Competition Safety.</strong> Changes here affect the local visualization/sandbox only. The official
        autonomous submission agent is never modified by this UI.
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card title="Agent" subtitle="Select active policy">
          <Toggle label="Champion / Challenger" value={champion} options={["champion-v1.0", "DelayedExpansion-v1", "MarketTiming-v1"]} onChange={setChampion} />
          <Toggle label="Strategy Mode" value="adaptive" options={["adaptive", "aggressive", "conservative"]} onChange={() => {}} />
        </Card>

        <Card title="Simulation" subtitle="Local sandbox parameters">
          <Field label="Starting Seed">
            <input className="inp" defaultValue={0} type="number" />
          </Field>
          <Field label="Season Length (turns)">
            <input className="inp" defaultValue={720} type="number" />
          </Field>
          <Field label="Opponent">
            <select className="inp" value={opponent} onChange={(e) => setOpponent(e.target.value)}>
              <option>random</option>
              <option>starter</option>
              <option>pass</option>
            </select>
          </Field>
          <Field label={`Default Speed (${speed}×)`}>
            <input className="inp" type="range" min={1} max={100} value={speed} onChange={(e) => setSpeed(Number(e.target.value))} />
          </Field>
        </Card>

        <Card title="Appearance">
          <div className="flex items-center justify-between py-1">
            <span className="text-sm text-white/70">Theme</span>
            <Badge color="#00D4FF" solid>DARK · FOREST</Badge>
          </div>
          <div className="flex items-center justify-between py-1">
            <span className="text-sm text-white/70">Accent</span>
            <span className="font-mono text-xs text-cyan">#00D4FF</span>
          </div>
        </Card>

        <Card title="Telemetry & Performance">
          <div className="flex items-center justify-between py-1">
            <span className="text-sm text-white/70">Emit performance metrics</span>
            <On />
          </div>
          <div className="flex items-center justify-between py-1">
            <span className="text-sm text-white/70">Log decision latency</span>
            <On />
          </div>
          <div className="flex items-center justify-between py-1">
            <span className="text-sm text-white/70">Stream logs to UI</span>
            <On />
          </div>
        </Card>

        <Card title="AI Assistant">
          <div className="flex items-center justify-between py-1">
            <span className="text-sm text-white/70">Enable Farm AI chat</span>
            <On />
          </div>
          <div className="flex items-center justify-between py-1">
            <span className="text-sm text-white/70">Grounded responses only</span>
            <On />
          </div>
        </Card>

        <Card title="Notifications">
          <div className="flex items-center justify-between py-1">
            <span className="text-sm text-white/70">Fallback triggered</span>
            <On />
          </div>
          <div className="flex items-center justify-between py-1">
            <span className="text-sm text-white/70">Experiment completed</span>
            <On />
          </div>
        </Card>

        <Card title="Developer">
          <div className="flex items-center justify-between py-1">
            <div>
              <div className="text-sm text-white/80">Developer Mode</div>
              <div className="text-[11px] text-white/40">Expose raw observations, actions, timings, stack traces.</div>
            </div>
            <button
              onClick={() => setDeveloper(!developer)}
              className={`relative h-6 w-11 rounded-full transition-colors ${developer ? "bg-cyan" : "bg-white/10"}`}
            >
              <span className={`absolute top-0.5 h-5 w-5 rounded-full bg-white transition-all ${developer ? "left-[22px]" : "left-0.5"}`} />
            </button>
          </div>
        </Card>
      </div>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="mb-2 block">
      <span className="card-title mb-1 block">{label}</span>
      {children}
    </label>
  );
}

function Toggle({ label, value, options, onChange }: { label: string; value: string; options: string[]; onChange: (v: string) => void }) {
  return (
    <div className="mb-3">
      <div className="card-title mb-1">{label}</div>
      <div className="flex flex-wrap gap-1.5">
        {options.map((o) => (
          <button
            key={o}
            onClick={() => onChange(o)}
            className={`rounded-lg border px-2.5 py-1 text-xs ${
              value === o ? "border-cyan/40 bg-cyan/15 text-cyan" : "border-border bg-surface text-white/55"
            }`}
          >
            {o}
          </button>
        ))}
      </div>
    </div>
  );
}

function On() {
  return <span className="chip border border-emerald/40 bg-emerald/10 text-emerald">ON</span>;
}
