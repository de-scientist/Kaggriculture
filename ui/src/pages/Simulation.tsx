import React from "react";
import { Play, Pause, SkipBack, SkipForward, Gauge, ShieldAlert, Check, X, Bot, Hand, UserCog } from "lucide-react";
import { useStore } from "../lib/store";
import { getTurn } from "../lib/sim";
import { Card, EmptyState, Badge } from "../components/common";
import { FarmMap } from "../components/farm/FarmMap";
import { ProgressBar } from "../lib/charts";

const SPEEDS = [1, 2, 5, 10, 25, 100];

export function Simulation() {
  const { game, cursor, playing, speed, mode, play, pause, step, setSpeed, setMode, setCursor } = useStore();
  const turn = getTurn(game, cursor);
  if (!game || !turn) return <EmptyState title="No simulation loaded" desc="Load a replay from the Replays page to control playback." />;

  const max = game.turns.length - 1;

  return (
    <div className="space-y-4">
      {/* CONTROL BAR */}
      <Card bodyClass="space-y-3">
        <div className="flex flex-wrap items-center gap-2">
          <button className="btn" onClick={() => step(-1)} title="Previous turn">
            <SkipBack size={16} />
          </button>
          {playing ? (
            <button className="btn btn-primary" onClick={pause}>
              <Pause size={16} /> Pause
            </button>
          ) : (
            <button className="btn btn-primary" onClick={play}>
              <Play size={16} /> Play
            </button>
          )}
          <button className="btn" onClick={() => step(1)} title="Next turn">
            <SkipForward size={16} />
          </button>

          <div className="ml-2 flex items-center gap-1 rounded-xl border border-border bg-surface p-1">
            <Gauge size={14} className="text-white/40" />
            {SPEEDS.map((s) => (
              <button
                key={s}
                onClick={() => setSpeed(s)}
                className={`rounded-lg px-2 py-1 text-xs font-medium ${
                  speed === s ? "bg-cyan/20 text-cyan" : "text-white/50 hover:text-white"
                }`}
              >
                {s}×
              </button>
            ))}
          </div>

          <div className="ml-auto flex items-center gap-1 rounded-xl border border-border bg-surface p-1">
            <ModeBtn id="autonomous" icon={<Bot size={14} />} label="Autonomous" active={mode === "autonomous"} onClick={() => setMode("autonomous")} />
            <ModeBtn id="assisted" icon={<Hand size={14} />} label="Assisted" active={mode === "assisted"} onClick={() => setMode("assisted")} />
            <ModeBtn id="manual" icon={<UserCog size={14} />} label="Manual" active={mode === "manual"} onClick={() => setMode("manual")} />
          </div>
        </div>

        <div>
          <div className="mb-1 flex justify-between text-xs text-white/45">
            <span>Turn {turn.turn} / {max}</span>
            <span>Day {turn.day + 1} / 30 · Hour {turn.hour + 1}</span>
          </div>
          <input
            type="range"
            min={0}
            max={max}
            value={cursor}
            onChange={(e) => setCursor(Number(e.target.value))}
            className="w-full accent-cyan"
          />
          <ProgressBar value={(cursor / max) * 100} color="#00D4FF" />
        </div>

        {mode !== "autonomous" && (
          <div className="flex items-start gap-2 rounded-xl border border-amber/30 bg-amber/10 p-3 text-xs text-amber">
            <ShieldAlert size={16} className="mt-0.5 shrink-0" />
            <div>
              <strong>SANDBOX MODE.</strong> Human actions affect this local simulation view only. This does not modify
              the official autonomous submission agent, which runs independently.
            </div>
          </div>
        )}
      </Card>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card title="Live Board" className="lg:col-span-2">
          <FarmMap turn={turn} />
        </Card>
        <div className="space-y-4">
          <Card title="Current Decision">
            <div className="text-sm font-semibold text-white/90">{turn.decision.summary}</div>
            <div className="mt-1 flex items-center gap-2">
              <Badge color="#00D4FF" solid>{turn.decision.type}</Badge>
              <Badge color="#2E7D32">{turn.decision.strategy_mode}</Badge>
            </div>
            <div className="mt-3 text-xs text-white/55">
              Confidence {Math.round(turn.decision.confidence.value * 100)}%
            </div>
          </Card>

          {mode === "assisted" && (
            <Card title="Recommended Action" subtitle="Approve or reject">
              <div className="text-sm text-white/85">{turn.decision.summary}</div>
              <div className="mt-3 flex gap-2">
                <button className="btn btn-primary flex-1"><Check size={15} /> Approve</button>
                <button className="btn flex-1"><X size={15} /> Reject</button>
              </div>
            </Card>
          )}

          {mode === "manual" && (
            <Card title="Manual Actions" subtitle="Legal ops only">
              <div className="grid grid-cols-2 gap-1.5 text-xs">
                {["NORTH", "SOUTH", "EAST", "WEST", "PLANT", "WATER", "HARVEST", "FERTILIZE", "FEED", "DIG", "BUILD_COOP", "BUILD_PASTURE"].map((a) => (
                  <button key={a} className="rounded-lg border border-border bg-surface px-2 py-1.5 text-white/70 hover:border-cyan/40 hover:text-white">
                    {a}
                  </button>
                ))}
              </div>
              <p className="mt-2 text-[11px] text-white/40">
                Actions pass through validation before reaching the environment. Invalid ops are rejected silently.
              </p>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}

function ModeBtn({ id, icon, label, active, onClick }: { id: string; icon: React.ReactNode; label: string; active: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs font-medium ${
        active ? "bg-cyan/20 text-cyan" : "text-white/50 hover:text-white"
      }`}
    >
      {icon}
      {label}
    </button>
  );
}
