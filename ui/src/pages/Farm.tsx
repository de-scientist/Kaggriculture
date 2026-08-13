import React, { useState } from "react";
import { Sprout, Lock, Users, Rabbit, Wheat, Boxes } from "lucide-react";
import { useStore } from "../lib/store";
import { getTurn } from "../lib/sim";
import { cropEmoji, cropColor } from "../lib/format";
import { Card, EmptyState, Badge } from "../components/common";
import { FarmMap } from "../components/farm/FarmMap";
import { ProgressBar } from "../lib/charts";

export function Farm() {
  const { game, cursor } = useStore();
  const turn = getTurn(game, cursor);
  const [sel, setSel] = useState<{ x: number; y: number } | null>(null);

  if (!game || !turn) return <EmptyState icon={<Sprout size={40} />} title="No farm data" />;

  const size = turn.farm.tiles.length;
  const quads = ["NW", "NE", "SW", "SE"];
  const quadStatus = quads.map((q) => ({
    q,
    owned: turn!.farm.unlocked_quadrants.includes(q),
  }));

  let plants = 0,
    animals = 0,
    weeds = 0,
    locked = 0;
  for (const row of turn.farm.tiles)
    for (const tile of row) {
      if (tile === "LOCKED") locked++;
      else if (tile && typeof tile === "object") {
        if (tile.kind === "WEED") weeds++;
        else if (tile.kind === "PLANT") plants++;
        else if ((tile.kind === "COOP" || tile.kind === "PASTURE") && tile.animal) animals++;
      }
    }

  const selTile = sel ? turn.farm.tiles[sel.y]?.[sel.x] : null;

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        <Stat icon={<Sprout size={15} />} label="Plants" value={plants} color="#2E7D32" />
        <Stat icon={<Rabbit size={15} />} label="Animals" value={animals} color="#22C55E" />
        <Stat icon={<Lock size={15} />} label="Locked" value={locked} color="#64748b" />
        <Stat icon={<Wheat size={15} />} label="Weeds" value={weeds} color="#F5A623" />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card title="Farm Board" subtitle="Click a tile for details" className="lg:col-span-2">
          <FarmMap turn={turn} selected={sel} onSelect={setSel} />
          <div className="mt-3 flex flex-wrap gap-3 text-[11px] text-white/50">
            <Legend color="#00D4FF" label="Farmer" dot />
            <Legend color="#F5A623" label="Hired hand" dot />
            <Legend color="rgba(46,125,50,0.3)" label="Plant" />
            <Legend color="rgba(120,90,30,0.3)" label="Weed" />
            <Legend color="rgba(0,0,0,0.4)" label="Locked" />
          </div>
        </Card>

        <div className="space-y-4">
          <Card title="Quadrants">
            <div className="grid grid-cols-2 gap-2">
              {quadStatus.map(({ q, owned }) => (
                <div
                  key={q}
                  className={`rounded-xl border p-3 ${
                    owned ? "border-ag/40 bg-ag/10" : "border-border bg-surface"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-semibold text-white/85">{q}</span>
                    {owned ? (
                      <Badge color="#22C55E" solid>
                        Owned
                      </Badge>
                    ) : (
                      <Badge color="#64748b">Locked</Badge>
                    )}
                  </div>
                  <div className="mt-1 text-[11px] text-white/40">
                    {owned ? "Operational" : "Available to buy"}
                  </div>
                </div>
              ))}
            </div>
          </Card>

          <Card title="Tile Inspector" subtitle={sel ? `(${sel.x}, ${sel.y})` : "Select a tile"}>
            {!selTile ? (
              <div className="py-6 text-center text-sm text-white/40">No tile selected.</div>
            ) : selTile === "LOCKED" ? (
              <Detail title="Locked Quadrant" body="Buy this land via BUY_LAND to unlock planting." color="#64748b" />
            ) : selTile === null ? (
              <Detail title="Empty Tile" body="Unlocked and ready for planting or building." color="#2E7D32" />
            ) : selTile.kind === "WEED" ? (
              <Detail title="Weed" body="Clear with DIG to free the tile." color="#F5A623" />
            ) : selTile.kind === "PLANT" ? (
              <PlantDetail tile={selTile} day={turn.day} />
            ) : (
              <StructureDetail tile={selTile} />
            )}
          </Card>

          <Card title="Workforce" subtitle={`${1 + turn.farm.hands.length} units`}>
            <div className="space-y-1.5 text-sm">
              <div className="flex justify-between">
                <span className="text-white/70">Main Farmer</span>
                <span className="font-mono text-white/60">
                  ({turn.farm.farmer[0]},{turn.farm.farmer[1]})
                </span>
              </div>
              {turn.farm.hands.map((h, i) => (
                <div key={i} className="flex justify-between">
                  <span className="text-white/70">Hand #{i + 1}</span>
                  <span className="font-mono text-white/60">
                    ({h[0]},{h[1]})
                  </span>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}

function Stat({ icon, label, value, color }: { icon: React.ReactNode; label: string; value: number; color: string }) {
  return (
    <div className="glass flex items-center gap-3 p-3">
      <span style={{ color }}>{icon}</span>
      <div>
        <div className="metric text-xl text-white">{value}</div>
        <div className="card-title">{label}</div>
      </div>
    </div>
  );
}

function Legend({ color, label, dot }: { color: string; label: string; dot?: boolean }) {
  return (
    <span className="flex items-center gap-1.5">
      {dot ? (
        <span className="h-2 w-2 rounded-full" style={{ background: color }} />
      ) : (
        <span className="h-3 w-3 rounded" style={{ background: color }} />
      )}
      {label}
    </span>
  );
}

function Detail({ title, body, color }: { title: string; body: string; color: string }) {
  return (
    <div>
      <div className="text-sm font-semibold" style={{ color }}>
        {title}
      </div>
      <p className="mt-1 text-xs text-white/55">{body}</p>
    </div>
  );
}

function PlantDetail({ tile, day }: { tile: any; day: number }) {
  const age = day - tile.planted_day;
  const c = cropColor(tile.crop);
  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        <span className="text-xl">{cropEmoji(tile.crop)}</span>
        <span className="text-sm font-semibold text-white/90">{tile.crop}</span>
      </div>
      <Row k="Growth" v={`${age} days`} />
      <Row k="Yield units" v={`${tile.yield_units}`} />
      <Row k="Watered today" v={tile.watered_today ? "Yes" : "No"} />
      <Row k="Consecutive unwatered" v={`${tile.consecutive_unwatered}`} />
      <Row k="Fertilized until" v={`Day ${tile.fertilized_until_day}`} />
      <div>
        <div className="mb-1 flex justify-between text-[11px] text-white/45">
          <span>Yield fill</span>
          <span>{Math.min(100, tile.yield_units * 12)}%</span>
        </div>
        <ProgressBar value={tile.yield_units * 12} color={c} />
      </div>
    </div>
  );
}

function StructureDetail({ tile }: { tile: any }) {
  const isCoop = tile.kind === "COOP";
  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        <span className="text-xl">{isCoop ? "🏠" : "🌾"}</span>
        <span className="text-sm font-semibold text-white/90">
          {isCoop ? "Coop" : "Pasture"}
        </span>
      </div>
      {tile.animal ? (
        <>
          <Row k="Animal" v={`${cropEmoji(tile.animal)} ${tile.animal}`} />
          <Row k="Fed today" v={tile.fed_today ? "Yes" : "No"} />
          <Row k="Yield units" v={`${tile.yield_units ?? 0}`} />
          <Row k="Pending care bonus" v={`${tile.pending_care_bonus ?? 0}`} />
          <Row k="Fertilizer avail." v={`${tile.fertilizer_available ?? 0}`} />
        </>
      ) : (
        <p className="text-xs text-white/55">Empty structure — place an animal.</p>
      )}
    </div>
  );
}

function Row({ k, v }: { k: string; v: string }) {
  return (
    <div className="flex justify-between text-sm">
      <span className="text-white/55">{k}</span>
      <span className="text-white/85">{v}</span>
    </div>
  );
}
