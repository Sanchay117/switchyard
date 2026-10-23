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

const ZETARIS_NODES = [
  {
    table: "zetaris_erp.purchase_orders",
    reqId: "req:ead0326a",
    metric: "4,000u · SHIPPED_ON_TIME",
    sql: "SELECT * FROM zetaris_erp.purchase_orders WHERE po_number = 'PO-8841'",
    color: C.indigo,
    y: 195,
  },
  {
    table: "zetaris_wms.inventory_ledger",
    reqId: "req:c463d9ff",
    metric: "350u Usable · 800u Quarantine",
    sql: "SELECT * FROM zetaris_wms.inventory_ledger WHERE po_number = 'PO-8841'",
    color: C.cyan,
    y: 355,
  },
  {
    table: "zetaris_qms.incident_tickets",
    reqId: "req:71b00ffe",
    metric: "QMS-419 · 18.4% Void Defect",
    sql: "SELECT * FROM zetaris_qms.incident_tickets WHERE po_number = 'PO-8841'",
    color: C.red,
    y: 515,
  },
  {
    table: "zetaris_rest.carrier_port_feeds",
    reqId: "req:c7fd13cb",
    metric: "CAR-901 · +96h Customs Hold",
    sql: "SELECT * FROM zetaris_rest.carrier_port_feeds WHERE po_number = 'PO-8841'",
    color: C.amber,
    y: 675,
  },
  {
    table: "zetaris_erp.qualified_suppliers",
    reqId: "req:97a69b53",
    metric: "2 Qualified Backups (DE / KR)",
    sql: "SELECT * FROM zetaris_erp.qualified_suppliers WHERE sku = 'SIC-MOD-1200V'",
    color: C.emerald,
    y: 835,
  },
];

export const NodeGraph3D: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const switchScreen = frame > durationInFrames * 0.48;
  const hubY = 515;
  const hubX = 690;

  return (
    <AbsoluteFill
      style={{
        background: `
          radial-gradient(ellipse 70% 60% at 32% 50%, rgba(99, 102, 241, 0.14) 0%, transparent 65%),
          radial-gradient(ellipse 65% 55% at 76% 48%, rgba(56, 189, 248, 0.12) 0%, transparent 65%),
          linear-gradient(180deg, ${C.bg0} 0%, ${C.bg1} 100%)
        `,
        overflow: "hidden",
      }}
    >
      {/* Audio Cues */}
      <Sequence from={2} layout="none">
        <Audio src={staticFile("sfx/whoosh.wav")} volume={0.34} />
      </Sequence>
      {ZETARIS_NODES.map((_, i) => (
        <Sequence key={i} from={18 + i * 24} layout="none">
          <Audio src={staticFile("sfx/pulse.wav")} volume={0.25} />
        </Sequence>
      ))}
      <Sequence from={Math.floor(durationInFrames * 0.48)} layout="none">
        <Audio src={staticFile("sfx/pop.wav")} volume={0.3} />
      </Sequence>

      <ChromeFrame
        chapterNum="02"
        chapterTitle="LAYER 01 (DATA): ZETARIS FEDERATED SQL HARNESS"
        activeLayerBadge="01 DATA // ZETARIS LIGHTNING SQL"
        rightMetric="5 TABLES VIRTUALIZED · 0.02ms FEDERATED JOIN"
      />

      {/* Top Section Title */}
      <div
        style={{
          position: "absolute",
          top: 94,
          left: 60,
          zIndex: 20,
        }}
      >
        <div
          style={{
            fontFamily: FONT.display,
            fontWeight: 800,
            fontSize: 38,
            letterSpacing: "-0.03em",
            color: C.ink,
          }}
        >
          Single-Statement Federated SQL{" "}
          <span style={{ color: C.indigo }}>Across 5 Disconnected Sources</span>
        </div>
      </div>

      {/* SVG Animated Cubic-Bezier Conduit Layer (Hizz Scene 2 signature) */}
      <svg
        width={1920}
        height={1080}
        style={{ position: "absolute", inset: 0, pointerEvents: "none", zIndex: 5 }}
      >
        <defs>
          <linearGradient id="bezierGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor={C.indigo} stopOpacity="0.85" />
            <stop offset="50%" stopColor={C.cyan} stopOpacity="0.95" />
            <stop offset="100%" stopColor={C.lime} stopOpacity="0.9" />
          </linearGradient>
        </defs>

        {ZETARIS_NODES.map((node, idx) => {
          const startX = 485;
          const startY = node.y + 38;
          const pathD = `M ${startX} ${startY} C ${startX + 95} ${startY}, ${
            hubX - 95
          } ${hubY}, ${hubX} ${hubY}`;
          const dashOffset = -frame * 4.5 + idx * 35;

          return (
            <g key={idx}>
              {/* Base curve */}
              <path
                d={pathD}
                fill="none"
                stroke="rgba(148, 163, 184, 0.18)"
                strokeWidth={2}
              />
              {/* Animated glowing pulse stream */}
              <path
                d={pathD}
                fill="none"
                stroke={node.color}
                strokeWidth={3}
                strokeDasharray="18 28"
                strokeDashoffset={dashOffset}
                opacity={0.9}
              />
            </g>
          );
        })}

        {/* Output curves from Zetaris Hub into 3D Browser Window */}
        {[-110, 0, 110].map((offsetY, i) => {
          const outD = `M ${hubX + 115} ${hubY} C ${hubX + 165} ${hubY}, ${
            hubX + 175
          } ${hubY + offsetY}, ${hubX + 235} ${hubY + offsetY}`;
          return (
            <g key={i}>
              <path
                d={outD}
                fill="none"
                stroke="url(#bezierGrad)"
                strokeWidth={3}
                strokeDasharray="14 20"
                strokeDashoffset={-frame * 5.2}
              />
            </g>
          );
        })}
      </svg>

      {/* Left Column: 5 Stacked Zetaris Source Nodes */}
      {ZETARIS_NODES.map((node, idx) => {
        const p = spring({
          frame: frame - (10 + idx * 16),
          fps,
          config: { damping: 18, stiffness: 105 },
        });
        return (
          <div
            key={idx}
            style={{
              position: "absolute",
              left: 60,
              top: node.y,
              width: 425,
              ...glassCardStyle(`${node.color}66`, 0.84),
              borderRadius: 14,
              padding: "13px 16px",
              transform: `translateX(${interpolate(p, [0, 1], [-40, 0])}px)`,
              opacity: p,
              zIndex: 12,
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
                  fontWeight: 700,
                  fontSize: 13,
                  color: node.color,
                }}
              >
                {node.table}
              </span>
              <span
                style={{
                  fontFamily: FONT.mono,
                  fontSize: 10.5,
                  color: C.inkDim,
                  padding: "2px 7px",
                  borderRadius: 5,
                  background: "rgba(255,255,255,0.06)",
                }}
              >
                {node.reqId}
              </span>
            </div>
            <div
              style={{
                fontFamily: FONT.display,
                fontWeight: 700,
                fontSize: 16,
                color: C.ink,
                marginBottom: 4,
              }}
            >
              {node.metric}
            </div>
            <div
              style={{
                fontFamily: FONT.mono,
                fontSize: 10.5,
                color: C.inkMute,
                whiteSpace: "nowrap",
                overflow: "hidden",
                textOverflow: "ellipsis",
              }}
            >
              {node.sql}
            </div>
          </div>
        );
      })}

      {/* Center Hub: Zetaris Lightning SQL Router Node */}
      <div
        style={{
          position: "absolute",
          left: hubX - 95,
          top: hubY - 72,
          width: 215,
          height: 144,
          ...glassCardStyle(`${C.indigo}99`, 0.92),
          borderRadius: 18,
          padding: "14px 16px",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          textAlign: "center",
          zIndex: 15,
          boxShadow: `0 0 50px rgba(99, 102, 241, 0.42), inset 0 1px 0 rgba(255,255,255,0.3)`,
        }}
      >
        <div
          style={{
            fontFamily: FONT.mono,
            fontSize: 10.5,
            fontWeight: 800,
            color: C.cyan,
            letterSpacing: "0.08em",
            marginBottom: 6,
          }}
        >
          ZETARIS LIGHTNING
        </div>
        <div
          style={{
            fontFamily: FONT.display,
            fontWeight: 800,
            fontSize: 18,
            color: C.ink,
            lineHeight: 1.15,
          }}
        >
          /sql-editor/sqls/run
        </div>
        <div
          style={{
            marginTop: 8,
            fontFamily: FONT.mono,
            fontSize: 10.5,
            color: C.lime,
            padding: "3px 8px",
            borderRadius: 6,
            background: "rgba(163, 230, 53, 0.14)",
            border: "1px solid rgba(163, 230, 53, 0.35)",
          }}
        >
          X-Org-ID: 1 · UUIDv4
        </div>
      </div>

      {/* Right Column: 3D Perspective Glass Browser Window */}
      <div
        style={{
          position: "absolute",
          right: 52,
          top: 175,
          zIndex: 14,
        }}
      >
        <GlassBrowser3D
          screenFile={
            switchScreen ? "screens/zetaris-sql.png" : "screens/command-center.png"
          }
          urlText="POST https://api.zetaris.com/api/v1.0/sql-editor/sqls/run"
          rotateYDeg={-13 + Math.sin(frame * 0.025) * 2}
          rotateXDeg={3.5}
          width={980}
          height={640}
          accentColor={C.indigo}
          statusPill={
            switchScreen
              ? "SQL RECEIPTS // 5 QUERIES VERIFIED"
              : "4-SOURCE PROVENANCE GRAPH"
          }
        />
      </div>
    </AbsoluteFill>
  );
};
