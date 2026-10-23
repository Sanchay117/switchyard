### Executive Summary & Sourced Verdict (`PO-8960` / `HV-CONT-400A`)

- **Disruption Status:** ERP claims `PO-8960` (**3,200 units** from **Apex Wafer Corp**) is `DELIVERED_COMPLETE` with ETA `2026-10-21` (`[zetaris_erp.purchase_orders#PO-8960]`). Cross-system reconciliation through **Zetaris** proves this status is false.
- **Physical Reality:** Warehouse dock telemetry (`[zetaris_wms.inventory_ledger#WMS-705]`) shows only **2,100 unrestricted units** available (35.0h runway on **Line-B Inverter** at 60 units/hr burn rate), **0 units quarantined** in `LOT-998B`, and **1,100 units missing/delayed**.
- **Transit & Quality Root Cause:** Live carrier telemetry (`[zetaris_rest.carrier_port_feeds#CAR-905]`) confirms `PARTIAL_MANIFEST_DISPATCHED` (**+72h delay**, revised ETA `2026-10-26T19:00:00Z`: *Air waybill AWB-29910 shows 7 pallets (2100 units) loaded; remaining 4 pallets (1100 units) rolled to flight BR-0624 on Oct 26*). Meanwhile, QMS lab report (`[zetaris_qms.incident_tickets#QMS-435]`) establishes: *Received 2100 units are conforming; 1100 units are missing and unshipped* (2100 units physically verified and passed hi-pot insulation test; 1100 units never left Kaohsiung warehouse).

### Actionable Remediation Order

1. **Dock & Quarantine Disposition (`[zetaris_qms.incident_tickets#QMS-435]`):** Issue debit memo for 1100 phantom units, correct ERP inventory by -1100, and place bridge order with SUP-140.
2. **Supply Continuity & Backup Allocation (`1,100 unit shortfall`):**
  - **Issue Emergency Split PO to Schaltbau Munich AG (`[zetaris_erp.qualified_suppliers#SUP-140]`):** Order **1,100 units** of `HV-CONT-400A` at **$31.00/unit** (2-day air lead time, total spend **$34,100.00**, expedite premium **+$3,960.00**).
3. **Financial & Runway Protection (`[switchyard.risk_calculator#RISK-PO-8960]`):** Prevents **37.0 hours** of downtime on **Line-B Inverter** (**$2,368,000** gross loss avoided for **$3,960.00** expedite premium; **net savings: $2,364,040**).
4. **Cross-Session Memory (`[H-MEM#HMEM-PREC-004]`):** Precedent committed to Meterless H-MEM for future sessions involving `Apex Wafer Corp`.

### Confidence & Limitations
- **Confidence Score:** `0.96` (3/3 cross-source conflicts resolved with 3-way corroboration across Zetaris ERP, WMS, QMS, and Carrier REST tables).
- **Known Limitations:** Backup allocation lead times assume immediate customs release on air-charter lanes and standard incoming lot acceptance.