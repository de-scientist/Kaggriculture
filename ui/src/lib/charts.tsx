import React, { useMemo, useState } from "react";

export function Sparkline({
  data,
  color = "#00D4FF",
  width = 120,
  height = 32,
  fill = true,
}: {
  data: number[];
  color?: string;
  width?: number;
  height?: number;
  fill?: boolean;
}) {
  const { line, area } = useMemo(() => {
    if (data.length < 2) return { line: "", area: "" };
    const min = Math.min(...data);
    const max = Math.max(...data);
    const span = max - min || 1;
    const stepX = width / (data.length - 1);
    const pts = data.map((v, i) => {
      const x = i * stepX;
      const y = height - ((v - min) / span) * (height - 4) - 2;
      return [x, y] as const;
    });
    const line = pts.map((p, i) => `${i === 0 ? "M" : "L"}${p[0].toFixed(1)},${p[1].toFixed(1)}`).join(" ");
    const area = `${line} L${width},${height} L0,${height} Z`;
    return { line, area };
  }, [data, width, height]);

  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} className="overflow-visible">
      {fill && area && <path d={area} fill={color} opacity={0.12} />}
      {line && <path d={line} fill="none" stroke={color} strokeWidth={1.5} strokeLinejoin="round" />}
    </svg>
  );
}

export interface Series {
  name: string;
  color: string;
  data: number[];
}

export function LineChart({
  series,
  height = 240,
  xLabels,
  formatY = (v) => `${Math.round(v)}`,
  formatTooltip,
}: {
  series: Series[];
  height?: number;
  xLabels?: string[];
  formatY?: (v: number) => string;
  formatTooltip?: (i: number) => React.ReactNode;
}) {
  const width = 720;
  const padL = 52;
  const padR = 12;
  const padT = 12;
  const padB = 24;
  const [hover, setHover] = useState<number | null>(null);

  const { paths, min, max } = useMemo(() => {
    let min = Infinity;
    let max = -Infinity;
    for (const s of series)
      for (const v of s.data) {
        if (v < min) min = v;
        if (v > max) max = v;
      }
    if (!isFinite(min)) {
      min = 0;
      max = 1;
    }
    const span = max - min || 1;
    const plotW = width - padL - padR;
    const plotH = height - padT - padB;
    const n = Math.max(...series.map((s) => s.data.length), 2);
    const stepX = plotW / (n - 1);
    const paths = series.map((s) => {
      const pts = s.data.map((v, i) => {
        const x = padL + i * stepX;
        const y = padT + plotH - ((v - min) / span) * plotH;
        return `${i === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
      });
      return { name: s.name, color: s.color, d: pts.join(" ") };
    });
    return { paths, min, max };
  }, [series, height]);

  const plotW = width - padL - padR;
  const plotH = height - padT - padB;
  const n = Math.max(...series.map((s) => s.data.length), 2);
  const stepX = plotW / (n - 1);

  const gridLines = 4;
  const yticks = Array.from({ length: gridLines + 1 }, (_, i) => {
    const v = min + ((max - min) * i) / gridLines;
    const y = padT + plotH - (i / gridLines) * plotH;
    return { v, y };
  });

  function onMove(e: React.MouseEvent<SVGSVGElement>) {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * width;
    const idx = Math.round(((x - padL) / stepX));
    if (idx >= 0 && idx < n) setHover(idx);
    else setHover(null);
  }

  return (
    <div className="relative w-full">
      <svg
        viewBox={`0 0 ${width} ${height}`}
        className="w-full"
        style={{ height }}
        onMouseMove={onMove}
        onMouseLeave={() => setHover(null)}
        preserveAspectRatio="none"
      >
        {yticks.map((t, i) => (
          <g key={i}>
            <line x1={padL} y1={t.y} x2={width - padR} y2={t.y} stroke="rgba(255,255,255,0.06)" />
            <text x={padL - 8} y={t.y + 3} textAnchor="end" className="fill-white/35" fontSize={10} fontFamily="JetBrains Mono">
              {formatY(t.v)}
            </text>
          </g>
        ))}
        {paths.map((p) => (
          <path key={p.name} d={p.d} fill="none" stroke={p.color} strokeWidth={2} strokeLinejoin="round" />
        ))}
        {hover !== null && (
          <line
            x1={padL + hover * stepX}
            y1={padT}
            x2={padL + hover * stepX}
            y2={padT + plotH}
            stroke="rgba(255,255,255,0.25)"
          />
        )}
      </svg>
      {hover !== null && (
        <div className="pointer-events-none absolute left-2 top-2 rounded-lg border border-border bg-forest/90 px-3 py-2 text-xs backdrop-blur">
          {xLabels?.[hover] && <div className="mb-1 font-mono text-white/50">{xLabels[hover]}</div>}
          {series.map((s) => (
            <div key={s.name} className="flex items-center gap-2">
              <span className="inline-block h-2 w-2 rounded-full" style={{ background: s.color }} />
              <span className="text-white/70">{s.name}</span>
              <span className="ml-auto font-mono text-white">{formatY(s.data[hover] ?? 0)}</span>
            </div>
          ))}
          {formatTooltip?.(hover)}
        </div>
      )}
      <div className="mt-1 flex flex-wrap gap-3 px-2">
        {series.map((s) => (
          <div key={s.name} className="flex items-center gap-1.5 text-[11px] text-white/55">
            <span className="inline-block h-2 w-2 rounded-full" style={{ background: s.color }} />
            {s.name}
          </div>
        ))}
      </div>
    </div>
  );
}

export function Bars({
  data,
  height = 160,
  color = "#2E7D32",
  formatY = (v) => `${Math.round(v)}`,
}: {
  data: { label: string; value: number; color?: string }[];
  height?: number;
  color?: string;
  formatY?: (v: number) => string;
}) {
  const max = Math.max(...data.map((d) => d.value), 1);
  return (
    <div className="flex items-end gap-2" style={{ height }}>
      {data.map((d, i) => (
        <div key={i} className="flex flex-1 flex-col items-center gap-1">
          <div className="flex w-full flex-1 items-end">
            <div
              className="w-full rounded-t-md"
              style={{
                height: `${(d.value / max) * 100}%`,
                background: d.color ?? color,
                minHeight: 2,
              }}
              title={`${d.label}: ${formatY(d.value)}`}
            />
          </div>
          <span className="text-[10px] text-white/45">{d.label}</span>
        </div>
      ))}
    </div>
  );
}

export function ProgressBar({
  value,
  color = "#00D4FF",
  bg = "rgba(255,255,255,0.08)",
}: {
  value: number;
  color?: string;
  bg?: string;
}) {
  return (
    <div className="h-1.5 w-full overflow-hidden rounded-full" style={{ background: bg }}>
      <div className="h-full rounded-full" style={{ width: `${Math.max(0, Math.min(100, value))}%`, background: color }} />
    </div>
  );
}
