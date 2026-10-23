import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SR = 48000;

function writeWav(file: string, left: Float32Array, right?: Float32Array) {
  const r = right ?? left;
  const n = left.length;
  const dataSize = n * 4;
  const buf = Buffer.alloc(44 + dataSize);
  buf.write("RIFF", 0);
  buf.writeUInt32LE(36 + dataSize, 4);
  buf.write("WAVE", 8);
  buf.write("fmt ", 12);
  buf.writeUInt32LE(16, 16);
  buf.writeUInt16LE(1, 20);
  buf.writeUInt16LE(2, 22);
  buf.writeUInt32LE(SR, 24);
  buf.writeUInt32LE(SR * 4, 28);
  buf.writeUInt16LE(4, 32);
  buf.writeUInt16LE(16, 34);
  buf.write("data", 36);
  buf.writeUInt32LE(dataSize, 40);
  for (let i = 0; i < n; i++) {
    const l = Math.max(-1, Math.min(1, left[i]));
    const rr = Math.max(-1, Math.min(1, r[i]));
    buf.writeInt16LE(Math.round(l * 32767), 44 + i * 4);
    buf.writeInt16LE(Math.round(rr * 32767), 44 + i * 4 + 2);
  }
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, buf);
}

let seed = 0x57c41a2d;
function rand() {
  seed = (seed * 1664525 + 1013904223) >>> 0;
  return seed / 0xffffffff - 0.5;
}

// 1. Whoosh — smooth filtered sweep + sub-harmonic glide (Hizz camera transition)
function genWhoosh(): [Float32Array, Float32Array] {
  const dur = 0.52;
  const n = Math.floor(SR * dur);
  const L = new Float32Array(n);
  const R = new Float32Array(n);
  let lpL = 0,
    lpR = 0,
    phase = 0;
  for (let i = 0; i < n; i++) {
    const t = i / n;
    const env = Math.sin(Math.PI * Math.pow(t, 0.78));
    const cutoff = 0.012 + 0.16 * Math.sin(Math.PI * t);
    lpL += cutoff * (rand() * 2 - lpL);
    lpR += cutoff * (rand() * 2 - lpR);
    const freq = 140 * Math.pow(0.42, t);
    phase += (2 * Math.PI * freq) / SR;
    const sub = Math.sin(phase) * 0.25 * env;
    const pan = 0.25 + 0.5 * t;
    L[i] = (lpL * 0.42 * (1 - pan * 0.45) + sub) * env * 0.55;
    R[i] = (lpR * 0.42 * (0.55 + pan * 0.45) + sub) * env * 0.55;
  }
  return [L, R];
}

// 2. Hit — deep cinematic sub impact + crystalline shimmer
function genHit(): [Float32Array, Float32Array] {
  const dur = 1.1;
  const n = Math.floor(SR * dur);
  const L = new Float32Array(n);
  const R = new Float32Array(n);
  let phase = 0;
  for (let i = 0; i < n; i++) {
    const t = i / SR;
    const freq = 42 + 96 * Math.exp(-t * 26);
    phase += (2 * Math.PI * freq) / SR;
    const body = Math.tanh(Math.sin(phase) * 1.65) * Math.exp(-t * 3.8);
    const click =
      (Math.sin(2 * Math.PI * 1320 * t) + rand() * 0.35) * Math.exp(-t * 85);
    const shimmerL = Math.sin(2 * Math.PI * 440 * t) * Math.exp(-t * 5.2) * 0.08;
    const shimmerR = Math.sin(2 * Math.PI * 659.25 * t) * Math.exp(-t * 5.2) * 0.08;
    L[i] = (body * 0.62 + click * 0.18 + shimmerL) * 0.72;
    R[i] = (body * 0.62 + click * 0.18 + shimmerR) * 0.72;
  }
  return [L, R];
}

// 3. Pop — glass card entrance chime
function genPop(): [Float32Array, Float32Array] {
  const dur = 0.16;
  const n = Math.floor(SR * dur);
  const L = new Float32Array(n);
  const R = new Float32Array(n);
  let p1 = 0,
    p2 = 0;
  for (let i = 0; i < n; i++) {
    const t = i / SR;
    const f1 = 587.33 + 220 * Math.exp(-t * 60); // D5
    const f2 = 880.0; // A5
    p1 += (2 * Math.PI * f1) / SR;
    p2 += (2 * Math.PI * f2) / SR;
    const s =
      (Math.sin(p1) * 0.65 + Math.sin(p2) * 0.35) *
      Math.exp(-t * 28) *
      0.28;
    L[i] = s * 0.96;
    R[i] = s * 1.04;
  }
  return [L, R];
}

// 4. Key — subtle data tick
function genKey(): [Float32Array, Float32Array] {
  const dur = 0.045;
  const n = Math.floor(SR * dur);
  const L = new Float32Array(n);
  const R = new Float32Array(n);
  let lp = 0;
  for (let i = 0; i < n; i++) {
    const t = i / SR;
    lp += 0.28 * (rand() - lp);
    const body = Math.sin(2 * Math.PI * 1950 * t) * Math.exp(-t * 140);
    const s = (lp * Math.exp(-t * 190) * 0.6 + body * 0.4) * 0.22;
    L[i] = s;
    R[i] = s * 0.94;
  }
  return [L, R];
}

// 5. Pulse — bezier node electric pulse
function genPulse(): [Float32Array, Float32Array] {
  const dur = 0.38;
  const n = Math.floor(SR * dur);
  const L = new Float32Array(n);
  const R = new Float32Array(n);
  for (let i = 0; i < n; i++) {
    const t = i / SR;
    const env = Math.sin(Math.PI * (t / dur)) * Math.exp(-t * 4.5);
    const carrier =
      Math.sin(2 * Math.PI * 523.25 * t) * 0.5 +
      Math.sin(2 * Math.PI * 783.99 * t) * 0.35 +
      Math.sin(2 * Math.PI * 1046.5 * t) * 0.15;
    L[i] = carrier * env * 0.24;
    R[i] = carrier * env * 0.26;
  }
  return [L, R];
}

// 6. Hizz-inspired Dark Electronic Synth & Sub-Bass Bed (D minor9 / Bb maj7 / G min9 / A7sus4)
// Driving 116 BPM subtle pulse + warm analog pad + crystalline high arp
function genMusicBed(durationSec = 110): [Float32Array, Float32Array] {
  const n = Math.floor(SR * durationSec);
  const L = new Float32Array(n);
  const R = new Float32Array(n);

  const chords: number[][] = [
    [73.42, 146.83, 220.0, 261.63, 329.63], // Dm9
    [58.27, 116.54, 174.61, 220.0, 293.66], // Bbmaj7
    [49.0, 98.0, 146.83, 196.0, 261.63], // Gm9
    [55.0, 110.0, 164.81, 220.0, 293.66], // A7sus4
  ];
  const arpNotes: number[][] = [
    [587.33, 659.25, 880.0, 659.25, 523.25, 440.0, 523.25, 587.33],
    [466.16, 587.33, 698.46, 587.33, 523.25, 440.0, 466.16, 523.25],
    [392.0, 523.25, 587.33, 698.46, 587.33, 523.25, 440.0, 392.0],
    [440.0, 523.25, 659.25, 783.99, 659.25, 587.33, 523.25, 440.0],
  ];

  const chordLen = 6.0; // seconds per bar
  const stepSec = chordLen / 16; // 16th-note pulse (~0.375s)

  for (let i = 0; i < n; i++) {
    const t = i / SR;
    const pos = t / chordLen;
    const idx = Math.floor(pos) % chords.length;
    const nextIdx = (idx + 1) % chords.length;
    const frac = pos - Math.floor(pos);
    const xfade =
      frac > 0.84 ? 0.5 - 0.5 * Math.cos(((frac - 0.84) / 0.16) * Math.PI) : 0;

    let sL = 0,
      sR = 0;

    // Warm pad + sub bass
    const cA = chords[idx];
    const cB = chords[nextIdx];
    for (let v = 0; v < cA.length; v++) {
      const fA = cA[v];
      const fB = cB[v];
      const amp = v === 0 ? 0.36 : 0.13 / Math.sqrt(v);
      const detune = 1 + 0.0016 * Math.sin(0.27 * t + v);
      const aL =
        Math.sin(2 * Math.PI * fA * t) +
        0.28 * Math.sin(2 * Math.PI * fA * 2 * t) * 0.25;
      const aR =
        Math.sin(2 * Math.PI * fA * detune * t + 0.35 * v) +
        0.28 * Math.sin(2 * Math.PI * fA * 2 * detune * t) * 0.25;
      const bL =
        Math.sin(2 * Math.PI * fB * t) +
        0.28 * Math.sin(2 * Math.PI * fB * 2 * t) * 0.25;
      const bR =
        Math.sin(2 * Math.PI * fB * detune * t + 0.35 * v) +
        0.28 * Math.sin(2 * Math.PI * fB * 2 * detune * t) * 0.25;
      sL += amp * (aL * (1 - xfade) + bL * xfade);
      sR += amp * (aR * (1 - xfade) + bR * xfade);
    }

    // Driving electronic sub-pulse + soft crystalline arp (Hizz signature feel)
    const stepIdx = Math.floor(t / stepSec);
    const stepT = t - stepIdx * stepSec;
    const pulseEnv = Math.exp(-stepT * 11.5) * (1 - Math.exp(-stepT * 140));
    const subRoot = cA[0];
    const bassPulse =
      Math.tanh(Math.sin(2 * Math.PI * subRoot * 2 * t) * 1.3) *
      pulseEnv *
      0.16;

    const arpNote = arpNotes[idx][stepIdx % 8];
    const arpEnv = Math.exp(-stepT * 14.0) * (1 - Math.exp(-stepT * 180));
    const arpPan = stepIdx % 2 === 0 ? 0.7 : 0.3;
    const arpSig = Math.sin(2 * Math.PI * arpNote * t) * arpEnv * 0.065;

    sL += bassPulse + arpSig * arpPan;
    sR += bassPulse + arpSig * (1 - arpPan);

    const fadeIn = Math.min(1, t / 1.5);
    const fadeOut = Math.min(1, (durationSec - t) / 2.5);
    const master = 0.28 * fadeIn * fadeOut;
    L[i] = Math.tanh(sL * 0.85) * master;
    R[i] = Math.tanh(sR * 0.85) * master;
  }
  return [L, R];
}

const pub = path.resolve(__dirname, "../public");
writeWav(path.join(pub, "sfx/whoosh.wav"), ...genWhoosh());
writeWav(path.join(pub, "sfx/hit.wav"), ...genHit());
writeWav(path.join(pub, "sfx/pop.wav"), ...genPop());
writeWav(path.join(pub, "sfx/key.wav"), ...genKey());
writeWav(path.join(pub, "sfx/pulse.wav"), ...genPulse());
writeWav(path.join(pub, "music/bed.wav"), ...genMusicBed(175));
console.log("Synthesized Hizz-style SFX + 175s electronic music bed in public/");
