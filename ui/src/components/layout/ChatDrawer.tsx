import React, { useEffect, useRef, useState } from "react";
import { X, Send, Sparkles, Bot } from "lucide-react";
import { useStore } from "../../lib/store";
import { respond, ChatResponse } from "../../lib/aiChat";
import { fmt } from "../../lib/format";

interface Msg {
  role: "user" | "ai";
  text: string;
  structured?: { label: string; value: string }[];
  confidence?: number;
}

const QUICK = [
  "Analyze Farm",
  "Explain Last Decision",
  "Analyze Market",
  "Find Weakness",
  "Compare Opponent",
  "Explain Strategy",
];

export function ChatDrawer() {
  const { chatOpen, setChatOpen, game, cursor } = useStore();
  const [input, setInput] = useState("");
  const [msgs, setMsgs] = useState<Msg[]>([
    {
      role: "ai",
      text: "I'm the Farm AI assistant. Ask me about the current farm, market, or decisions using the loaded replay data.",
      confidence: 1,
    },
  ]);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight });
  }, [msgs, chatOpen]);

  function send(text: string) {
    const q = text.trim();
    if (!q) return;
    setMsgs((m) => [...m, { role: "user", text: q }]);
    setInput("");
    const r: ChatResponse = respond(q, game, cursor);
    setTimeout(() => {
      setMsgs((m) => [
        ...m,
        {
          role: "ai",
          text: r.answer,
          structured: r.structured,
          confidence: r.confidence,
        },
      ]);
    }, 220);
  }

  if (!chatOpen) return null;

  return (
    <div className="fixed inset-0 z-40 flex justify-end" onClick={() => setChatOpen(false)}>
      <div className="absolute inset-0 bg-black/40" />
      <aside
        className="relative flex h-full w-full max-w-md flex-col border-l border-border bg-forest/95 backdrop-blur-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <header className="flex items-center justify-between border-b border-border px-4 py-3">
          <div className="flex items-center gap-2">
            <span className="grid h-7 w-7 place-items-center rounded-lg bg-cyan/15 text-cyan">
              <Bot size={16} />
            </span>
            <div>
              <div className="text-sm font-semibold text-white">FARM AI</div>
              <div className="text-[10px] text-white/40">Grounded in replay data</div>
            </div>
          </div>
          <button onClick={() => setChatOpen(false)} className="text-white/50 hover:text-white">
            <X size={18} />
          </button>
        </header>

        <div ref={scrollRef} className="flex-1 space-y-3 overflow-y-auto p-4">
          {msgs.map((m, i) => (
            <div key={i} className={m.role === "user" ? "flex justify-end" : "flex justify-start"}>
              <div
                className={`max-w-[90%] rounded-2xl px-3.5 py-2.5 text-sm ${
                  m.role === "user"
                    ? "bg-cyan/20 text-white"
                    : "border border-border bg-surface text-white/85"
                }`}
              >
                <p className="whitespace-pre-line">{m.text}</p>
                {m.structured && (
                  <div className="mt-2 grid grid-cols-2 gap-1.5">
                    {m.structured.map((s, j) => (
                      <div key={j} className="rounded-lg bg-white/5 px-2 py-1">
                        <div className="text-[10px] uppercase tracking-wide text-white/40">{s.label}</div>
                        <div className="font-mono text-xs text-white/90">{s.value}</div>
                      </div>
                    ))}
                  </div>
                )}
                {m.confidence !== undefined && m.role === "ai" && (
                  <div className="mt-2 flex items-center gap-1.5 text-[10px] text-white/40">
                    <Sparkles size={11} className="text-cyan" /> confidence {Math.round(m.confidence * 100)}%
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        <div className="border-t border-border p-3">
          <div className="mb-2 flex flex-wrap gap-1.5">
            {QUICK.map((q) => (
              <button
                key={q}
                onClick={() => send(q)}
                className="rounded-full border border-border bg-surface px-2.5 py-1 text-[11px] text-white/60 hover:text-white"
              >
                {q}
              </button>
            ))}
          </div>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              send(input);
            }}
            className="flex items-center gap-2 rounded-xl border border-border bg-surface px-3 py-2"
          >
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask anything about your farm…"
              className="flex-1 bg-transparent text-sm text-white placeholder:text-white/30 focus:outline-none"
            />
            <button type="submit" className="text-cyan">
              <Send size={16} />
            </button>
          </form>
        </div>
      </aside>
    </div>
  );
}
