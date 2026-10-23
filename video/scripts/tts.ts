import fs from "node:fs";
import path from "node:path";
import { createHash } from "node:crypto";
import { fileURLToPath } from "node:url";
import { NARRATION, NARRATION_VOICE, SceneId } from "../src/narration";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");

function loadEnvKey(): string {
  if (process.env.DEEPGRAM_API_KEY) return process.env.DEEPGRAM_API_KEY;
  const candidates = [
    path.resolve(ROOT, "../.env"),
    path.resolve(ROOT, "../../Strike/.env"),
  ];
  for (const envPath of candidates) {
    if (fs.existsSync(envPath)) {
      const m = fs
        .readFileSync(envPath, "utf8")
        .match(/^\s*DEEPGRAM_API_KEY\s*=\s*"?([^"\n\r]+)"?/m);
      if (m?.[1]) return m[1].trim();
    }
  }
  throw new Error("DEEPGRAM_API_KEY missing");
}

const VO_DIR = path.join(ROOT, "public/vo");
const OUT_TIMING = path.join(ROOT, "src/generated/timing.json");
const CACHE_PATH = path.join(ROOT, "src/generated/tts-cache.json");
const FPS = 30;
const GAP = 0.34;
const TRANSITION_FRAMES = 12;

function wavSeconds(buf: Buffer): number {
  let off = 12;
  let byteRate = 96000;
  while (off + 8 <= buf.length) {
    const id = buf.toString("ascii", off, off + 4);
    let size = buf.readUInt32LE(off + 4);
    if (id === "fmt ") {
      byteRate = buf.readUInt32LE(off + 16);
    }
    if (id === "data") {
      if (size === 0 || size === 0xffffffff || off + 8 + size > buf.length) {
        size = buf.length - off - 8;
      }
      return size / byteRate;
    }
    off += 8 + size + (size % 2);
  }
  throw new Error("no data chunk");
}

function fixWavHeader(buf: Buffer): Buffer {
  const out = Buffer.from(buf);
  let off = 12;
  while (off + 8 <= out.length) {
    const id = out.toString("ascii", off, off + 4);
    const size = out.readUInt32LE(off + 4);
    if (id === "data") {
      const actualData = out.length - (off + 8);
      out.writeUInt32LE(actualData, off + 4);
      out.writeUInt32LE(out.length - 8, 4);
      break;
    }
    off += 8 + size + (size % 2);
  }
  return out;
}

async function speak(key: string, text: string): Promise<Buffer> {
  const url = `https://api.deepgram.com/v1/speak?model=${NARRATION_VOICE}&encoding=linear16&sample_rate=48000&container=wav`;
  for (let attempt = 1; ; attempt++) {
    const r = await fetch(url, {
      method: "POST",
      headers: {
        Authorization: `Token ${key}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ text }),
    });
    if (r.ok) return fixWavHeader(Buffer.from(await r.arrayBuffer()));
    if (attempt >= 3) {
      throw new Error(`Deepgram ${r.status}: ${(await r.text()).slice(0, 200)}`);
    }
    await new Promise((res) => setTimeout(res, 1200 * attempt));
  }
}

export interface TimedLine {
  file: string;
  text: string;
  startSec: number;
  startFrame: number;
  seconds: number;
  frames: number;
}

export interface SceneTiming {
  id: SceneId;
  durationInFrames: number;
  durationSec: number;
  lines: TimedLine[];
}

export interface TimingManifest {
  fps: number;
  transitionFrames: number;
  totalDurationInFrames: number;
  totalDurationSec: number;
  voice: string;
  scenes: Record<SceneId, SceneTiming>;
  order: SceneId[];
}

async function main() {
  fs.mkdirSync(VO_DIR, { recursive: true });
  fs.mkdirSync(path.dirname(OUT_TIMING), { recursive: true });

  const key = loadEnvKey();
  const cache: Record<string, string> = fs.existsSync(CACHE_PATH)
    ? JSON.parse(fs.readFileSync(CACHE_PATH, "utf8"))
    : {};

  const scenes = {} as Record<SceneId, SceneTiming>;
  const order: SceneId[] = [];

  for (const scene of NARRATION) {
    let t = scene.lead;
    const lines: TimedLine[] = [];

    for (const [i, line] of scene.lines.entries()) {
      const file = `${scene.id}-${i + 1}.wav`;
      const wavPath = path.join(VO_DIR, file);
      const say = line.say ?? line.text;
      const hash = createHash("sha256")
        .update(`${NARRATION_VOICE}|${say}`)
        .digest("hex")
        .slice(0, 16);

      let buf: Buffer;
      if (cache[file] === hash && fs.existsSync(wavPath)) {
        buf = fs.readFileSync(wavPath);
      } else {
        buf = await speak(key, say);
        fs.writeFileSync(wavPath, buf);
        cache[file] = hash;
        console.log(`spoke ${file} (${NARRATION_VOICE})`);
      }

      const seconds = Number(wavSeconds(buf).toFixed(3));
      const startFrame = Math.round(t * FPS);
      const frames = Math.ceil(seconds * FPS);
      lines.push({
        file: `vo/${file}`,
        text: line.text,
        startSec: Number(t.toFixed(3)),
        startFrame,
        seconds,
        frames,
      });
      t += seconds + GAP;
    }

    const totalSec = t - GAP + scene.tail;
    const durationInFrames = Math.ceil(totalSec * FPS);
    scenes[scene.id] = {
      id: scene.id,
      durationInFrames,
      durationSec: Number((durationInFrames / FPS).toFixed(2)),
      lines,
    };
    order.push(scene.id);
    console.log(
      `${scene.id.padEnd(10)} ${scenes[scene.id].durationSec
        .toFixed(1)
        .padStart(5)}s  [${lines.map((l) => `${l.seconds.toFixed(1)}s`).join(" + ")}]`
    );
  }

  const sumFrames = order.reduce((acc, id) => acc + scenes[id].durationInFrames, 0);
  const totalDurationInFrames = sumFrames - TRANSITION_FRAMES * (order.length - 1);

  const manifest: TimingManifest = {
    fps: FPS,
    transitionFrames: TRANSITION_FRAMES,
    totalDurationInFrames,
    totalDurationSec: Number((totalDurationInFrames / FPS).toFixed(2)),
    voice: NARRATION_VOICE,
    scenes,
    order,
  };

  fs.writeFileSync(CACHE_PATH, JSON.stringify(cache, null, 2));
  fs.writeFileSync(OUT_TIMING, JSON.stringify(manifest, null, 2));
  console.log(
    `\nTotal composition: ${manifest.totalDurationSec}s (${totalDurationInFrames} frames @ ${FPS}fps, voice=${NARRATION_VOICE})`
  );
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
