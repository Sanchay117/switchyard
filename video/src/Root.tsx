import React from "react";
import { Composition } from "remotion";
import { Video } from "./Video";
import timingData from "./generated/timing.json";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="Switchyard"
        component={Video}
        durationInFrames={timingData.totalDurationInFrames}
        fps={timingData.fps}
        width={1920}
        height={1080}
      />
    </>
  );
};
