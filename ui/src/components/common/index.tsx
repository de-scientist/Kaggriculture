import React from "react";

export function Card({
  title,
  subtitle,
  action,
  className = "",
  bodyClass = "",
  children,
}: {
  title?: React.ReactNode;
  subtitle?: React.ReactNode;
  action?: React.ReactNode;
  className?: string;
  bodyClass?: string;
  children?: React.ReactNode;
}) {
  return (
    <section className={`glass p-4 ${className}`}>
      {(title || action) && (
        <header className="mb-3 flex items-start justify-between gap-3">
          <div>
            {title && <h3 className="text-sm font-semibold text-white/90">{title}</h3>}
            {subtitle && <p className="mt-0.5 text-xs text-white/45">{subtitle}</p>}
          </div>
          {action}
        </header>
      )}
      <div className={bodyClass}>{children}</div>
    </section>
  );
}

export function KpiCard({
  label,
  value,
  delta,
  deltaPositive,
  spark,
  icon,
  accent = "#00D4FF",
}: {
  label: string;
  value: React.ReactNode;
  delta?: string;
  deltaPositive?: boolean;
  spark?: React.ReactNode;
  icon?: React.ReactNode;
  accent?: string;
}) {
  return (
    <div className="glass flex flex-col gap-2 p-4">
      <div className="flex items-center justify-between">
        <span className="card-title">{label}</span>
        {icon && <span style={{ color: accent }}>{icon}</span>}
      </div>
      <div className="metric text-2xl text-white">{value}</div>
      <div className="flex items-end justify-between gap-2">
        {delta ? (
          <span
            className="text-xs font-medium"
            style={{ color: deltaPositive ? "#22C55E" : "#EF4444" }}
          >
            {delta}
          </span>
        ) : (
          <span />
        )}
        {spark && <div className="opacity-80">{spark}</div>}
      </div>
    </div>
  );
}

const STATE_COLORS: Record<string, string> = {
  THINKING: "#00D4FF",
  EXECUTING: "#2E7D32",
  WAITING: "#94a3b8",
  HARVESTING: "#F5A623",
  TRADING: "#22C55E",
  EXPANDING: "#a855f7",
  OPTIMIZING: "#00D4FF",
  ENDGAME: "#F5A623",
  WARNING: "#F5A623",
  ERROR: "#EF4444",
};

export function StatusPill({ state, label }: { state: string; label: string }) {
  const color = STATE_COLORS[state] ?? "#00D4FF";
  return (
    <span
      className="chip border"
      style={{
        color,
        borderColor: `${color}40`,
        background: `${color}14`,
      }}
    >
      <span
        className="inline-block h-1.5 w-1.5 rounded-full"
        style={{ background: color, animation: "pulseSoft 1.8s ease-in-out infinite" }}
      />
      {label}
    </span>
  );
}

export function Badge({
  children,
  color = "#00D4FF",
  solid = false,
  className = "",
}: {
  children: React.ReactNode;
  color?: string;
  solid?: boolean;
  className?: string;
}) {
  return (
    <span
      className={`chip border ${className}`}
      style={{
        color: solid ? "#06110D" : color,
        borderColor: `${color}40`,
        background: solid ? color : `${color}14`,
      }}
    >
      {children}
    </span>
  );
}

export function EmptyState({
  icon,
  title,
  desc,
  action,
}: {
  icon?: React.ReactNode;
  title: string;
  desc?: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-border p-10 text-center">
      {icon && <div className="text-white/25">{icon}</div>}
      <div className="text-sm font-medium text-white/70">{title}</div>
      {desc && <p className="max-w-sm text-xs text-white/40">{desc}</p>}
      {action}
    </div>
  );
}

export function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse rounded-lg bg-white/5 ${className}`} />;
}

export function Tabs<T extends string>({
  tabs,
  active,
  onChange,
}: {
  tabs: { id: T; label: string }[];
  active: T;
  onChange: (id: T) => void;
}) {
  return (
    <div className="flex gap-1 rounded-xl border border-border bg-surface p-1">
      {tabs.map((t) => (
        <button
          key={t.id}
          onClick={() => onChange(t.id)}
          className={`flex-1 rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${
            active === t.id ? "bg-white/10 text-white" : "text-white/50 hover:text-white/80"
          }`}
        >
          {t.label}
        </button>
      ))}
    </div>
  );
}
