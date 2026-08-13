import React, { useState } from "react";
import { useStore } from "./lib/store";
import { Sidebar } from "./components/layout/Sidebar";
import { Header } from "./components/layout/Header";
import { ChatDrawer } from "./components/layout/ChatDrawer";
import { EmptyState, Skeleton } from "./components/common";
import { AlertTriangle, ServerCrash, Sprout } from "lucide-react";

import { Dashboard } from "./pages/Dashboard";
import { Farm } from "./pages/Farm";
import { AIBrain } from "./pages/AIBrain";
import { Market } from "./pages/Market";
import { Simulation } from "./pages/Simulation";
import { Analytics } from "./pages/Analytics";
import { Championship } from "./pages/Championship";
import { Replays } from "./pages/Replays";
import { Experiments } from "./pages/Experiments";
import { Logs } from "./pages/Logs";
import { Settings } from "./pages/Settings";
import { PageId } from "./types";

export default function App() {
  const { loading, error, dataset, reload } = useStore();
  const [page, setPage] = useState<PageId>("dashboard");

  return (
    <div className="flex h-screen w-screen overflow-hidden text-white/90">
      <Sidebar page={page} onNavigate={setPage} />
      <div className="flex min-w-0 flex-1 flex-col">
        <Header />
        <main className="flex-1 overflow-y-auto p-5">
          {loading && <LoadingState />}
          {error && (
            <EmptyState
              icon={<ServerCrash size={40} />}
              title="Simulation data unavailable"
              desc={`Could not load replay data: ${error}. The autonomous agent still runs independently — this is only the visualization layer.`}
              action={
                <button className="btn btn-primary" onClick={reload}>
                  Retry
                </button>
              }
            />
          )}
          {!loading && !error && dataset && (
            <PageSwitch page={page} />
          )}
        </main>
      </div>
      <ChatDrawer />
    </div>
  );
}

function PageSwitch({ page }: { page: PageId }) {
  switch (page) {
    case "dashboard":
      return <Dashboard />;
    case "farm":
      return <Farm />;
    case "aibrain":
      return <AIBrain />;
    case "market":
      return <Market />;
    case "simulation":
      return <Simulation />;
    case "analytics":
      return <Analytics />;
    case "championship":
      return <Championship />;
    case "replays":
      return <Replays />;
    case "experiments":
      return <Experiments />;
    case "logs":
      return <Logs />;
    case "settings":
      return <Settings />;
    default:
      return <Dashboard />;
  }
}

function LoadingState() {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        {Array.from({ length: 8 }).map((_, i) => (
          <Skeleton key={i} className="h-24" />
        ))}
      </div>
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Skeleton className="h-72 lg:col-span-2" />
        <Skeleton className="h-72" />
      </div>
      <EmptyState
        icon={<Sprout size={32} />}
        title="Loading command center"
        desc="Fetching recorded replay data and championship telemetry…"
      />
    </div>
  );
}
