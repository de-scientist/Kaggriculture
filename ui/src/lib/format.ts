export function fmt(n: number, opts: Intl.NumberFormatOptions = {}): string {
  return new Intl.NumberFormat("en-US", opts).format(Math.round(n));
}

export function coins(n: number): string {
  return fmt(n);
}

export function pct(n: number, digits = 1): string {
  return `${n >= 0 ? "+" : ""}${n.toFixed(digits)}%`;
}

export function signed(n: number): string {
  return `${n >= 0 ? "+" : "-"}${fmt(Math.abs(n))}`;
}

export function clamp(n: number, lo: number, hi: number): number {
  return Math.max(lo, Math.min(hi, n));
}

export function shortId(id: string): string {
  return id.length > 22 ? id.slice(0, 10) + "…" + id.slice(-6) : id;
}

export function timeOfDay(hour: number, turnsPerDay = 24): string {
  const h = Math.floor((hour / turnsPerDay) * 24);
  const m = Math.floor(((hour / turnsPerDay) * 24 - h) * 60);
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}`;
}

export function cropEmoji(crop: string): string {
  switch (crop) {
    case "WHEAT":
      return "🌾";
    case "CARROT":
      return "🥕";
    case "TOMATO":
      return "🍅";
    case "STRAWBERRY":
      return "🍓";
    case "MELON":
      return "🍈";
    case "EGG":
      return "🥚";
    case "MILK":
      return "🥛";
    case "WOOL":
      return "🧶";
    default:
      return "🌱";
  }
}

export function cropColor(crop: string): string {
  switch (crop) {
    case "WHEAT":
      return "#E3B341";
    case "CARROT":
      return "#F5A623";
    case "TOMATO":
      return "#EF4444";
    case "STRAWBERRY":
      return "#FF5C8A";
    case "MELON":
      return "#22C55E";
    case "EGG":
      return "#F0E6D2";
    case "MILK":
      return "#E8F0F5";
    case "WOOL":
      return "#C9A26B";
    default:
      return "#2E7D32";
  }
}

export function quadrantOf(x: number, y: number, size = 10): string {
  const half = size / 2;
  if (y < half && x < half) return "NW";
  if (y < half && x >= half) return "NE";
  if (y >= half && x < half) return "SW";
  return "SE";
}
