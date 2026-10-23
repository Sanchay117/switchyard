import React from "react";
import {
  AbsoluteFill,
  Audio,
  Sequence,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import timingData from "./generated/timing.json";
import { SceneId } from "./narration";
import { C } from "./theme";
import { Open } from "./scenes/Open";
import { NodeGraph3D } from "./scenes/NodeGraph3D";
import { CriticAndEngines } from "./scenes/CriticAndEngines";
import { NemotronLanes } from "./scenes/NemotronLanes";
import { RemediationAndOutro } from "./scenes/RemediationAndOutro";

const SCENE_COMPONENTS: Record<SceneId, React.FC> = {
  open: Open,
  zetaris: NodeGraph3D,
  engines: CriticAndEngines,
  nemotron: NemotronLanes,
  outro: RemediationAndOutro,
};

const SceneCrossfade: React.FC<{
  id: SceneId;
  frames: number;
  fadeFrames: number;
  isFirst: boolean;
  isLast: boolean;
}> = ({ id, frames, fadeFrames, isFirst, isLast }) => {
  const frame = useCurrentFrame();
  const s = timingData.scenes[id];
  const Comp = SCENE_COMPONENTS[id];

  const fadeIn = isFirst
    ? 1
    : interpolate(frame, [0, fadeFrames], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
  const fadeOut = isLast
    ? 1
    : interpolate(frame, [frames - fadeFrames, frames], [1, 0], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
  const opacity = Math.min(fadeIn, fadeOut);

  return (
    <AbsoluteFill style={{ opacity }}>
      <Comp />
      <Sequence from={s.voStartFrame} layout="none">
        <Audio src={staticFile(s.audioFile)} volume={1.0} />
      </Sequence>
    </AbsoluteFill>
  );
};

export const Video: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const T = timingData.transitionFrames;
  const order = timingData.order as SceneId[];

  let cursor = 0;
  const scheduled = order.map((id, idx) => {
    const dur = timingData.scenes[id].durationInFrames;
    const from = cursor;
    cursor += dur - T;
    return { id, from, dur, isFirst: idx === 0, isLast: idx === order.length - 1 };
  });

  const bedVol = interpolate(
    frame,
    [0, 25, 45, durationInFrames - 60, durationInFrames - 12],
    [0.0, 0.24, 0.14, 0.14, 0.28],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  return (
    <AbsoluteFill style={{ background: C.bg0 }}>
      <Audio src={staticFile("music/bed.wav")} volume={bedVol} />

      {scheduled.map((item) => (
        <Sequence
          key={item.id}
          from={item.from}
          durationInFrames={item.dur}
          name={item.id}
        >
          <SceneCrossfade
            id={item.id}
            frames={item.dur}
            fadeFrames={T}
            isFirst={item.isFirst}
            isLast={item.isLast}
          />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
