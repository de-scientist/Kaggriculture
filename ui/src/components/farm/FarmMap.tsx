import React, { useState } from "react";
import { Turn } from "../../types";
import { cropEmoji, cropColor } from "../../lib/format";
import { CROPS, ANIMALS } from "../../lib/sim";

interface Hover {
  x: number;
  y: number;
  px: number;
  py: number;
  text: string;
}

function tileText(turn: Turn, x: number, y: number): string {
  const tile = turn.farm.tiles[y]?.[x];
  if (!tile) return `(${x},${y}) Empty`;
  if (tile === "LOCKED") return `(${x},${y}) Locked quadrant`;
  if (tile.kind === "WEED") return `(${x},${y}) Weed — clear with DIG`;
  if (tile.kind === "PLANT") {
    const age = turn.day - tile.planted_day;
    return `(${x},${y}) ${tile.crop} — yield ${tile.yield_units}, age ${age}d, watered:${tile.watered_today}`;
  }
  if (tile.kind === "COOP" || tile.kind === "PASTURE") {
    const kind = tile.kind === "COOP" ? "Coop" : "Pasture";
    if (tile.animal)
      return `(${x},${y}) ${kind}: ${tile.animal} — fed:${tile.fed_today}, yield:${tile.yield_units ?? 0}`;
    return `(${x},${y}) Empty ${kind}`;
  }
  return `(${x},${y})`;
}

function Cell({
  turn,
  x,
  y,
  onHover,
  onLeave,
  onClick,
  selected,
}: {
  turn: Turn;
  x: number;
  y: number;
  onHover: (h: Hover | null) => void;
  onLeave: () => void;
  onClick: () => void;
  selected: boolean;
}) {
  const tile = turn.farm.tiles[y]?.[x];
  const isFarmer = turn.farm.farmer[0] === x && turn.farm.farmer[1] === y;
  const isHand = turn.farm.hands.some(([hx, hy]) => hx === x && hy === y);

  let bg = "rgba(255,255,255,0.025)";
  let content: React.ReactNode = null;
  let sub: React.ReactNode = null;

  if (tile === "LOCKED") {
    bg = "rgba(0,0,0,0.35)";
    content = <span className="text-white/20">▦</span>;
  } else if (tile && typeof tile === "object") {
    if (tile.kind === "WEED") {
      bg = "rgba(120,90,30,0.18)";
      content = <span>🌿</span>;
    } else if (tile.kind === "PLANT") {
      const c = cropColor(tile.crop);
      bg = `${c}14`;
      const maxY = Math.max(6, tile.yield_units, 1);
      const pctv = Math.min(100, (tile.yield_units / maxY) * 100);
      content = <span className="text-base leading-none">{cropEmoji(tile.crop)}</span>;
      sub = (
        <span
          className="absolute bottom-0 left-0 h-[3px]"
          style={{ width: `${pctv}%`, background: c }}
        />
      );
    } else if (tile.kind === "COOP" || tile.kind === "PASTURE") {
      bg = tile.animal ? "rgba(46,125,50,0.18)" : "rgba(255,255,255,0.04)";
      const icon = tile.kind === "COOP" ? "🏠" : "🌾";
      content = (
        <span className="text-sm leading-none">
          {icon}
          {tile.animal ? cropEmoji(tile.animal) : ""}
        </span>
      );
    }
  }

  return (
    <button
      onClick={onClick}
      onMouseEnter={(e) =>
        onHover({
          x,
          y,
          px: e.clientX,
          py: e.clientY,
          text: tileText(turn, x, y),
        })
      }
      onMouseMove={(e) =>
        onHover({ x, y, px: e.clientX, py: e.clientY, text: tileText(turn, x, y) })
      }
      onMouseLeave={onLeave}
      className={`relative flex aspect-square items-center justify-center rounded-[5px] border text-center transition-colors ${
        selected ? "border-cyan" : "border-white/5 hover:border-white/20"
      }`}
      style={{ background: bg }}
    >
      {content}
      {sub}
      {isFarmer && (
        <span className="absolute -right-1 -top-1 h-2.5 w-2.5 rounded-full bg-cyan ring-2 ring-bg" />
      )}
      {isHand && (
        <span className="absolute -bottom-1 -left-1 h-2 w-2 rounded-full bg-amber ring-2 ring-bg" />
      )}
    </button>
  );
}

export function FarmMap({
  turn,
  onSelect,
  selected,
  showQuadrantLabels = true,
}: {
  turn: Turn | null;
  onSelect?: (x: number, y: number) => void;
  selected?: { x: number; y: number } | null;
  showQuadrantLabels?: boolean;
}) {
  const [hover, setHover] = useState<Hover | null>(null);
  if (!turn) return <div className="text-white/40">No farm state.</div>;

  const size = turn.farm.tiles.length;

  return (
    <div className="relative">
      <div className="grid gap-1" style={{ gridTemplateColumns: `repeat(${size}, minmax(0,1fr))` }}>
        {Array.from({ length: size }).map((_, y) =>
          Array.from({ length: size }).map((_, x) => {
            const quad =
              y < size / 2 && x < size / 2
                ? "NW"
                : y < size / 2
                ? "NE"
                : x < size / 2
                ? "SW"
                : "SE";
            const owned = turn.farm.unlocked_quadrants.includes(quad);
            return (
              <div
                key={`${x}-${y}`}
                className="relative"
                style={{
                  outline: owned ? "none" : "1px solid rgba(0,0,0,0.4)",
                  background: owned ? "transparent" : "rgba(0,0,0,0.25)",
                  borderRadius: 4,
                }}
              >
                <Cell
                  turn={turn}
                  x={x}
                  y={y}
                  selected={selected?.x === x && selected?.y === y}
                  onHover={setHover}
                  onLeave={() => setHover(null)}
                  onClick={() => onSelect?.(x, y)}
                />
                {showQuadrantLabels && x === 0 && y === 0 && (
                  <span className="pointer-events-none absolute left-0.5 top-0.5 text-[9px] font-semibold text-white/30">NW</span>
                )}
                {showQuadrantLabels && x === size - 1 && y === 0 && (
                  <span className="pointer-events-none absolute right-0.5 top-0.5 text-[9px] font-semibold text-white/30">NE</span>
                )}
                {showQuadrantLabels && x === 0 && y === size - 1 && (
                  <span className="pointer-events-none absolute bottom-0.5 left-0.5 text-[9px] font-semibold text-white/30">SW</span>
                )}
                {showQuadrantLabels && x === size - 1 && y === size - 1 && (
                  <span className="pointer-events-none absolute bottom-0.5 right-0.5 text-[9px] font-semibold text-white/30">SE</span>
                )}
              </div>
            );
          })
        )}
      </div>

      {hover && (
        <div
          className="pointer-events-none fixed z-50 rounded-lg border border-border bg-forest/95 px-2.5 py-1.5 font-mono text-[11px] text-white/85 shadow-glow backdrop-blur"
          style={{
            left: Math.min(hover.px + 12, window.innerWidth - 200),
            top: Math.min(hover.py + 12, window.innerHeight - 60),
          }}
        >
          {hover.text}
        </div>
      )}
    </div>
  );
}

export const CROP_LIST = CROPS;
export const ANIMAL_LIST = ANIMALS;
