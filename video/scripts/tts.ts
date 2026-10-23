import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { NARRATION, NARRATION_VOICE, SceneId } from "../src/narration";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");

function loadEnvKey(): string | undefined {
  if (process.env.DEEPGRAM_API_KEY) return process.env.DEEPGRAM_API_KEY;
  const candidates = [
    path.resolve(ROOT, "../.env"),
    path.resolve(ROOT, "../../Strike/.env"),
  ];
  for (const envPath of candidates) {
    if (fs.existsSync(envPath)) {
      for (const line of fs.readFileSync(envPath, "utf8").split("\n")) {
        const m = line.match(/^\s*DEEPGRAM_API_KEY\s*=\s*(.+?)\s*$/);
        if (m) return m[1].replace(/^["']|["']$/g, "");
      }
    }
  }
  return undefined;
}

const VO_DIR = path.join(ROOT, "public/vo");
const OUT_TIMING = path.join(ROOT, "src/generated/timing.json");
const FPS = 30;
const TRANSITION_FRAMES = 14;

function wavDurationSec(buf: Buffer): number {
  let offset = 12;
  let byteRate = 48000 * 2;
  let dataBytes = buf.length - 44;
  while (offset + 8 <= buf.length) {
    const id = buf.toString("ascii", offset, offset + 4);
    const size = buf.readUInt32LE(offset + 4);
    if (id === "fmt ") {
      byteRate = buf.readUInt32LE(offset + 8 + 8);
    } else if (id === "data") {
      dataBytes = size > 0 && size <= buf.length - offset - 8 ? size : buf.length - (offset + 8);
      break;
    }
    offset += 8 + size + (size % 2);
  }
  return dataBytes / byteRate;
}

function fixWavHeader(buf: Buffer): Buffer {
  const out = Buffer.from(buf);
  let offset = 12;
  while (offset + 8 <= out.length) {
    const id = out.toString("ascii", offset, offset + 4);
    const size = out.readUInt32LE(offset + 4);
    if (id === "data") {
      const actualData = out.length - (offset + 8);
      out.writeUInt32LE(actualData, offset + 4);
      out.writeUInt32LE(out.length - 8, 4);
      break;
    }
    offset += 8 + size + (size % 2);
  }
  return out;
}

async function synthDeepgram(text: string, apiKey: string): Promise<Buffer> {
  const url = `https://api.deepgram.com/v1/speak?model=${encodeURIComponent(
    NARRATION_VOICE
  )}&encoding=linear16&sample_rate=48000&container=wav`;
  const res = await fetch(url, {
    method: "POST",
    headers: {
      Authorization: `Token ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`Deepgram TTS ${res.status}: ${body}`);
  }
  const raw = Buffer.from(await res.arrayBuffer());
  return fixWavHeader(raw);
}

function synthLocalSay(text: string, wavPath: string): Buffer {
  const tmpAiff = `${wavPath}.tmp.aiff`;
  execFileSync("/usr/bin/say", ["-r", "188", "-o", tmpAiff, text]);
  execFileSync("/opt/homebrew/bin/ffmpeg", [
    "-y",
    "-i",
    tmpAiff,
    "-ar",
    "48000",
    "-ac",
    "1",
    "-c:a",
    "pcm_s16le",
    wavPath,
  ]);
  if (fs.existsSync(tmpAiff)) fs.unlinkSync(tmpAiff);
  return fs.readFileSync(wavPath);
}

export interface SceneTiming {
  id: SceneId;
  text: string;
  audioFile: string;
  voDurationSec: number;
  voStartFrame: number;
  durationInFrames: number;
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

  const apiKey = loadEnvKey();
  const scenes = {} as Record<SceneId, SceneTiming>;
  const order: SceneId[] = [];

  for (const seg of NARRATION) {
    const wavPath = path.join(VO_DIR, `${seg.id}.wav`);
    const hashPath = path.join(VO_DIR, `${seg.id}.txt`);
    const cacheKey = `${NARRATION_VOICE}::${seg.text}`;
    let buf: Buffer;

    if (
      fs.existsSync(wavPath) &&
      fs.existsSync(hashPath) &&
      fs.readFileSync(hashPath, "utf8") === cacheKey
    ) {
      buf = fs.readFileSync(wavPath);
      console.log(`cached  ${seg.id}.wav`);
    } else if (apiKey) {
      console.log(`synth   ${seg.id}.wav (${seg.text.length} chars via Deepgram Aura-2)`);
      buf = await synthDeepgram(seg.text, apiKey);
      fs.writeFileSync(wavPath, buf);
      fs.writeFileSync(hashPath, cacheKey);
    } else {
      console.log(`synth   ${seg.id}.wav (local fallback)`);
      buf = synthLocalSay(seg.text, wavPath);
      fs.writeFileSync(hashPath, cacheKey);
    }

    const voDur = wavDurationSec(buf);
    const totalSec = seg.visualLeadSec + voDur + seg.visualTailSec;
    const durationInFrames = Math.ceil(totalSec * FPS);
    const voStartFrame = Math.round(seg.visualLeadSec * FPS);

    scenes[seg.id] = {
      id: seg.id,
      text: seg.text,
      audioFile: `vo/${seg.id}.wav`,
      voDurationSec: Number(voDur.toFixed(3)),
      voStartFrame,
      durationInFrames,
    };
    order.push(seg.id);
    console.log(
      `        vo=${voDur.toFixed(2)}s  scene=${(durationInFrames / FPS).toFixed(2)}s (${durationInFrames}f)`
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

  fs.writeFileSync(OUT_TIMING, JSON.stringify(manifest, null, 2));
  console.log(
    `\nTotal composition: ${manifest.totalDurationSec}s (${totalDurationInFrames} frames @ ${FPS}fps)`
  );
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
