import {
  GameDataset,
  GameRecord,
  Turn,
  Decision,
  AIState,
} from "../types";

export type SimMode = "autonomous" | "assisted" | "manual";

export interface Store {
  dataset: GameDataset | null;
  loading: boolean;
  error: string | null;
  game: GameRecord | null;
  gameId: string | null;
  cursor: number;
  playing: boolean;
  speed: number;
  mode: SimMode;
  chatOpen: boolean;
  developer: boolean;
  sidebarCollapsed: boolean;
  setGame: (id: string) => void;
  setCursor: (i: number) => void;
  play: () => void;
  pause: () => void;
  togglePlay: () => void;
  step: (dir?: 1 | -1) => void;
  setSpeed: (s: number) => void;
  setMode: (m: SimMode) => void;
  setChatOpen: (b: boolean) => void;
  setDeveloper: (b: boolean) => void;
  toggleSidebar: () => void;
  reload: () => void;
}

import { createContext, useContext, useEffect, useMemo, useReducer, useRef } from "react";
import type { ReactNode } from "react";

const Ctx = createContext<Store | null>(null);

export function useStore(): Store {
  const s = useContext(Ctx);
  if (!s) throw new Error("useStore must be used within StoreProvider");
  return s;
}

type Action =
  | { t: "loaded"; dataset: GameDataset }
  | { t: "error"; error: string }
  | { t: "game"; id: string }
  | { t: "cursor"; i: number }
  | { t: "play" }
  | { t: "pause" }
  | { t: "speed"; s: number }
  | { t: "mode"; m: SimMode }
  | { t: "chat"; b: boolean }
  | { t: "dev"; b: boolean }
  | { t: "sidebar" };

interface S {
  dataset: GameDataset | null;
  loading: boolean;
  error: string | null;
  gameId: string | null;
  cursor: number;
  playing: boolean;
  speed: number;
  mode: SimMode;
  chatOpen: boolean;
  developer: boolean;
  sidebarCollapsed: boolean;
}

const BASE_TICK = 110;

export function StoreProvider({ children }: { children: ReactNode }) {
  const [s, dispatch] = useReducer(reducer, {
    dataset: null,
    loading: true,
    error: null,
    gameId: null,
    cursor: 0,
    playing: false,
    speed: 5,
    mode: "autonomous",
    chatOpen: false,
    developer: false,
    sidebarCollapsed: false,
  });

  const timer = useRef<ReturnType<typeof setInterval> | null>(null);

  async function load() {
    try {
      let dataset: GameDataset | null = null;
      try {
        const res = await fetch("/data/played.json", { cache: "no-store" });
        if (res.ok) {
          const d = (await res.json()) as GameDataset;
          if (d.games?.length) dataset = d;
        }
      } catch {
        /* fall through to demo dataset */
      }
      if (!dataset) {
        const res = await fetch("/data/games.json", { cache: "no-store" });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        dataset = (await res.json()) as GameDataset;
      }
      const firstId = dataset.games[0]?.id ?? null;
      dispatch({ t: "loaded", dataset });
      if (firstId) dispatch({ t: "game", id: firstId });
    } catch (e) {
      dispatch({ t: "error", error: (e as Error).message });
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const game = useMemo<TurnSafeGame | null>(() => {
    if (!s.dataset || !s.gameId) return null;
    return s.dataset.games.find((g) => g.id === s.gameId) ?? null;
  }, [s.dataset, s.gameId]);

  // Playback timer
  useEffect(() => {
    if (timer.current) {
      clearInterval(timer.current);
      timer.current = null;
    }
    if (!s.playing || !game) return;
    const interval = Math.max(8, BASE_TICK / s.speed);
    timer.current = setInterval(() => {
      dispatch({ t: "cursor", i: -1 }); // sentinel: advance handled in reducer
    }, interval);
    return () => {
      if (timer.current) clearInterval(timer.current);
    };
  }, [s.playing, s.speed, game, s.cursor]);

  const store: Store = {
    dataset: s.dataset,
    loading: s.loading,
    error: s.error,
    game,
    gameId: s.gameId,
    cursor: s.cursor,
    playing: s.playing,
    speed: s.speed,
    mode: s.mode,
    chatOpen: s.chatOpen,
    developer: s.developer,
    sidebarCollapsed: s.sidebarCollapsed,
    setGame: (id) => {
      dispatch({ t: "game", id });
    },
    setCursor: (i) => dispatch({ t: "cursor", i }),
    play: () => dispatch({ t: "play" }),
    pause: () => dispatch({ t: "pause" }),
    togglePlay: () => dispatch({ t: "play" }),
    step: (dir = 1) => dispatch({ t: "cursor", i: dir }),
    setSpeed: (sp) => dispatch({ t: "speed", s: sp }),
    setMode: (m) => dispatch({ t: "mode", m }),
    setChatOpen: (b) => dispatch({ t: "chat", b }),
    setDeveloper: (b) => dispatch({ t: "dev", b }),
    toggleSidebar: () => dispatch({ t: "sidebar" }),
    reload: () => {
      dispatch({ t: "error", error: "" });
      load();
    },
  };

  return <Ctx.Provider value={store}>{children}</Ctx.Provider>;
}

type TurnSafeGame = GameRecord;

function reducer(s: S, a: Action): S {
  switch (a.t) {
    case "loaded":
      return { ...s, dataset: a.dataset, loading: false, error: null };
    case "error":
      return { ...s, loading: false, error: a.error };
    case "game":
      return {
        ...s,
        gameId: a.id,
        cursor: 0,
        playing: false,
        dataset: s.dataset,
        loading: s.loading,
        error: s.error,
        speed: s.speed,
        mode: s.mode,
        chatOpen: s.chatOpen,
        developer: s.developer,
        sidebarCollapsed: s.sidebarCollapsed,
      };
    case "cursor": {
      const max = s.dataset?.games.find((x) => x.id === s.gameId)?.turns.length ?? 1;
      let i: number;
      if (a.i === -1) {
        i = s.cursor + 1;
      } else {
        i = a.i;
      }
      if (i >= max) {
        return { ...s, cursor: max - 1, playing: false };
      }
      if (i < 0) i = 0;
      return { ...s, cursor: i };
    }
    case "play":
      return { ...s, playing: true };
    case "pause":
      return { ...s, playing: false };
    case "speed":
      return { ...s, speed: a.s };
    case "mode":
      return { ...s, mode: a.m };
    case "chat":
      return { ...s, chatOpen: a.b };
    case "dev":
      return { ...s, developer: a.b };
    case "sidebar":
      return { ...s, sidebarCollapsed: !s.sidebarCollapsed };
    default:
      return s;
  }
}

export function aiStateFromTurn(t: Turn | null): { state: AIState; label: string } {
  if (!t) return { state: "WAITING", label: "Idle" };
  const d = t.decision;
  if (d.type === "trade") return { state: "TRADING", label: "Trading" };
  if (d.type === "expand") return { state: "EXPANDING", label: "Expanding" };
  if (d.type === "farm") {
    const lower = d.summary.toLowerCase();
    if (lower.includes("harvest")) return { state: "HARVESTING", label: "Harvesting" };
    if (lower.includes("water") || lower.includes("plant"))
      return { state: "EXECUTING", label: "Executing" };
  }
  if (t.day >= 26) return { state: "ENDGAME", label: "Endgame" };
  if (d.confidence.value < 0.5) return { state: "WARNING", label: "Uncertain" };
  return { state: "THINKING", label: "Optimizing" };
}
