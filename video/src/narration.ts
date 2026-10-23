export type SceneId = "open" | "zetaris" | "engines" | "nemotron" | "outro";

export interface Line {
  text: string;
  say?: string;
}

export interface SceneScript {
  id: SceneId;
  lead: number;
  tail: number;
  lines: Line[];
}

export const NARRATION_VOICE = "aura-2-thalia-en";

export const NARRATION: SceneScript[] = [
  {
    id: "open",
    lead: 0.6,
    tail: 0.8,
    lines: [
      {
        text: "In high-value manufacturing, enterprise systems constantly disagree.",
      },
      {
        text: "Your ERP says 4,000 silicon-carbide power modules on PO-8841 shipped on time.",
        say: "Your E.R.P. says four thousand silicon-carbide power modules on P.O. eighty-eight forty-one shipped on time.",
      },
      {
        text: "But warehouse dock scans show only 350 usable units, quality control quarantined 800 for solder voids, and ocean telemetry reports a 96-hour customs hold.",
        say: "But warehouse dock scans show only three hundred and fifty usable units, quality control quarantined eight hundred for solder voids, and ocean telemetry reports a ninety-six hour customs hold.",
      },
      {
        text: "Meet Switchyard: an autonomous multi-agent reconciliation system that resolves cross-system conflicts before a $64,000/hr factory line stops.",
        say: "Meet Switchyard. An autonomous multi-agent reconciliation system that resolves cross-system conflicts before a sixty-four thousand dollar per hour factory line stops.",
      },
    ],
  },
  {
    id: "zetaris",
    lead: 0.45,
    tail: 0.75,
    lines: [
      {
        text: "Layer One is the Zetaris Data Harness.",
      },
      {
        text: "Instead of brittle ETL pipelines, Switchyard queries ERP purchase orders, warehouse inventory ledgers, quality tickets, and live carrier feeds through single-statement Zetaris Lightning SQL.",
        say: "Instead of brittle E.T.L. pipelines, Switchyard queries E.R.P. purchase orders, warehouse inventory ledgers, quality tickets, and live carrier feeds through single-statement Zetaris Lightning S.Q.L.",
      },
      {
        text: "Every query carries a fresh request UUID and maps conflicting records directly into a live provenance graph.",
        say: "Every query carries a fresh request U.U.I.D., and maps conflicting records directly into a live provenance graph.",
      },
    ],
  },
  {
    id: "engines",
    lead: 0.45,
    tail: 0.75,
    lines: [
      {
        text: "Layer Two runs all four Meterless Engines inside a non-linear adversarial loop.",
      },
      {
        text: "When the Reconciler proposes a partial answer in Round One, the Conflict Critic rejects it for missing acoustic lab evidence and forces a targeted Round Two SQL re-query.",
        say: "When the Reconciler proposes a partial answer in Round One, the Conflict Critic rejects it for missing acoustic lab evidence, and forces a targeted Round Two S.Q.L. re-query.",
      },
      {
        text: "Scout Intent routes each task by blast radius, World Model enforces optimistic concurrency across 15 state transitions, Markovian compresses context tokens by 84%, and H-MEM commits supplier precedents across sessions.",
        say: "Scout Intent routes each task by blast radius. World Model enforces optimistic concurrency across fifteen state transitions. Markovian compresses context tokens by eighty-four percent, and H-Mem commits supplier precedents across sessions.",
      },
    ],
  },
  {
    id: "nemotron",
    lead: 0.45,
    tail: 0.75,
    lines: [
      {
        text: "Layer Three powers every agent through Meterless Nightshift on port 8088 using dual NVIDIA Nemotron lanes.",
        say: "Layer Three powers every agent through Meterless Nightshift on port eighty-eighty-eight, using dual NVIDIA Nemotron lanes.",
      },
      {
        text: "Nemotron 3.5 Lightning 30B handles low-latency SQL discovery, while Nemotron 3.5 Super 120B executes deep adversarial critique and policy verification, logging cryptographic model receipts on every turn.",
        say: "Nemotron three point five Lightning thirty-B handles low-latency S.Q.L. discovery, while Nemotron three point five Super one-twenty-B executes deep adversarial critique and policy verification, logging cryptographic model receipts on every turn.",
      },
    ],
  },
  {
    id: "outro",
    lead: 0.45,
    tail: 1.8,
    lines: [
      {
        text: "Once all three conflicts are corroborated, Switchyard issues a sourced remediation order: releasing 350 verified units, rejecting the defective sub-lot, and splitting a 3,650-unit emergency order across Silicore Dresden and Pacific Semi.",
        say: "Once all three conflicts are corroborated, Switchyard issues a sourced remediation order: releasing three hundred and fifty verified units, rejecting the defective sub-lot, and splitting a three thousand six hundred and fifty unit emergency order across Silicore Dresden and Pacific Semi.",
      },
      {
        text: "Total impact: 85 hours of downtime prevented and $5.42M saved.",
        say: "Total impact: eighty-five hours of downtime prevented, and five point four two million dollars saved.",
      },
      {
        text: "Switchyard. Reconcile reality before line-down.",
      },
    ],
  },
];
