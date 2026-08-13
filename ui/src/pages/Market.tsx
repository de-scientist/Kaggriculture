import React, { useMemo, useState } from "react";
import { LineChart as LineIcon, Flame, TrendingUp, TrendingDown, Minus, ShieldAlert } from "lucide-react";
import { useStore } from "../lib/store";
import { getTurn, deriveMarket, PRODUCTS } from "../lib/sim";
import { Card, EmptyState, Badge } from "../components/common";
import { LineChart, ProgressBar } from "../lib/charts";
import { cropEmoji } from "../lib/format";
import { Tabs } from "../components/common";

const TREND_ICON = { up: TrendingUp, down: TrendingDown, flat: Minus };

export function Market() {
  const { game, cursor, dataset } = useStore();
  const turn = getTurn(game, cursor);
  const [active, setActive] = useState<string>("WHEAT");

  const rows = useMemo(() => deriveMarket(game, cursor), [game, cursor]);

  const priceSeries = useMemo(() => {
    if (!game) return [];
    const p = game.price_history[active] ?? [];
    return p.slice(0, cursor + 1);
  }, [game, cursor, active]);

  if (!game || !turn) return <EmptyState icon={<LineIcon size={40} />} title="No market data" />;

  const sorted = [...rows].sort((a, b) => b.price - a.price);
  const top = sorted[0];
  const glut = [...rows].sort((a, b) => b.supply - a.supply)[0];

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card title={`Price History — ${active}`} subtitle="Per-unit sale price" className="lg:col-span-2" bodyClass="px-2">
          <Tabs
            tabs={PRODUCTS.filter((p) => p !== "FERTILIZER").map((p) => ({ id: p, label: p.slice(0, 4) }))}
            active={active}
            onChange={setActive}
          />
          <div className="mt-3">
            <LineChart
              height={240}
              series={[{ name: active, color: "#00D4FF", data: priceSeries }]}
              xLabels={game.turns.slice(0, cursor + 1).map((t) => `D${t.day + 1}`)}
            />
          </div>
        </Card>

        <Card title="Market AI Advisor" subtitle="Grounded in live data">
          <div className="space-y-3">
            <div className="rounded-2xl border border-ag/30 bg-ag/10 p-3">
              <div className="card-title flex items-center gap-1.5">
                <Flame size={12} className="text-amber" /> Market Signal
              </div>
              <p className="mt-1.5 text-sm text-white/80">
                <span className="font-semibold text-white">{top.product}</span> is the strongest price at{" "}
                <span className="font-mono text-cyan">{top.price}c</span> (trend {top.trend}). Consider selling
                inventory into strength.
              </p>
            </div>
            <div className="rounded-2xl border border-border bg-surface p-3">
              <div className="card-title flex items-center gap-1.5">
                <ShieldAlert size={12} className="text-amber" /> Risk
              </div>
              <p className="mt-1.5 text-sm text-white/70">
                {glut.product} shows a glut (supply {glut.supply}) — large-volume sales may push its price toward
                the floor. Phase liquidation.
              </p>
            </div>
          </div>
        </Card>
      </div>

      <Card title="Market Heatmap" subtitle="Demand · Supply · Price · Trend">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-[11px] uppercase tracking-wide text-white/40">
                <th className="py-2">Commodity</th>
                <th className="py-2">Price</th>
                <th className="py-2">Change</th>
                <th className="py-2">Supply</th>
                <th className="py-2">Demand</th>
                <th className="py-2">Trend</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => {
                const Trend = TREND_ICON[r.trend];
                const trendColor = r.trend === "up" ? "#22C55E" : r.trend === "down" ? "#EF4444" : "#94a3b8";
                return (
                  <tr key={r.product} className="border-t border-border">
                    <td className="py-2">
                      <span className="mr-2">{cropEmoji(r.product)}</span>
                      <span className="text-white/85">{r.product}</span>
                      <Badge color={r.level === "HIGH" ? "#EF4444" : r.level === "MEDIUM" ? "#F5A623" : "#22C55E"}>
                        {r.level}
                      </Badge>
                    </td>
                    <td className="py-2 font-mono text-white/90">{r.price}c</td>
                    <td className="py-2 font-mono" style={{ color: r.change >= 0 ? "#22C55E" : "#EF4444" }}>
                      {r.change >= 0 ? "+" : ""}
                      {r.change.toFixed(1)}%
                    </td>
                    <td className="py-2">
                      <div className="flex items-center gap-2">
                        <div className="w-20">
                          <ProgressBar value={(r.supply / 100) * 100} color="#64748b" />
                        </div>
                        <span className="font-mono text-white/55">{r.supply}</span>
                      </div>
                    </td>
                    <td className="py-2 font-mono text-white/55">{r.demand}</td>
                    <td className="py-2">
                      <Trend size={16} style={{ color: trendColor }} />
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </Card>

      <Card title="Town Demand" subtitle="Active shops consume product">
        <div className="flex flex-wrap gap-2">
          {turn.town.unlocked_shops.length === 0 && (
            <span className="text-sm text-white/40">Only the town center is active.</span>
          )}
          {turn.town.unlocked_shops.map((s) => (
            <Badge key={s} color="#2E7D32" solid>
              {s}
            </Badge>
          ))}
        </div>
        <p className="mt-2 text-xs text-white/45">
          Town center demands 1 of each product every 12 turns (2× after day 10, 4× after day 20). Shops unlock every 3
          days.
        </p>
      </Card>
    </div>
  );
}
