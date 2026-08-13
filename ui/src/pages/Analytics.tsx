import React, { useMemo } from "react";
import { BarChart3, TrendingUp, Sprout, Users, Map, Rabbit, Boxes } from "lucide-react";
import { useStore } from "../lib/store";
import { getTurn, cropTimeline, animalCount, CROPS, ANIMALS, TURNS_PER_DAY } from "../lib/sim";
import { Card, EmptyState } from "../components/common";
import { LineChart, Bars, ProgressBar } from "../lib/charts";
import { cropColor, cropEmoji, fmt } from "../lib/format";

export function Analytics() {
  const { game, cursor } = useStore();
  const turn = getTurn(game, cursor);

  const series = useMemo(() => {
    if (!game) return null;
    const workers = game.turns.map((t) => 1 + t.farm.hands.length);
    const land = game.turns.map((t) => t.farm.unlocked_quadrants.length);
    const plants = game.turns.map((t) => {
      let n = 0;
      for (const row of t.farm.tiles)
        for (const tile of row)
          if (tile && typeof tile === "object" && tile.kind === "PLANT") n++;
      return n;
    });
    return { workers, land, plants };
  }, [game]);

  if (!game || !turn || !series) return <EmptyState icon={<BarChart3 size={40} />} title="No analytics data" />;

  const cropCounts = CROPS.map((c) => ({
    label: c.slice(0, 3),
    value: game!.turns[cursor].farm.tiles.flat().filter(
      (t) => t && typeof t === "object" && t.kind === "PLANT" && t.crop === c
    ).length,
    color: cropColor(c),
  }));

  const animalCounts = ANIMALS.map((a) => ({
    label: a.slice(0, 3),
    value: animalCount(game, cursor, a),
    color: "#22C55E",
  }));

  const invBars = Object.entries(turn.private.shed)
    .filter(([, v]) => (v as number) > 0)
    .map(([k, v]) => ({ label: k.slice(0, 3), value: v as number, color: cropColor(k) }));

  const netProfit = game.money_history.slice(0, cursor + 1).map((v) => v - 3000);

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card title="Economic Performance" subtitle="Net profit over time" icon>
          <LineChart height={220} series={[{ name: "Net Profit", color: "#22C55E", data: netProfit }]} xLabels={game.turns.slice(0, cursor + 1).map((t) => `D${t.day + 1}`)} />
        </Card>
        <Card title="Cash Flow" subtitle="Coins vs opponent">
          <LineChart height={220} series={[
            { name: "Us", color: "#00D4FF", data: game.money_history.slice(0, cursor + 1) },
            { name: "Opp", color: "#EF4444", data: game.opp_money_history.slice(0, cursor + 1) },
          ]} xLabels={game.turns.slice(0, cursor + 1).map((t) => `D${t.day + 1}`)} />
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card title="Workers" subtitle="Active units over time">
          <LineChart height={200} series={[{ name: "Workers", color: "#F5A623", data: series.workers.slice(0, cursor + 1) }]} xLabels={game.turns.slice(0, cursor + 1).map((t) => `D${t.day + 1}`)} />
        </Card>
        <Card title="Land" subtitle="Quadrants unlocked">
          <LineChart height={200} series={[{ name: "Quadrants", color: "#a855f7", data: series.land.slice(0, cursor + 1) }]} xLabels={game.turns.slice(0, cursor + 1).map((t) => `D${t.day + 1}`)} />
        </Card>
        <Card title="Production" subtitle="Living plants over time">
          <LineChart height={200} series={[{ name: "Plants", color: "#2E7D32", data: series.plants.slice(0, cursor + 1) }]} xLabels={game.turns.slice(0, cursor + 1).map((t) => `D${t.day + 1}`)} />
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card title="Crop Production" subtitle="Living plants by crop">
          <Bars data={cropCounts} height={160} />
        </Card>
        <Card title="Animals" subtitle="Count by species">
          <Bars data={animalCounts} height={160} />
        </Card>
        <Card title="Inventory" subtitle="Units in shed">
          {invBars.length ? <Bars data={invBars} height={160} /> : <div className="text-sm text-white/40">Shed empty.</div>}
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card title="Crop Yields" subtitle="Estimated standing value">
          <div className="space-y-2">
            {CROPS.map((c) => {
              const count = cropCounts.find((x) => x.label === c.slice(0, 3))?.value ?? 0;
              const price = turn.market.prices[c] ?? 0;
              return (
                <div key={c} className="flex items-center gap-2 text-sm">
                  <span className="w-24 text-white/70">{cropEmoji(c)} {c}</span>
                  <div className="flex-1"><ProgressBar value={count * price} color={cropColor(c)} /></div>
                  <span className="w-16 text-right font-mono text-white/70">{fmt(count * price)}</span>
                </div>
              );
            })}
          </div>
        </Card>
        <Card title="Asset Allocation" subtitle="Value breakdown">
          <div className="space-y-2">
            <Alloc label="Cash" value={turn.money} total={turn.money + 1} color="#22C55E" />
            <Alloc label="Inventory" value={Object.entries(turn.private.shed).reduce((s, [k, v]) => s + (v as number) * (turn.market.prices[k] ?? 1), 0)} total={turn.money + 1} color="#00D4FF" />
            <Alloc label="Standing crops" value={series.plants[cursor] * 40} total={turn.money + 1} color="#2E7D32" />
          </div>
        </Card>
      </div>
    </div>
  );
}

function Alloc({ label, value, total, color }: { label: string; value: number; total: number; color: string }) {
  return (
    <div>
      <div className="mb-1 flex justify-between text-sm">
        <span className="text-white/70">{label}</span>
        <span className="font-mono text-white/85">{fmt(value)}</span>
      </div>
      <ProgressBar value={(value / Math.max(1, total)) * 100} color={color} />
    </div>
  );
}
