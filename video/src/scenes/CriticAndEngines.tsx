import React from "react";
import {
  AbsoluteFill,
  Audio,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { C, FONT, glassCardStyle } from "../theme";
import { ChromeFrame } from "../components/ChromeFrame";
import { GlassBrowser3D } from "../components/GlassBrowser3D";

const AGENT_STEPS = [
  { step: "01", name: "Planner & Mapper", lane: "Nemotron 30B", color: C.cyan },
  { step: "02", name: "Reconciler (Round 1)", lane: "3 SQL Queries", color: C.indigo },
  {
    step: "03",
    name: "Conflict Critic",
    lane: "REJECTS ROUND 1",
    color: C.red,
  },
  {
    step: "04",
    name: "Reconciler (Round 2)",
    lane: "+2 Targeted SQL",
    color: C.amber,
  },
  {
    step: "05",
    name: "Risk Escalator",
    lane: "Critic Approves",
    color: C.emerald,
  },
  {
    step: "06",
    name: "Sourced Reporter",
    lane: "H-MEM Commit",
    color: C.lime,
  },
];

const METERLESS_ENGINES = [
  {
    num: "ENGINE 01",
    name: "Scout Intent Engine",
    metric: "CRITICAL · 95 / 100 Blast Radius",
    detail:
      "Classifies disruption intent, maps 5 Zetaris tables, and assigns Fast (30B) vs Deep (120B) Nemotron lanes.",
    color: C.amber,
    delay: 25,
  },
  {
    num: "ENGINE 02",
    name: "World Model Engine",
    metric: "Version v15 · Optimistic Concurrency Lock",
    detail:
      "Tracks 6 sourced facts & 3 cross-system conflicts (CONF-01, CONF-02, CONF-03) with zero state clobbering.",
    color: C.cyan,
    delay: 95,
  },
  {
    num: "ENGINE 03",
    name: "Markovian Thinking Engine",
    metric: "84.0% Token Reduction (6,396t Saved)",
    detail:
      "Replaces O(n²) chat history with bounded <= 420-token Carry-Over State capsules (1,216t vs 7,612t naive).",
    color: C.lime,
    delay: 165,
  },
  {
    num: "ENGINE 04",
    name: "H-MEM (Hierarchical Memory)",
    metric: "3-Tier Cross-Session Precedent Store",
    detail:
      "Recalls Q3 Apex Wafer void precedent before planning; commits HMEM-PREC-004 after Critic verification.",
    color: C.emerald,
    delay: 235,
  },
];

export const CriticAndEngines: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const activeStepIdx = Math.min(
    5,
    Math.floor((frame / (durationInFrames * 0.85)) * 6)
  );
  const showEnginesScreen = frame > durationInFrames * 0.46;

  const tiltY = interpolate(
    frame,
    [0, durationInFrames * 0.5, durationInFrames],
    [-11, 7, 4]
  );

  return (
    <AbsoluteFill
      style={{
        background: `
          radial-gradient(ellipse 70% 55% at 25% 35%, rgba(245, 158, 11, 0.12) 0%, transparent 65%),
          radial-gradient(ellipse 65% 55% at 78% 65%, rgba(16, 185, 129, 0.12) 0%, transparent 65%),
          linear-gradient(180deg, ${C.bg0} 0%, ${C.bg1} 100%)
        `,
        overflow: "hidden",
      }}
    >
      {/* Audio Cues */}
      <Sequence from={2} layout="none">
        <Audio src={staticFile("sfx/whoosh.wav")} volume={0.34} />
      </Sequence>
      {METERLESS_ENGINES.map((e, i) => (
        <Sequence key={i} from={e.delay} layout="none">
          <Audio src={staticFile("sfx/pop.wav")} volume={0.28} />
        </Sequence>
      ))}
      <Sequence from={Math.floor(durationInFrames * 0.46)} layout="none">
        <Audio src={staticFile("sfx/hit.wav")} volume={0.3} />
      </Sequence>

      <ChromeFrame
        chapterNum="03"
        chapterTitle="LAYER 02 (BUILD): ADVERSARIAL CRITIC & ALL 4 METERLESS ENGINES"
        activeLayerBadge="02 BUILD // 4 METERLESS ENGINES"
        rightMetric="WORLD MODEL v15 · MARKOVIAN -84.0% TOKENS"
      />

      {/* Top 6-Step Non-Linear Multi-Agent Loop Strip */}
      <div
        style={{
          position: "absolute",
          top: 94,
          left: 56,
          right: 56,
          display: "grid",
          gridTemplateColumns: "repeat(6, 1fr)",
          gap: 12,
          zIndex: 20,
        }}
      >
        {AGENT_STEPS.map((s, idx) => {
          const isActive = idx === activeStepIdx;
          const isDone = idx < activeStepIdx;
          return (
            <div
              key={idx}
              style={{
                ...glassCardStyle(
                  isActive
                    ? s.color
                    : isDone
                    ? "rgba(16, 185, 129, 0.4)"
                    : "rgba(255,255,255,0.1)",
                  isActive ? 0.92 : 0.72
                ),
                borderRadius: 12,
                padding: "10px 14px",
                transform: isActive ? "scale(1.03)" : "scale(1)",
                boxShadow: isActive ? `0 0 28px ${s.color}44` : undefined,
              }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: 4,
                }}
              >
                <span
                  style={{
                    fontFamily: FONT.mono,
                    fontSize: 10.5,
                    fontWeight: 800,
                    color: s.color,
                  }}
                >
                  STEP {s.step}
                </span>
                <span
                  style={{
                    fontFamily: FONT.mono,
                    fontSize: 10,
                    padding: "2px 6px",
                    borderRadius: 4,
                    background: `${s.color}22`,
                    color: s.color,
                  }}
                >
                  {s.lane}
                </span>
              </div>
              <div
                style={{
                  fontFamily: FONT.display,
                  fontWeight: 700,
                  fontSize: 14,
                  color: C.ink,
                }}
              >
                {s.name}
              </div>
            </div>
          );
        })}
      </div>

      {/* Main Split: Left = 4 Stacked Meterless Engine Glass Cards | Right = Rotating 3D Browser */}
      <div
        style={{
          position: "absolute",
          top: 190,
          left: 56,
          right: 56,
          bottom: 92,
          display: "grid",
          gridTemplateColumns: "720px 1fr",
          gap: 32,
          alignItems: "center",
        }}
      >
        {/* Left Column: 4 Meterless Engines */}
        <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
          {METERLESS_ENGINES.map((eng, idx) => {
            const p = spring({
              frame: frame - eng.delay,
              fps,
              config: { damping: 18, stiffness: 100 },
            });
            return (
              <div
                key={idx}
                style={{
                  ...glassCardStyle(`${eng.color}66`, 0.84),
                  borderRadius: 16,
                  padding: "16px 20px",
                  transform: `translateX(${interpolate(p, [0, 1], [-48, 0])}px)`,
                  opacity: p,
                }}
              >
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    marginBottom: 6,
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <span
                      style={{
                        fontFamily: FONT.mono,
                        fontSize: 10.5,
                        fontWeight: 800,
                        padding: "3px 8px",
                        borderRadius: 6,
                        background: `${eng.color}20`,
                        color: eng.color,
                        border: `1px solid ${eng.color}55`,
                      }}
                    >
                      {eng.num}
                    </span>
                    <span
                      style={{
                        fontFamily: FONT.display,
                        fontWeight: 800,
                        fontSize: 19,
                        color: C.ink,
                      }}
                    >
                      {eng.name}
                    </span>
                  </div>
                  <span
                    style={{
                      fontFamily: FONT.mono,
                      fontWeight: 700,
                      fontSize: 12,
                      color: eng.color,
                    }}
                  >
                    {eng.metric}
                  </span>
                </div>
                <div
                  style={{
                    fontFamily: FONT.sans,
                    fontSize: 13.5,
                    color: C.inkDim,
                    lineHeight: 1.38,
                  }}
                >
                  {eng.detail}
                </div>
              </div>
            );
          })}
        </div>

        {/* Right Column: 3D Rotating Glass Browser */}
        <div style={{ display: "flex", justifyContent: "center" }}>
          <GlassBrowser3D
            screenFile={
              showEnginesScreen
                ? "screens/meterless-engines.png"
                : "screens/conflict-reconciliation.png"
            }
            urlText={
              showEnginesScreen
                ? "switchyard://meterless-engines // scout · world-model · markovian · h-mem"
                : "switchyard://adversarial-critic // round-1-rejected -> round-2-resolved"
            }
            rotateYDeg={tiltY}
            rotateXDeg={3}
            width={1030}
            height={650}
            accentColor={showEnginesScreen ? C.amber : C.emerald}
            statusPill={
              showEnginesScreen
                ? "ALL 4 METERLESS ENGINES VERIFIED"
                : "3/3 CONFLICTS RESOLVED"
            }
          />
        </div>
      </div>
    </AbsoluteFill>
  );
};
