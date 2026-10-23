import React from "react";
import { Img, staticFile, useCurrentFrame } from "remotion";
import { C, FONT } from "../theme";

interface GlassBrowser3DProps {
  screenFile: string;
  urlText?: string;
  rotateYDeg?: number;
  rotateXDeg?: number;
  rotateZDeg?: number;
  scale?: number;
  width?: number;
  height?: number;
  accentColor?: string;
  statusPill?: string;
}

export const GlassBrowser3D: React.FC<GlassBrowser3DProps> = ({
  screenFile,
  urlText = "http://127.0.0.1:8050 // switchyard-command-center",
  rotateYDeg = -13,
  rotateXDeg = 3.5,
  rotateZDeg = 0,
  scale = 1,
  width = 1060,
  height = 660,
  accentColor = C.cyan,
  statusPill = "LIVE TRACE // RUN-PO-8841",
}) => {
  const frame = useCurrentFrame();
  const sheenPos = ((frame * 1.4) % 240) - 60;

  return (
    <div
      style={{
        width,
        height,
        transform: `perspective(1550px) rotateY(${rotateYDeg}deg) rotateX(${rotateXDeg}deg) rotateZ(${rotateZDeg}deg) scale(${scale})`,
        transformStyle: "preserve-3d",
        borderRadius: 20,
        background: "rgba(9, 13, 22, 0.92)",
        border: "1px solid rgba(255, 255, 255, 0.18)",
        boxShadow: `
          0 45px 110px rgba(0, 0, 0, 0.78),
          0 0 65px ${accentColor}22,
          inset 0 1px 0 rgba(255, 255, 255, 0.32)
        `,
        overflow: "hidden",
        display: "flex",
        flexDirection: "column",
        position: "relative",
      }}
    >
      {/* Top Browser Chrome Bar */}
      <div
        style={{
          height: 44,
          padding: "0 18px",
          background:
            "linear-gradient(180deg, rgba(24, 34, 54, 0.95) 0%, rgba(13, 19, 32, 0.95) 100%)",
          borderBottom: "1px solid rgba(255, 255, 255, 0.1)",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexShrink: 0,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span
            style={{
              width: 11,
              height: 11,
              borderRadius: "50%",
              background: "#f43f5e",
            }}
          />
          <span
            style={{
              width: 11,
              height: 11,
              borderRadius: "50%",
              background: "#f59e0b",
            }}
          />
          <span
            style={{
              width: 11,
              height: 11,
              borderRadius: "50%",
              background: "#10b981",
            }}
          />
        </div>

        {/* Center Glass URL Bar */}
        <div
          style={{
            padding: "5px 18px",
            borderRadius: 8,
            background: "rgba(5, 7, 11, 0.68)",
            border: "1px solid rgba(255, 255, 255, 0.09)",
            fontFamily: FONT.mono,
            fontSize: 11.5,
            color: C.inkDim,
            letterSpacing: "0.02em",
          }}
        >
          {urlText}
        </div>

        <div
          style={{
            padding: "4px 10px",
            borderRadius: 6,
            background: "rgba(163, 230, 53, 0.14)",
            border: "1px solid rgba(163, 230, 53, 0.35)",
            fontFamily: FONT.mono,
            fontSize: 10.5,
            fontWeight: 700,
            color: C.lime,
          }}
        >
          {statusPill}
        </div>
      </div>

      {/* Main UI Screenshot Viewport */}
      <div style={{ flex: 1, position: "relative", overflow: "hidden" }}>
        <Img
          src={staticFile(screenFile)}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            objectPosition: "top center",
          }}
        />

        {/* Subtle Specular Glass Reflection Sweep */}
        <div
          style={{
            position: "absolute",
            inset: 0,
            background: `linear-gradient(115deg, transparent ${sheenPos}%, rgba(255, 255, 255, 0.055) ${
              sheenPos + 14
            }%, transparent ${sheenPos + 28}%)`,
            pointerEvents: "none",
          }}
        />
      </div>
    </div>
  );
};
