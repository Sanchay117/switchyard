import React from "react";

export const C = {
  bg0: "#05070b",
  bg1: "#090d16",
  bg2: "#0f172a",
  surface: "rgba(15, 23, 42, 0.72)",
  surfaceStrong: "rgba(11, 15, 25, 0.88)",
  glassBorder: "rgba(255, 255, 255, 0.14)",
  glassHighlight: "rgba(255, 255, 255, 0.28)",
  ink: "#f8fafc",
  inkDim: "#94a3b8",
  inkMute: "#64748b",
  lime: "#a3e635",
  emerald: "#10b981",
  cyan: "#38bdf8",
  indigo: "#818cf8",
  amber: "#f59e0b",
  red: "#f43f5e",
  nvidia: "#76b900",
};

export const FONT = {
  display:
    '"Inter", -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", sans-serif',
  sans: '"Inter", -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", sans-serif',
  mono: '"SF Mono", "JetBrains Mono", "Menlo", monospace',
};

export const glassCardStyle = (
  accentColor = "rgba(255,255,255,0.14)",
  bgAlpha = 0.76
): React.CSSProperties => ({
  background: `linear-gradient(155deg, rgba(19, 28, 46, ${bgAlpha}) 0%, rgba(9, 13, 22, ${
    bgAlpha + 0.12
  }) 100%)`,
  border: `1px solid ${accentColor}`,
  boxShadow:
    "0 28px 70px rgba(0, 0, 0, 0.65), inset 0 1px 0 rgba(255, 255, 255, 0.22)",
  backdropFilter: "blur(22px)",
  WebkitBackdropFilter: "blur(22px)",
});
