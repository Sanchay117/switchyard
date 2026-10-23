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

const CONTRADICTION_CARDS = [
  {
    source: "zetaris_erp.purchase_orders",
    badge: "ERP SAYS",
    claim: "4,000 units · SHIPPED_ON_TIME",
    sub: "PO-8841 · Promised ETA Oct 25 · Apex Wafer Corp",
    color: C.emerald,
    delay: 28,
  },
  {
    source: "zetaris_wms.inventory_ledger",
    badge: "WMS DOCK SCAN",
    claim: "Only 350 Usable · 800 Quarantined",
    sub: "2,850 missing in transit · 35.9h Line-B runway left",
    color: C.red,
    delay: 95,
  },
  {
    source: "zetaris_qms.incident_tickets",
    badge: "QMS LAB VERDICT",
    claim: "18.4% Solder-Void Micro-Cracking",
    sub: "Ticket QMS-419 · Sub-lot 992A-2 failed acoustic scan",
    color: C.red,
    delay: 165,
  },
  {
    source: "zetaris_rest.carrier_port_feeds",
    badge: "OCEAN TELEMETRY",
    claim: "+96h Export Customs Hold",
    sub: "MV Pacific Horizon · Kaohsiung Port · ETA Oct 29",
    color: C.amber,
    delay: 235,
  },
];

export const Open: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const phaseSplit = Math.floor(durationInFrames * 0.54);
  const beat2Progress = spring({
    frame: frame - phaseSplit,
    fps,
    config: { damping: 22, stiffness: 80, mass: 1.1 },
  });

  const beat1Opacity = interpolate(
    frame,
    [phaseSplit - 12, phaseSplit + 18],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  const beat1Y = interpolate(beat2Progress, [0, 1], [0, -90]);

  const titleSpring = spring({
    frame: frame - 6,
    fps,
    config: { damping: 20, stiffness: 95 },
  });

  const browserRise = spring({
    frame: frame - (phaseSplit + 10),
    fps,
    config: { damping: 20, stiffness: 75, mass: 1.2 },
  });

  return (
    <AbsoluteFill
      style={{
        background: `
          radial-gradient(ellipse 75% 60% at 22% 28%, rgba(56, 189, 248, 0.13) 0%, transparent 65%),
          radial-gradient(ellipse 65% 55% at 78% 72%, rgba(163, 230, 53, 0.11) 0%, transparent 65%),
          linear-gradient(180deg, ${C.bg0} 0%, ${C.bg1} 100%)
        `,
        overflow: "hidden",
      }}
    >
      {/* SFX cues */}
      <Sequence from={4} layout="none">
        <Audio src={staticFile("sfx/hit.wav")} volume={0.38} />
      </Sequence>
      {CONTRADICTION_CARDS.map((c, i) => (
        <Sequence key={i} from={c.delay} layout="none">
          <Audio src={staticFile("sfx/pop.wav")} volume={0.28} />
        </Sequence>
      ))}
      <Sequence from={phaseSplit} layout="none">
        <Audio src={staticFile("sfx/whoosh.wav")} volume={0.36} />
      </Sequence>
      <Sequence from={phaseSplit + 14} layout="none">
        <Audio src={staticFile("sfx/hit.wav")} volume={0.34} />
      </Sequence>

      <ChromeFrame
        chapterNum="01"
        chapterTitle="FRAGMENTED ENTERPRISE REALITY"
        activeLayerBadge="TRACK 01 // SOLVING FRAGMENTED INTELLIGENCE"
      />

      {/* BEAT 1: Monumental Split-Tone Typography + 4 Contradicting Enterprise Sources */}
      <div
        style={{
          position: "absolute",
          inset: "110px 64px 96px 64px",
          opacity: beat1Opacity,
          transform: `translateY(${beat1Y}px)`,
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
        }}
      >
        {/* Top Monumental Headline (Hizz style) */}
        <div
          style={{
            transform: `translateY(${interpolate(titleSpring, [0, 1], [34, 0])}px)`,
            opacity: titleSpring,
          }}
        >
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 10,
              padding: "6px 14px",
              borderRadius: 999,
              background: "rgba(244, 63, 94, 0.12)",
              border: "1px solid rgba(244, 63, 94, 0.35)",
              fontFamily: FONT.mono,
              fontSize: 12,
              fontWeight: 700,
              color: "#fda4af",
              marginBottom: 18,
              letterSpacing: "0.08em",
            }}
          >
            LIVE INCIDENT // PO-8841 · 1200V SIC POWER MODULES · LINE-B INVERTER
          </div>

          <h1
            style={{
              margin: 0,
              fontFamily: FONT.display,
              fontWeight: 800,
              fontSize: 82,
              lineHeight: 0.98,
              letterSpacing: "-0.042em",
              color: C.ink,
            }}
          >
            Enterprise systems disagree
            <br />
            <span style={{ color: C.inkMute }}>while a </span>
            <span style={{ color: C.lime }}>$64,000/hr line</span>
            <span style={{ color: C.inkMute }}> runs dry.</span>
          </h1>
        </div>

        {/* 4 Contradicting Glass Source Cards */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(4, 1fr)",
            gap: 20,
            marginBottom: 24,
          }}
        >
          {CONTRADICTION_CARDS.map((card, idx) => {
            const p = spring({
              frame: frame - card.delay,
              fps,
              config: { damping: 18, stiffness: 110 },
            });
            return (
              <div
                key={idx}
                style={{
                  ...glassCardStyle(`${card.color}55`, 0.8),
                  borderRadius: 18,
                  padding: "24px 22px",
                  transform: `translateY(${interpolate(p, [0, 1], [48, 0])}px) scale(${interpolate(
                    p,
                    [0, 1],
                    [0.94, 1]
                  )})`,
                  opacity: p,
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "space-between",
                  minHeight: 220,
                }}
              >
                <div>
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      marginBottom: 14,
                    }}
                  >
                    <span
                      style={{
                        fontFamily: FONT.mono,
                        fontSize: 11,
                        fontWeight: 700,
                        padding: "4px 9px",
                        borderRadius: 6,
                        background: `${card.color}22`,
                        color: card.color,
                        border: `1px solid ${card.color}55`,
                      }}
                    >
                      {card.badge}
                    </span>
                    <span
                      style={{
                        fontFamily: FONT.mono,
                        fontSize: 11,
                        color: C.inkMute,
                      }}
                    >
                      0{idx + 1}
                    </span>
                  </div>
                  <div
                    style={{
                      fontFamily: FONT.mono,
                      fontSize: 12.5,
                      color: C.cyan,
                      marginBottom: 10,
                    }}
                  >
                    {card.source}
                  </div>
                  <div
                    style={{
                      fontFamily: FONT.display,
                      fontWeight: 700,
                      fontSize: 24,
                      lineHeight: 1.18,
                      color: C.ink,
                      letterSpacing: "-0.02em",
                    }}
                  >
                    {card.claim}
                  </div>
                </div>

                <div
                  style={{
                    marginTop: 18,
                    paddingTop: 12,
                    borderTop: "1px solid rgba(255,255,255,0.08)",
                    fontFamily: FONT.sans,
                    fontSize: 13.5,
                    color: C.inkDim,
                    lineHeight: 1.35,
                  }}
                >
                  {card.sub}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* BEAT 2: Meet Switchyard + 3D Perspective Command Center Reveal */}
      {frame >= phaseSplit - 10 && (
        <div
          style={{
            position: "absolute",
            inset: "106px 60px 92px 60px",
            opacity: beat2Progress,
            display: "grid",
            gridTemplateColumns: "680px 1fr",
            alignItems: "center",
            gap: 36,
          }}
        >
          {/* Left Column: Hero Title + 3-Layer Stack */}
          <div
            style={{
              transform: `translateX(${interpolate(beat2Progress, [0, 1], [-45, 0])}px)`,
            }}
          >
            <div
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 8,
                padding: "6px 14px",
                borderRadius: 999,
                background: "rgba(163, 230, 53, 0.14)",
                border: "1px solid rgba(163, 230, 53, 0.4)",
                fontFamily: FONT.mono,
                fontSize: 12,
                fontWeight: 700,
                color: C.lime,
                marginBottom: 18,
                letterSpacing: "0.08em",
              }}
            >
              AUTONOMOUS MULTI-AGENT RECONCILIATION
            </div>

            <h2
              style={{
                margin: "0 0 18px 0",
                fontFamily: FONT.display,
                fontWeight: 800,
                fontSize: 72,
                lineHeight: 0.98,
                letterSpacing: "-0.04em",
                color: C.ink,
              }}
            >
              Meet Switchyard.
              <br />
              <span style={{ color: C.cyan }}>Sourced truth</span>
              <br />
              <span style={{ color: C.inkMute }}>in seconds.</span>
            </h2>

            <p
              style={{
                margin: "0 0 26px 0",
                fontFamily: FONT.sans,
                fontSize: 20,
                lineHeight: 1.45,
                color: C.inkDim,
                maxWidth: 610,
              }}
            >
              Queries disconnected enterprise tables through Zetaris, challenges
              incomplete claims with an adversarial Critic, and issues an
              executable backup allocation before line-stop.
            </p>

            {/* 3 Mandatory Hackathon Architecture Layers */}
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {[
                {
                  code: "01 DATA",
                  title: "Zetaris Federated Data Harness",
                  desc: "Single-statement Lightning SQL across ERP, WMS, QMS & Carrier REST",
                  accent: C.indigo,
                },
                {
                  code: "02 BUILD",
                  title: "All 4 Meterless Engines Active",
                  desc: "Scout Intent · World Model v15 · Markovian (-84% tokens) · H-MEM",
                  accent: C.amber,
                },
                {
                  code: "03 POWER",
                  title: "Meterless Nightshift + Dual NVIDIA Nemotron",
                  desc: "Nemotron 3.5 Lightning 30B (Fast) + Super 120B (Deep Critic)",
                  accent: C.lime,
                },
              ].map((layer, idx) => (
                <div
                  key={idx}
                  style={{
                    ...glassCardStyle(`${layer.accent}44`, 0.78),
                    borderRadius: 14,
                    padding: "13px 18px",
                    display: "flex",
                    alignItems: "center",
                    gap: 16,
                  }}
                >
                  <div
                    style={{
                      fontFamily: FONT.mono,
                      fontWeight: 800,
                      fontSize: 12,
                      color: layer.accent,
                      padding: "6px 10px",
                      borderRadius: 8,
                      background: `${layer.accent}18`,
                      border: `1px solid ${layer.accent}44`,
                      minWidth: 88,
                      textAlign: "center",
                    }}
                  >
                    {layer.code}
                  </div>
                  <div>
                    <div
                      style={{
                        fontFamily: FONT.display,
                        fontWeight: 700,
                        fontSize: 16.5,
                        color: C.ink,
                      }}
                    >
                      {layer.title}
                    </div>
                    <div
                      style={{
                        fontFamily: FONT.mono,
                        fontSize: 12,
                        color: C.inkDim,
                        marginTop: 2,
                      }}
                    >
                      {layer.desc}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Right Column: 3D Tilted Glass Browser (Hizz signature angle) */}
          <div
            style={{
              display: "flex",
              justifyContent: "center",
              transform: `translateY(${interpolate(browserRise, [0, 1], [60, 0])}px)`,
            }}
          >
            <GlassBrowser3D
              screenFile="screens/command-center.png"
              rotateYDeg={-14 + Math.sin(frame * 0.03) * 1.5}
              rotateXDeg={4}
              width={1040}
              height={640}
              accentColor={C.cyan}
              statusPill="CASE-01 // PO-8841 ACTIVE"
            />
          </div>
        </div>
      )}
    </AbsoluteFill>
  );
};
