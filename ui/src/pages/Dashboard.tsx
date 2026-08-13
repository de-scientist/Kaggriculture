import React, { useMemo, useState } from "react";
import { Coins, TrendingUp, Sprout, Map, Users, Rabbit, Boxes, Trophy, Sparkles, ArrowRight } from "lucide-react";
import { useStore } from "../lib/store";
import { getTurn, deriveKpis, coinGap, getChampionWinRate, TURNS_PER_DAY } from "../lib/sim";
import { fmt, signed, pct } from "../lib/format";
import { Card, KpiCard, EmptyState, Badge } from "../components/common";
import { Sparkline, LineChart, ProgressBar } from "../lib/charts";
import { FarmMap } from "../components/farm/FarmMap";

export function Dashboard() {
  const { game, cursor, dataset } = useStore();
  const turn = getTurn(game, cursor);
  const winRate = getChampionWinRate(dataset);
  const kpis = deriveKpis(game, cursor, winRate);

  const coinsSpark = useMemo(() => {
    if (!game) return [];
    return game.money_history.slice(0, cursor + 1).slice(-50);
  }, [game, cursor]);
  const oppSpark = useMemo(() => {
    if (!game) return [];
    return game.opp_money_history.slice(0, cursor + 1).slice(-50);
  }, [game, cursor]);

  const gap = coinGap(turn);
  const gapPct = turn ? (gap / Math.max(1, turn.opp_money)) * 100 : 0;

  const recent = useMemo(() => {
    if (!game) return [];
    return game.actions_log.slice(Math.max(0, cursor - 14), cursor + 1).reverse();
  }, [game, cursor]);

  if (!game || !turn) {
    return <EmptyState icon={<Sprout size={40} />} title="No game loaded" desc="Select a replay from the Replays page." />;
  }

  return (
    <div className="space-y-4">
      {/* KPI CARDS */}
      <div className="grid grid-cols-2 gap-3 md:grid-cols-4 xl:grid-cols-4">
        <KpiCard
          label="Current Coins"
          value={fmt(turn.money)}
          delta={cursor > 1 ? pct(((turn.money - game.money_history[Math.max(0, cursor - 24)]) / Math.max(1, game.money_history[Math.max(0, cursor - 24)])) * 100) : undefined}
          deltaPositive={gap >= 0}
          icon={<Coins size={16} />}
          accent="#22C55E"
          spark={<Sparkline data={coinsSpark} color="#22C55E" width={80} height={26} />}
        />
        <KpiCard
          label="Net Profit"
          value={signed(kpis.netProfit)}
          icon={<TrendingUp size={16} />}
          accent="#00D4FF"
          spark={<Sparkline data={coinsSpark.map((v) => v - 3000)} color="#00D4FF" width={80} height={26} />}
        />
        <KpiCard
          label="Farm Value"
          value={fmt(kpis.farmValue)}
          icon={<Sprout size={16} />}
          accent="#2E7D32"
          spark={<Sparkline data={coinsSpark} color="#2E7D32" width={80} height={26} />}
        />
        <KpiCard
          label="Land Owned"
          value={`${kpis.landOwned}/4`}
          icon={<Map size={16} />}
          accent="#a855f7"
        />
        <KpiCard
          label="Workers"
          value={kpis.workers}
          icon={<Users size={16} />}
          accent="#F5A623"
        />
        <KpiCard
          label="Animals"
          value={kpis.animals}
          icon={<Rabbit size={16} />}
          accent="#22C55E"
        />
        <KpiCard
          label="Inventory Value"
          value={fmt(kpis.inventoryValue)}
          icon={<Boxes size={16} />}
          accent="#00D4FF"
          spark={<Sparkline data={oppSpark} color="#00D4FF" width={80} height={26} />}
        />
        <KpiCard
          label="Win Rate"
          value={winRate !== null ? `${Math.round(winRate * 100)}%` : "—"}
          icon={<Trophy size={16} />}
          accent="#F5A623"
        />
      </div>

      {/* PERFORMANCE + COIN GAP */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card title="Wealth Trajectory" subtitle="Coins over turns" className="lg:col-span-2" bodyClass="px-2">
          <LineChart
            height={240}
            series={[
              { name: "Our Agent", color: "#00D4FF", data: game.money_history.slice(0, cursor + 1) },
              { name: "Opponent", color: "#EF4444", data: game.opp_money_history.slice(0, cursor + 1) },
            ]}
            xLabels={game.turns.slice(0, cursor + 1).map((t) => `D${t.day + 1}·T${t.turn}`)}
          />
          <div className="flex gap-2 px-2 pb-1">
            {(["1D", "5D", "10D", "Full"] as const).map((r) => (
              <span key={r} className="chip border border-border bg-surface text-white/55">
                {r}
              </span>
            ))}
          </div>
        </Card>

        <Card title="Your Advantage" subtitle="Coin gap vs opponent">
          <div className="flex flex-col items-center justify-center py-4">
            <div
              className="metric text-4xl"
              style={{ color: gap >= 0 ? "#22C55E" : "#EF4444" }}
            >
              {gap >= 0 ? "+" : ""}
              {fmt(gap)}
            </div>
            <div className="mt-1 text-xs text-white/45">coins {gap >= 0 ? "ahead" : "behind"}</div>
            <div className="mt-4 w-full">
              <ProgressBar value={gap >= 0 ? Math.min(100, 50 + gapPct / 2) : Math.max(0, 50 + gapPct / 2)} color={gap >= 0 ? "#22C55E" : "#EF4444"} />
              <div className="mt-1 flex justify-between text-[10px] text-white/35">
                <span>Opponent</span>
                <span>Us</span>
              </div>
            </div>
          </div>
          <div className="mt-2 grid grid-cols-2 gap-2 text-center">
            <div className="rounded-lg bg-white/5 p-2">
              <div className="text-[10px] uppercase text-white/40">Our Coins</div>
              <div className="font-mono text-sm text-white">{fmt(turn.money)}</div>
            </div>
            <div className="rounded-lg bg-white/5 p-2">
              <div className="text-[10px] uppercase text-white/40">Opponent</div>
              <div className="font-mono text-sm text-white">{fmt(turn.opp_money)}</div>
            </div>
          </div>
        </Card>
      </div>

      {/* FARM MAP + AI STREAM */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card title="Farm Map" subtitle="Live board state" className="lg:col-span-2">
          <FarmMap turn={turn} />
        </Card>

        <Card
          title="AI Decision Stream"
          subtitle="Recent actions"
          action={<Badge color="#00D4FF"><Sparkles size={11} /> LIVE</Badge>}
          bodyClass="max-h-[360px] overflow-y-auto space-y-2"
        >
          {recent.map((a, i) => (
            <div key={i} className="rounded-lg border border-border bg-surface px-3 py-2">
              <div className="flex items-center justify-between">
                <span className="font-mono text-[11px] text-white/40">Turn {a.turn}</span>
                <span className="text-[11px] text-white/55">{a.decision.strategy_mode}</span>
              </div>
              <div className="mt-0.5 text-sm text-white/85">{a.decision.summary}</div>
              <div className="mt-1 flex items-center gap-2">
                <span className="text-[11px] text-cyan">{a.decision.type}</span>
                <span className="text-[11px] text-white/40">
                  conf {Math.round(a.decision.confidence.value * 100)}%
                </span>
              </div>
            </div>
          ))}
        </Card>
      </div>

      {/* MARKET / WORKERS / INVENTORY */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <Card title="Market Snapshot" subtitle="Top prices">
          <MarketMini turn={turn} />
        </Card>
        <Card title="Workers" subtitle={`${kpis.workers} units active`}>
          <div className="space-y-1.5">
            <WorkerRow label="Main Farmer" eff={92} />
            {turn.farm.hands.map((_, i) => (
              <WorkerRow key={i} label={`Hand #${i + 1}`} eff={80 + ((i * 7) % 18)} />
            ))}
            {kpis.workers === 1 && <div className="text-xs text-white/40">No hired hands this day.</div>}
          </div>
        </Card>
        <Card title="Inventory" subtitle={`${Object.values(turn.private.shed).reduce((s: number, v) => s + (v as number), 0)} units stored`}>
          <InventoryMini turn={turn} />
        </Card>
      </div>
    </div>
  );
}

function WorkerRow({ label, eff }: { label: string; eff: number }) {
  return (
    <div>
      <div className="flex justify-between text-xs">
        <span className="text-white/70">{label}</span>
        <span className="text-white/45">eff {eff}%</span>
      </div>
      <ProgressBar value={eff} color="#F5A623" />
    </div>
  );
}

function MarketMini({ turn }: { turn: ReturnType<typeof getTurn> }) {
  if (!turn) return null;
  const entries = Object.entries(turn.market.prices)
    .sort((a, b) => (b[1] as number) - (a[1] as number))
    .slice(0, 5);
  return (
    <div className="space-y-1.5">
      {entries.map(([k, v]) => (
        <div key={k} className="flex items-center justify-between text-sm">
          <span className="text-white/70">{k}</span>
          <span className="font-mono text-white/90">{v as number}c</span>
        </div>
      ))}
    </div>
  );
}

function InventoryMini({ turn }: { turn: ReturnType<typeof getTurn> }) {
  if (!turn) return null;
  const entries = Object.entries(turn.private.shed).filter(([, v]) => (v as number) > 0);
  if (entries.length === 0) return <div className="text-xs text-white/40">Shed empty.</div>;
  return (
    <div className="space-y-1.5">
      {entries.map(([k, v]) => (
        <div key={k} className="flex items-center justify-between text-sm">
          <span className="text-white/70">{k}</span>
          <span className="font-mono text-white/90">{v as number}</span>
        </div>
      ))}
    </div>
  );
}
