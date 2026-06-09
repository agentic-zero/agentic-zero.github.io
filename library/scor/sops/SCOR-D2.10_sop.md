# SOP — Pack Product (MTO)
**Process ID:** SCOR-D2.10
**Framework:** SCOR | **Domain:** Deliver
**Generated:** 2026-06-08

## Purpose
Process of packing MTO products for shipment including final packaging, customer-specific labeling, packing list generation and seal/close

## Triggers
- SCOR-D2.9 completion event with picked products payload
- availability of packing specifications and labels in staging queue

## Inputs Required
- picked products
- packing specifications
- labels
- packing materials
- shipment documentation

## Process Steps
1. IF product contains hazardous material THEN apply dangerous goods packaging and add compliance label
2. IF customer packaging standard exists THEN override default packing spec
3. IF quantity mismatch between picked items and order THEN halt and trigger inventory reconciliation

## Expected Outputs
- packed shipments
- packing lists
- shipment labels
- sealed packages

## Business Rules
- packing_accuracy must be >= 99.5% verified by barcode scan
- label_compliance_rate must satisfy GDPR and customer standards before sealing
- all sealed packages must include packing list and shipment label
- GxP pharma products require dual verification signature

## Exception Handling
- damaged picked item: quarantine item, log damage_rate, request replacement from SCOR-D2.9
- missing label data: auto-generate from shipment documentation or escalate to order management
- cycle_time exceeds threshold: flag for process review and notify supervisor

## Success Criteria
- all outputs (PackedShipment, PackingList, ShipmentLabel, SealedPackage) created with matching IDs
- KPIs within thresholds: packing_accuracy >= 99.5, label_compliance_rate = 100, damage_rate <= 0.1, cycle_time <= SLA
- no open exceptions logged

## Compliance Requirements
- dangerous goods packaging
- GxP if pharma
- customer packaging standards
- GDPR shipment data