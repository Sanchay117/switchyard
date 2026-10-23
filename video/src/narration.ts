export type SceneId = "open" | "zetaris" | "engines" | "nemotron" | "outro";

export interface NarrationSegment {
  id: SceneId;
  text: string;
  visualLeadSec: number;
  visualTailSec: number;
}

export const NARRATION_VOICE = "aura-2-apollo-en";

export const NARRATION: NarrationSegment[] = [
  {
    id: "open",
    text: "In high-value manufacturing, enterprise systems constantly disagree. Your ERP says four thousand silicon-carbide power modules shipped on time. But warehouse dock scans show only three hundred fifty usable units, quality control quarantined eight hundred for solder voids, and ocean telemetry reports a ninety-six hour customs hold. Meet Switchyard: an autonomous multi-agent reconciliation system that resolves cross-system conflicts before a sixty-four thousand dollar per hour factory line stops.",
    visualLeadSec: 0.4,
    visualTailSec: 0.7,
  },
  {
    id: "zetaris",
    text: "Layer One is the Zetaris Data Harness. Instead of brittle point-to-point ETL, Switchyard queries ERP purchase orders, warehouse inventory ledgers, quality incident tickets, and live carrier feeds through single-statement Zetaris Lightning SQL. Every query carries a fresh request UUID and maps conflicting records directly into a live provenance graph.",
    visualLeadSec: 0.35,
    visualTailSec: 0.65,
  },
  {
    id: "engines",
    text: "Layer Two runs all four Meterless Engines inside a non-linear adversarial loop. When the Reconciler proposes a partial answer in Round One, the Conflict Critic rejects it for missing acoustic lab evidence and forces a targeted Round Two SQL re-query. Scout Intent routes each task by blast radius, World Model enforces optimistic concurrency across fifteen state transitions, Markovian capsules compress context tokens by eighty-four percent, and H-MEM recalls and commits supplier precedents across sessions.",
    visualLeadSec: 0.35,
    visualTailSec: 0.65,
  },
  {
    id: "nemotron",
    text: "Layer Three powers every agent through Meterless Nightshift on port eighty-eighty-eight using dual NVIDIA Nemotron lanes. Nemotron Three-Point-Five Lightning Thirty-B handles low-latency SQL planning and discovery, while Nemotron Three-Point-Five Super One-Twenty-B executes deep adversarial critique and policy verification, logging cryptographic model receipts on every turn.",
    visualLeadSec: 0.35,
    visualTailSec: 0.65,
  },
  {
    id: "outro",
    text: "Once all three conflicts are corroborated, Switchyard issues a sourced remediation order: releasing three hundred fifty verified units, rejecting the defective sub-lot, and splitting a three thousand six hundred fifty unit emergency order across Silicore Dresden and Pacific Semi. Total impact: eighty-five hours of downtime prevented and five point four million dollars saved. Switchyard: reconcile reality before line-down.",
    visualLeadSec: 0.35,
    visualTailSec: 1.2,
  },
];
