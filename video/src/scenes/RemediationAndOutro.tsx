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

export const RemediationAndOutro: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const outroSplit = Math.floor(durationInFrames * 0.62);
  const outroProgress = spring({
    frame: frame - outroSplit,
    fps,
    config: { damping: 22, stiffness: 80, mass: 1.1 },
  });

  const beat1Opacity = interpolate(
    frame,
    [outroSplit - 12, outroSplit + 16],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const countProgress = interpolate(frame, [15, 110], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const savedDollars = Math.round(5422400 * countProgress);

  return (
    <AbsoluteFill
      style={{
        background: `
          radial-gradient(ellipse 75% 60% at 50% 45%, rgba(16, 185, 129, 0.15) 0%, transparent 65%),
          radial-gradient(ellipse 65% 55% at 50% 75%, rgba(163, 230, 53, 0.12) 0%, transparent 65%),
          linear-gradient(180deg, ${C.bg0} 0%, ${C.bg1} 100%)
        `,
        overflow: "hidden",
      }}
    >
      {/* Audio Cues */}
      <Sequence from={2} layout="none">
        <Audio src={staticFile("sfx/whoosh.wav")} volume={0.34} />
      </Sequence>
      <Sequence from={20} layout="none">
        <Audio src={staticFile("sfx/hit.wav")} volume={0.35} />
      </Sequence>
      <Sequence from={outroSplit} layout="none">
        <Audio src={staticFile("sfx/whoosh.wav")} volume={0.36} />
      </Sequence>
      <Sequence from={outroSplit + 12} layout="none">
        <Audio src={staticFile("sfx/hit.wav")} volume={0.42} />
      </Sequence>

      <ChromeFrame
        chapterNum="05"
        chapterTitle="SOURCED REMEDIATION & LINE-STOP PREVENTION"
        activeLayerBadge="CONFIDENCE 0.96 // APPROVED WITH PROVENANCE"
        rightMetric="85.1H DOWNTIME PREVENTED · $5,422,400 NET SAVED"
      />

      {/* BEAT 1: Sourced Remediation Order + Split Supplier Allocation + 3D Browser */}
      <div
        style={{
          position: "absolute",
          inset: "104px 56px 92px 56px",
          opacity: beat1Opacity,
          display: "grid",
          gridTemplateColumns: "720px 1fr",
          gap: 34,
          alignItems: "center",
        }}
      >
        {/* Left: Impact Counter + Split Allocation Cards */}
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {/* Hero Net Savings Card */}
          <div
            style={{
              ...glassCardStyle(`${C.emerald}88`, 0.88),
              borderRadius: 18,
              padding: "22px 24px",
            }}
          >
            <div
              style={{
                fontFamily: FONT.mono,
                fontSize: 12,
                fontWeight: 700,
                color: C.emerald,
                letterSpacing: "0.08em",
                marginBottom: 6,
              }}
            >
              VERIFIED REMEDIATION OUTCOME // PO-8841 · LINE-B INVERTER
            </div>
            <div
              style={{
                fontFamily: FONT.display,
                fontWeight: 800,
                fontSize: 64,
                lineHeight: 1,
                letterSpacing: "-0.04em",
                color: C.lime,
                marginBottom: 8,
              }}
            >
              ${savedDollars.toLocaleString()}
            </div>
            <div
              style={{
                fontFamily: FONT.sans,
                fontSize: 16,
                color: C.inkDim,
              }}
            >
              Net line-down loss avoided (85.1h downtime prevented at $64,000/hr
              for a $24,000 expedite premium ·{" "}
              <strong style={{ color: C.ink }}>225x ROI</strong>).
            </div>
          </div>

          {/* Lot Disposition Card */}
          <div
            style={{
              ...glassCardStyle(`${C.cyan}66`, 0.84),
              borderRadius: 15,
              padding: "16px 20px",
            }}
          >
            <div
              style={{
                fontFamily: FONT.mono,
                fontSize: 11,
                fontWeight: 700,
                color: C.cyan,
                marginBottom: 6,
              }}
            >
              01 // DOCK & QUARANTINE DISPOSITION [zetaris_qms.incident_tickets#QMS-419]
            </div>
            <div
              style={{
                fontFamily: FONT.display,
                fontWeight: 700,
                fontSize: 18,
                color: C.ink,
              }}
            >
              Release 350u in Sub-lot 992A-1 (0.0% void) · Reject 800u in
              Sub-lot 992A-2 (18.4% void)
            </div>
          </div>

          {/* Emergency Split Backup Allocation Cards */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: 14,
            }}
          >
            {[
              {
                sup: "Silicore Dresden GmbH",
                cite: "[zetaris_erp.qualified_suppliers#SUP-108]",
                qty: "2,400 units",
                terms: "$49.50/u · 2-Day Air · $118,800",
                color: C.lime,
              },
              {
                sup: "Pacific Semi Foundry",
                cite: "[zetaris_erp.qualified_suppliers#SUP-115]",
                qty: "1,250 units",
                terms: "$46.80/u · 3-Day Air · $58,500",
                color: C.emerald,
              },
            ].map((alloc, i) => (
              <div
                key={i}
                style={{
                  ...glassCardStyle(`${alloc.color}66`, 0.84),
                  borderRadius: 15,
                  padding: "16px 18px",
                }}
              >
                <div
                  style={{
                    fontFamily: FONT.mono,
                    fontSize: 10,
                    color: alloc.color,
                    marginBottom: 4,
                  }}
                >
                  {alloc.cite}
                </div>
                <div
                  style={{
                    fontFamily: FONT.display,
                    fontWeight: 800,
                    fontSize: 18,
                    color: C.ink,
                  }}
                >
                  {alloc.sup}
                </div>
                <div
                  style={{
                    fontFamily: FONT.mono,
                    fontWeight: 800,
                    fontSize: 22,
                    color: alloc.color,
                    margin: "6px 0 4px 0",
                  }}
                >
                  {alloc.qty}
                </div>
                <div
                  style={{
                    fontFamily: FONT.mono,
                    fontSize: 11.5,
                    color: C.inkDim,
                  }}
                >
                  {alloc.terms}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right: 3D Browser with Sourced Report */}
        <div style={{ display: "flex", justifyContent: "center" }}>
          <GlassBrowser3D
            screenFile="screens/conflict-reconciliation.png"
            urlText="switchyard://remediation-order // PO-8841 · HMEM-PREC-004 COMMITTED"
            rotateYDeg={-10 + Math.sin(frame * 0.03) * 1.5}
            rotateXDeg={3}
            width={1030}
            height={650}
            accentColor={C.emerald}
            statusPill="SOURCED ORDER ISSUED"
          />
        </div>
      </div>

      {/* BEAT 2: Monumental Hizz-Style Closing Card */}
      {frame >= outroSplit - 10 && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            opacity: outroProgress,
            transform: `scale(${interpolate(outroProgress, [0, 1], [0.94, 1])})`,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            textAlign: "center",
            padding: "0 80px",
          }}
        >
          {/* Glowing Brand Emblem */}
          <div
            style={{
              width: 88,
              height: 88,
              borderRadius: 24,
              background:
                "linear-gradient(135deg, #38bdf8 0%, #6366f1 50%, #a3e635 100%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: "0 0 65px rgba(163, 230, 53, 0.45)",
              fontFamily: FONT.mono,
              fontWeight: 900,
              fontSize: 36,
              color: "#05070b",
              marginBottom: 28,
            }}
          >
            SY
          </div>

          <div
            style={{
              fontFamily: FONT.mono,
              fontSize: 13,
              fontWeight: 700,
              color: C.cyan,
              letterSpacing: "0.14em",
              marginBottom: 16,
            }}
          >
            SWITCHYARD // OPEN AGENT HACKATHON 2026 · TRACK 1
          </div>

          <h1
            style={{
              margin: "0 0 22px 0",
              fontFamily: FONT.display,
              fontWeight: 800,
              fontSize: 94,
              lineHeight: 0.96,
              letterSpacing: "-0.045em",
              color: C.ink,
            }}
          >
            Reconcile reality
            <br />
            <span style={{ color: C.lime }}>before line-down.</span>
          </h1>

          <p
            style={{
              margin: "0 0 36px 0",
              fontFamily: FONT.sans,
              fontSize: 22,
              color: C.inkDim,
              maxWidth: 820,
            }}
          >
            Autonomous multi-agent supply-chain conflict reconciliation with
            full SQL provenance, adversarial verification, and cryptographic
            model receipts.
          </p>

          {/* Sponsor Verification Pill Row */}
          <div style={{ display: "flex", gap: 16 }}>
            {[
              {
                label: "01 DATA: ZETARIS LIGHTNING SQL",
                sub: "5 Tables · UUIDv4 Receipts",
                color: C.indigo,
              },
              {
                label: "02 BUILD: ALL 4 METERLESS ENGINES",
                sub: "Scout · WorldModel · Markovian · H-MEM",
                color: C.amber,
              },
              {
                label: "03 POWER: NIGHTSHIFT + NVIDIA NEMOTRON",
                sub: "Lightning 30B + Super 120B",
                color: C.lime,
              },
            ].map((p, i) => (
              <div
                key={i}
                style={{
                  ...glassCardStyle(`${p.color}77`, 0.86),
                  borderRadius: 14,
                  padding: "14px 22px",
                  textAlign: "left",
                }}
              >
                <div
                  style={{
                    fontFamily: FONT.mono,
                    fontSize: 12,
                    fontWeight: 800,
                    color: p.color,
                    marginBottom: 4,
                  }}
                >
                  {p.label}
                </div>
                <div
                  style={{
                    fontFamily: FONT.sans,
                    fontSize: 13,
                    color: C.ink,
                  }}
                >
                  {p.sub}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </AbsoluteFill>
  );
};
