import React from "react";
import {
  LayoutDashboard,
  Sprout,
  BrainCircuit,
  LineChart,
  PlayCircle,
  BarChart3,
  Trophy,
  History,
  FlaskConical,
  ScrollText,
  Settings,
  PanelLeftClose,
  PanelLeft,
} from "lucide-react";
import { useStore } from "../../lib/store";
import { PageId } from "../../types";

export const NAV: { id: PageId; label: string; icon: React.ComponentType<{ size?: number }> }[] = [
  { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
  { id: "farm", label: "Farm", icon: Sprout },
  { id: "aibrain", label: "AI Brain", icon: BrainCircuit },
  { id: "market", label: "Market", icon: LineChart },
  { id: "simulation", label: "Simulation", icon: PlayCircle },
  { id: "analytics", label: "Analytics", icon: BarChart3 },
  { id: "championship", label: "Championship", icon: Trophy },
  { id: "replays", label: "Replays", icon: History },
  { id: "experiments", label: "Experiments", icon: FlaskConical },
  { id: "logs", label: "Logs", icon: ScrollText },
  { id: "settings", label: "Settings", icon: Settings },
];

export function Sidebar({
  page,
  onNavigate,
}: {
  page: PageId;
  onNavigate: (p: PageId) => void;
}) {
  const { sidebarCollapsed, toggleSidebar } = useStore();
  return (
    <aside
      className={`flex shrink-0 flex-col border-r border-border bg-forest/60 backdrop-blur transition-all duration-200 ${
        sidebarCollapsed ? "w-[68px]" : "w-60"
      }`}
    >
      <div className="flex items-center gap-2.5 px-4 py-4">
        <div className="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-cyan/15 text-cyan">
          <Sprout size={20} />
        </div>
        {!sidebarCollapsed && (
          <div className="leading-tight">
            <div className="text-sm font-bold text-white">Kaggriculture</div>
            <div className="text-[10px] tracking-[0.18em] text-white/40">COMMAND CENTER</div>
          </div>
        )}
      </div>

      <nav className="flex-1 space-y-1 px-3 py-2">
        {NAV.map((item) => {
          const Icon = item.icon;
          const active = page === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              title={item.label}
              className={`nav-link w-full ${active ? "nav-link-active" : ""} ${
                sidebarCollapsed ? "justify-center px-0" : ""
              }`}
            >
              <Icon size={18} />
              {!sidebarCollapsed && <span>{item.label}</span>}
            </button>
          );
        })}
      </nav>

      <button
        onClick={toggleSidebar}
        className="m-3 flex items-center justify-center gap-2 rounded-xl border border-border px-3 py-2 text-xs text-white/45 hover:text-white"
      >
        {sidebarCollapsed ? <PanelLeft size={16} /> : <PanelLeftClose size={16} />}
        {!sidebarCollapsed && <span>Collapse</span>}
      </button>
    </aside>
  );
}
