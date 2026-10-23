import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { C, FONT } from "../theme";

interface ChromeFrameProps {
  chapterNum: string;
  chapterTitle: string;
  activeLayerBadge: string;
  rightMetric?: string;
}

export const ChromeFrame: React.FC<ChromeFrameProps> = ({
  chapterNum,
  chapterTitle,
  activeLayerBadge,
  rightMetric = "PO-8841 · SIC-MOD-1200V · $5.42M NET SAVED",
}) => {
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill style={{ pointerEvents: "none", zIndex: 50 }}>
      {/* Ambient background grid + radial atmospheric spotlights */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          zIndex: -1,
          backgroundImage: `
            linear-gradient(to right, rgba(148, 163, 184, 0.045) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(148, 163, 184, 0.045) 1px, transparent 1px)
          `,
          backgroundSize: "56px 56px",
          maskImage:
            "radial-gradient(ellipse 85% 75% at 50% 50%, black 35%, transparent 100%)",
          WebkitMaskImage:
            "radial-gradient(ellipse 85% 75% at 50% 50%, black 35%, transparent 100%)",
        }}
      />

      {/* Top Bar (Hizz-style persistent brand mark + sponsor lockup) */}
      <div
        style={{
          position: "absolute",
          top: 34,
          left: 52,
          right: 52,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        {/* Left: Switchyard Brand Mark + Wordmark */}
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <div
            style={{
              width: 36,
              height: 36,
              borderRadius: 10,
              background:
                "linear-gradient(135deg, #38bdf8 0%, #6366f1 55%, #a3e635 100%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: "0 0 24px rgba(56, 189, 248, 0.45)",
              fontFamily: FONT.mono,
              fontWeight: 800,
              fontSize: 15,
              color: "#05070b",
              letterSpacing: -0.5,
            }}
          >
            SY
          </div>
          <span
            style={{
              fontFamily: FONT.display,
              fontWeight: 700,
              fontSize: 22,
              color: C.ink,
              letterSpacing: "-0.03em",
            }}
          >
            switchyard
          </span>
          <span
            style={{
              fontFamily: FONT.mono,
              fontSize: 11,
              fontWeight: 600,
              color: C.lime,
              padding: "4px 10px",
              borderRadius: 999,
              background: "rgba(163, 230, 53, 0.1)",
              border: "1px solid rgba(163, 230, 53, 0.32)",
              letterSpacing: "0.06em",
            }}
          >
            {activeLayerBadge}
          </span>
        </div>

        {/* Right: Sponsor Lockup + Nightshift Runtime Status */}
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <div
            style={{
              fontFamily: FONT.mono,
              fontSize: 11,
              color: C.inkDim,
              letterSpacing: "0.08em",
              padding: "6px 14px",
              borderRadius: 999,
              background: "rgba(15, 23, 42, 0.72)",
              border: "1px solid rgba(255, 255, 255, 0.1)",
            }}
          >
            01 ZETARIS SQL · 02 METERLESS ENGINES · 03 NVIDIA NEMOTRON
          </div>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              padding: "6px 13px",
              borderRadius: 999,
              background: "rgba(16, 185, 129, 0.12)",
              border: "1px solid rgba(16, 185, 129, 0.35)",
              fontFamily: FONT.mono,
              fontSize: 11,
              fontWeight: 600,
              color: "#6ee7b7",
            }}
          >
            <span
              style={{
                width: 7,
                height: 7,
                borderRadius: "50%",
                background: C.emerald,
                boxShadow: `0 0 ${8 + 4 * Math.sin(frame * 0.2)}px ${C.emerald}`,
              }}
            />
            NIGHTSHIFT :8088
          </div>
        </div>
      </div>

      {/* Bottom Bar (Hizz-style chapter indicator + live audio telemetry bars) */}
      <div
        style={{
          position: "absolute",
          bottom: 32,
          left: 52,
          right: 52,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        {/* Left: Numbered Chapter Indicator */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 12,
            padding: "7px 16px",
            borderRadius: 999,
            background: "rgba(9, 13, 22, 0.82)",
            border: "1px solid rgba(255, 255, 255, 0.12)",
          }}
        >
          <span
            style={{
              fontFamily: FONT.mono,
              fontSize: 12,
              fontWeight: 700,
              color: C.cyan,
            }}
          >
            {chapterNum}
          </span>
          <span style={{ color: "rgba(255,255,255,0.22)" }}>//</span>
          <span
            style={{
              fontFamily: FONT.mono,
              fontSize: 12,
              fontWeight: 600,
              color: C.ink,
              letterSpacing: "0.08em",
            }}
          >
            {chapterTitle}
          </span>
        </div>

        {/* Right: Audio Waveform Equalizer + Live Metric */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 14,
            padding: "7px 16px",
            borderRadius: 999,
            background: "rgba(9, 13, 22, 0.82)",
            border: "1px solid rgba(255, 255, 255, 0.12)",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 3,
              height: 14,
            }}
          >
            {[0, 1, 2, 3, 4, 5].map((b) => {
              const h = interpolate(
                Math.sin(frame * 0.28 + b * 1.1),
                [-1, 1],
                [4, 14]
              );
              return (
                <div
                  key={b}
                  style={{
                    width: 2.5,
                    height: h,
                    borderRadius: 2,
                    background: b % 2 === 0 ? C.lime : C.cyan,
                  }}
                />
              );
            })}
          </div>
          <span
            style={{
              fontFamily: FONT.mono,
              fontSize: 11.5,
              color: C.inkDim,
              letterSpacing: "0.05em",
            }}
          >
            {rightMetric}
          </span>
        </div>
      </div>
    </AbsoluteFill>
  );
};
