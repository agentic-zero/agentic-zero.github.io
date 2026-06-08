# SOP — Pack Product (MTO)
**Process ID:** SCOR-D2.10
**Framework:** SCOR | **Domain:** Deliver
**Generated:** 2026-06-07

## Purpose
Process of packing MTO products for shipment including final packaging, customer-specific labeling, packing list generation and seal/close

## Triggers
- SCOR-D2.9 completion event with picked products ready
- availability of PackingSpecification and ShipmentDocumentation

## Inputs Required
- picked products
- packing specifications
- labels
- packing materials
- shipment documentation

## Process Steps
1. IF product contains dangerous goods THEN apply dangerous goods packaging rules and add ComplianceFlag
2. IF customer packaging standards exist THEN enforce them before sealing
3. IF GxP flag is true THEN require pharma-compliant labeling and audit trail

## Expected Outputs
- packed shipments
- packing lists
- shipment labels
- sealed packages

## Business Rules
- packing_accuracy >= 99.5%
- label_compliance_rate == 100%
- all SealedPackage must include ShipmentLabel and PackingList
- GDPR shipment data must be encrypted and logged

## Exception Handling
- Missing picked products: halt process and trigger SCOR-D2.9 retry
- Non-compliant label: regenerate Label and re-apply before sealing
- Damage detected during packing: quarantine product and log damage_rate incident

## Success Criteria
- All outputs (PackedShipment, PackingList, ShipmentLabel, SealedPackage) generated
- KPIs meet thresholds: packing_accuracy >= 99.5, label_compliance_rate == 100, damage_rate == 0
- Process completes within packing_cycle_time SLA

## Compliance Requirements
- dangerous goods packaging
- GxP if pharma
- customer packaging standards
- GDPR shipment data