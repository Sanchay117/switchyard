import { spawnSync } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const input = path.resolve(__dirname, "../out/switchyard.mp4");
const output = path.resolve(__dirname, "../out/switchyard-final.mp4");
const TARGET = "I=-16:TP=-1.5:LRA=11";

console.log("Pass 1: Measuring integrated loudness (EBU R128)...");
const measure = spawnSync(
  "/opt/homebrew/bin/ffmpeg",
  ["-hide_banner", "-i", input, "-af", `loudnorm=${TARGET}:print_format=json`, "-f", "null", "-"],
  { encoding: "utf8" }
);
const json = measure.stderr.slice(
  measure.stderr.lastIndexOf("{"),
  measure.stderr.lastIndexOf("}") + 1
);
const m = JSON.parse(json) as Record<string, string>;
console.log(
  `Measured: ${m.input_i} LUFS, true peak ${m.input_tp} dBTP, LRA ${m.input_lra}`
);

const filter = `loudnorm=${TARGET}:measured_I=${m.input_i}:measured_TP=${m.input_tp}:measured_LRA=${m.input_lra}:measured_thresh=${m.input_thresh}:offset=${m.target_offset}:linear=true`;

console.log("Pass 2: Applying linear loudness normalization + H.264/AAC encoding...");
const r = spawnSync(
  "/opt/homebrew/bin/ffmpeg",
  [
    "-hide_banner",
    "-loglevel",
    "error",
    "-y",
    "-i",
    input,
    "-af",
    filter,
    "-ar",
    "48000",
    "-c:v",
    "libx264",
    "-preset",
    "medium",
    "-crf",
    "24",
    "-pix_fmt",
    "yuv420p",
    "-c:a",
    "aac",
    "-b:a",
    "192k",
    "-movflags",
    "+faststart",
    output,
  ],
  { stdio: "inherit" }
);
if (r.status !== 0) process.exit(1);

const check = spawnSync(
  "/opt/homebrew/bin/ffmpeg",
  ["-hide_banner", "-i", output, "-af", "ebur128=peak=true", "-f", "null", "-"],
  { encoding: "utf8" }
);
const summary = check.stderr.slice(check.stderr.lastIndexOf("Summary:"));
console.log(
  `Wrote ${output}\n${summary
    .split("\n")
    .filter((l) => /I:|Peak:/.test(l))
    .join("\n")}`
);
