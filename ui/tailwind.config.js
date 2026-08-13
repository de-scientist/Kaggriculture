/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#06110D",
        forest: "#0B1F17",
        "forest-2": "#0E2A1E",
        ag: "#2E7D32",
        cyan: "#00D4FF",
        amber: "#F5A623",
        danger: "#EF4444",
        emerald: "#22C55E",
        surface: "rgba(255,255,255,0.05)",
        "surface-2": "rgba(255,255,255,0.08)",
        border: "rgba(255,255,255,0.08)",
      },
      fontFamily: {
        sans: ["Inter", "Manrope", "system-ui", "sans-serif"],
        mono: ["'JetBrains Mono'", "ui-monospace", "SFMono-Regular", "monospace"],
      },
      borderRadius: {
        xl: "1rem",
        "2xl": "1.25rem",
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(0,212,255,0.15), 0 8px 30px rgba(0,0,0,0.45)",
        card: "0 8px 24px rgba(0,0,0,0.35)",
      },
      keyframes: {
        pulseSoft: {
          "0%,100%": { opacity: "1" },
          "50%": { opacity: "0.45" },
        },
        slideUp: {
          from: { opacity: "0", transform: "translateY(8px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        fadeIn: {
          from: { opacity: "0" },
          to: { opacity: "1" },
        },
      },
      animation: {
        pulseSoft: "pulseSoft 2s ease-in-out infinite",
        slideUp: "slideUp 0.3s ease-out",
        fadeIn: "fadeIn 0.4s ease-out",
      },
    },
  },
  plugins: [],
};
