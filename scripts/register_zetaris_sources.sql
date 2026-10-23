-- ============================================================================
-- Switchyard: Zetaris Lightning SQL Onboarding Script
-- File: scripts/register_zetaris_sources.sql
-- Run each statement ONE AT A TIME in the Zetaris SQL Editor (http://localhost:3000)
-- or via POST http://localhost:8888/api/v1.0/sql-editor/sqls/run
-- ============================================================================

-- 1. Create theUnified SchemaStore Container for Switchyard
CREATE SCHEMASTORE CONTAINER switchyard;

-- 2. Register Live Carrier & Customs Telemetry REST Source
CREATE LIGHTNING DATABASE SWITCHYARD_REST
DESCRIBE BY "Live Carrier, Customs, and Cold-Chain Telemetry REST Source";

-- 3. Register Carrier Telemetry REST Table in Zetaris
CREATE LIGHTNING REST TABLE carrier_port_feeds
FROM SWITCHYARD_REST
REQUEST (
    endpoint "http://host.docker.internal:8050/api/mock-carrier-feed",
    method "get",
    response_type "json",
    http_encoding "URLENCODED"
)
HEADER ()
BODY ();

-- 4. Register Starter PokeAPI Validation Table (per Participant Setup Guide 1.8)
CREATE LIGHTNING DATABASE POKEAPI_REST
DESCRIBE BY "PokeAPI REST source for setup verification";

CREATE SCHEMASTORE CONTAINER pokeapi;

CREATE LIGHTNING REST TABLE pikachu_facts
FROM POKEAPI_REST
REQUEST (
    endpoint "https://pokeapi.co/api/v2/pokemon/pikachu",
    method "get",
    response_type "json",
    http_encoding "URLENCODED"
)
HEADER ()
BODY ();

-- 5. Create Unified Semantic Layer (USL) Views in Switchyard Container
CREATE SCHEMASTORE VIEW erp_purchase_orders
WITH CONTAINER switchyard AS
SELECT
    po_number,
    sku,
    part_name,
    production_line,
    supplier_id,
    supplier_name,
    ordered_qty,
    unit_cost_usd,
    erp_status,
    promised_eta,
    incoterms,
    buyer_notes
FROM zetaris_erp.purchase_orders;

CREATE SCHEMASTORE VIEW wms_inventory_ledger
WITH CONTAINER switchyard AS
SELECT
    ledger_id,
    po_number,
    sku,
    production_line,
    received_qty,
    usable_unrestricted_qty,
    quarantined_qty,
    in_transit_deficit_qty,
    lot_code,
    dock_location,
    hourly_line_burn_rate,
    line_runway_hours,
    downtime_cost_per_hour_usd,
    last_scan_utc,
    warehouse_note
FROM zetaris_wms.inventory_ledger;

CREATE SCHEMASTORE VIEW qms_incident_tickets
WITH CONTAINER switchyard AS
SELECT
    ticket_id,
    po_number,
    sku,
    supplier_id,
    lot_code,
    severity,
    qms_status,
    defect_rate_pct,
    failure_mode,
    sublot_breakdown,
    supplier_dispute_claim,
    lab_verdict,
    inspector_action_required
FROM zetaris_qms.incident_tickets;
