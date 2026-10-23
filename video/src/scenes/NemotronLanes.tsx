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

const RECEIPTS = [
  {
    id: "NS-RCPT-001-96b61b",
    step: "Step 1: Planner & Source Mapper",
    model: "nvidia/nemotron-3.5-lightning-30b-a3b",
    lane: "Lane 1: Fast",
    tokens: "404p / 291c",
    color: C.cyan,
  },
  {
    id: "NS-RCPT-002-85bac9",
    step: "Step 2: Reconciler Round 1 SQL",
    model: "nvidia/nemotron-3.5-lightning-30b-a3b",
    lane: "Lane 1: Fast",
    tokens: "527p / 158c",
    color: C.cyan,
  },
  {
    id: "NS-RCPT-003-9e52f7",
    step: "Step 3: Adversarial Conflict Critic",
    model: "nvidia/nemotron-3.5-super-vl-120b-a12b",
    lane: "Lane 2: Deep",
    tokens: "397p / 162c",
    color: C.lime,
  },
  {
    id: "NS-RCPT-004-eb0e22",
    step: "Step 4: Reconciler Round 2 SQL",
    model: "nvidia/nemotron-3.5-lightning-30b-a3b",
    lane: "Lane 1: Fast",
    tokens: "603p / 151c",
    color: C.cyan,
  },
  {
    id: "NS-RCPT-005-26543f",
    step: "Step 5: Risk Escalation & Sign-Off",
    model: "nvidia/nemotron-3.5-super-vl-120b-a12b",
    lane: "Lane 2: Deep",
    tokens: "556p / 184c",
    color: C.lime,
  },
  {
    id: "NS-RCPT-006-bf6904",
    step: "Step 6: Sourced Decision Reporter",
    model: "nvidia/nemotron-3.5-super-vl-120b-a12b",
    lane: "Lane 2: Deep",
    tokens: "615p / 681c",
    color: C.lime,
  },
];

export const NemotronLanes: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const lane1Spring = spring({
    frame: frame - 14,
    fps,
    config: { damping: 18, stiffness: 95 },
  });
  const lane2Spring = spring({
    frame: frame - 42,
    fps,
    config: { damping: 18, stiffness: 95 },
  });

  return (
    <AbsoluteFill
      style={{
        background: `
          radial-gradient(ellipse 72% 58% at 24% 40%, rgba(163, 230, 53, 0.14) 0%, transparent 65%),
          radial-gradient(ellipse 65% 55% at 78% 58%, rgba(56, 189, 248, 0.12) 0%, transparent 65%),
          linear-gradient(180deg, ${C.bg0} 0%, ${C.bg1} 100%)
        `,
        overflow: "hidden",
      }}
    >
      {/* Audio Cues */}
      <Sequence from={2} layout="none">
        <Audio src={staticFile("sfx/whoosh.wav")} volume={0.34} />
      </Sequence>
      <Sequence from={18} layout="none">
        <Audio src={staticFile("sfx/pop.wav")} volume={0.3} />
      </Sequence>
      <Sequence from={46} layout="none">
        <Audio src={staticFile("sfx/pop.wav")} volume={0.3} />
      </Sequence>

      <ChromeFrame
        chapterNum="04"
        chapterTitle="LAYER 03 (POWER): METERLESS NIGHTSHIFT & DUAL NVIDIA NEMOTRON LANES"
        activeLayerBadge="03 POWER // NVIDIA NEMOTRON 3.5"
        rightMetric="6/6 MODEL RECEIPTS VERIFIED · 127.0.0.1:8088"
      />

      {/* Main Content Split */}
      <div
        style={{
          position: "absolute",
          inset: "104px 56px 92px 56px",
          display: "grid",
          gridTemplateColumns: "720px 1fr",
          gap: 34,
          alignItems: "center",
        }}
      >
        {/* Left Column: Nightshift Gateway + Dual Nemotron Lanes + Live Receipt Ticker */}
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <div>
            <div
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 8,
                padding: "5px 12px",
                borderRadius: 999,
                background: "rgba(163, 230, 53, 0.14)",
                border: "1px solid rgba(163, 230, 53, 0.4)",
                fontFamily: FONT.mono,
                fontSize: 11.5,
                fontWeight: 700,
                color: C.lime,
                marginBottom: 10,
              }}
            >
              PRIMARY AI PROVIDER // http://127.0.0.1:8088/v1
            </div>
            <h2
              style={{
                margin: 0,
                fontFamily: FONT.display,
                fontWeight: 800,
                fontSize: 48,
                lineHeight: 1.02,
                letterSpacing: "-0.035em",
                color: C.ink,
              }}
            >
              Dual NVIDIA Nemotron Lanes{" "}
              <span style={{ color: C.lime }}>via Nightshift Runtime</span>
            </h2>
          </div>

          {/* Lane 1 Card */}
          <div
            style={{
              ...glassCardStyle(`${C.cyan}77`, 0.85),
              borderRadius: 16,
              padding: "18px 20px",
              transform: `translateX(${interpolate(lane1Spring, [0, 1], [-45, 0])}px)`,
              opacity: lane1Spring,
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
              <span
                style={{
                  fontFamily: FONT.mono,
                  fontSize: 11,
                  fontWeight: 800,
                  padding: "3px 9px",
                  borderRadius: 6,
                  background: "rgba(56, 189, 248, 0.16)",
                  color: C.cyan,
                  border: "1px solid rgba(56, 189, 248, 0.4)",
                }}
              >
                LANE 01 // FAST WORKER (3 CALLS)
              </span>
              <span
                style={{
                  fontFamily: FONT.mono,
                  fontSize: 11,
                  color: C.inkDim,
                }}
              >
                Steps 1, 2, 4
              </span>
            </div>
            <div
              style={{
                fontFamily: FONT.mono,
                fontWeight: 800,
                fontSize: 20,
                color: C.ink,
                marginBottom: 4,
              }}
            >
              nvidia/nemotron-3.5-lightning-30b-a3b
            </div>
            <div
              style={{
                fontFamily: FONT.sans,
                fontSize: 13.5,
                color: C.inkDim,
              }}
            >
              High-throughput Scout Intent routing & iterative Zetaris SQL query
              generation across Round 1 and Round 2.
            </div>
          </div>

          {/* Lane 2 Card */}
          <div
            style={{
              ...glassCardStyle(`${C.lime}88`, 0.88),
              borderRadius: 16,
              padding: "18px 20px",
              transform: `translateX(${interpolate(lane2Spring, [0, 1], [-45, 0])}px)`,
              opacity: lane2Spring,
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
              <span
                style={{
                  fontFamily: FONT.mono,
                  fontSize: 11,
                  fontWeight: 800,
                  padding: "3px 9px",
                  borderRadius: 6,
                  background: "rgba(163, 230, 53, 0.18)",
                  color: C.lime,
                  border: "1px solid rgba(163, 230, 53, 0.45)",
                }}
              >
                LANE 02 // DEEP REASONING CRITIC (3 CALLS)
              </span>
              <span
                style={{
                  fontFamily: FONT.mono,
                  fontSize: 11,
                  color: C.inkDim,
                }}
              >
                Steps 3, 5, 6
              </span>
            </div>
            <div
              style={{
                fontFamily: FONT.mono,
                fontWeight: 800,
                fontSize: 20,
                color: C.lime,
                marginBottom: 4,
              }}
            >
              nvidia/nemotron-3.5-super-vl-120b-a12b
            </div>
            <div
              style={{
                fontFamily: FONT.sans,
                fontSize: 13.5,
                color: C.inkDim,
              }}
            >
              Adversarial Conflict Critique, QMS acoustic lab dispute
              verification, and final Sourced Remediation synthesis.
            </div>
          </div>

          {/* 6 ModelReceipt Mini-Ledger */}
          <div
            style={{
              ...glassCardStyle("rgba(255,255,255,0.14)", 0.82),
              borderRadius: 14,
              padding: "12px 16px",
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: 8,
            }}
          >
            {RECEIPTS.map((r, idx) => (
              <div
                key={idx}
                style={{
                  padding: "7px 10px",
                  borderRadius: 8,
                  background: "rgba(5, 7, 11, 0.65)",
                  border: `1px solid ${r.color}40`,
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <div>
                  <div
                    style={{
                      fontFamily: FONT.mono,
                      fontSize: 10,
                      color: r.color,
                      fontWeight: 700,
                    }}
                  >
                    {r.id}
                  </div>
                  <div
                    style={{
                      fontFamily: FONT.sans,
                      fontSize: 11,
                      color: C.ink,
                      fontWeight: 600,
                    }}
                  >
                    {r.step}
                  </div>
                </div>
                <span
                  style={{
                    fontFamily: FONT.mono,
                    fontSize: 10,
                    color: C.inkDim,
                  }}
                >
                  {r.lane}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Right Column: 3D Perspective Glass Browser showing Nightshift & Nemotron Receipts */}
        <div style={{ display: "flex", justifyContent: "center" }}>
          <GlassBrowser3D
            screenFile="screens/nightshift-receipts.png"
            urlText="http://127.0.0.1:8088/v1/chat/completions // meterless-app: switchyard-agent"
            rotateYDeg={-12 + Math.sin(frame * 0.03) * 2}
            rotateXDeg={3.5}
            width={1030}
            height={650}
            accentColor={C.lime}
            statusPill="6 NEMOTRON RECEIPTS LOGGED"
          />
        </div>
      </div>
    </AbsoluteFill>
  );
};
