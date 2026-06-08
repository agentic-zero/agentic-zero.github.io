# SOP — Receive Product (MTO)
**Process ID:** SCOR-S2.2
**Framework:** SCOR | **Domain:** Source
**Generated:** 2026-06-07

## Purpose
Process of receiving, inspecting and verifying MTO materials against purchase orders and quality specifications before releasing to production

## Triggers
- ASN or delivery notification received from supplier
- Physical truck arrival logged at receiving dock via RFID/scan

## Inputs Required
- delivery schedule
- purchase orders
- quality specifications
- receiving dock capacity
- inspection criteria

## Process Steps
1. IF received quantity matches PurchaseOrder AND passes InspectionCriteria THEN create GoodsReceiptConfirmation ELSE create DiscrepancyAlert
2. IF ReceivingDock capacity exceeded THEN queue delivery and log delay
3. IF quality rejection rate > threshold THEN quarantine batch and notify supplier

## Expected Outputs
- goods receipt confirmation
- quality inspection report
- inventory update
- discrepancy alerts

## Business Rules
- GoodsReceiptConfirmation must be created within 4 hours of physical arrival
- QualityInspectionReport must reference ISO 9001 criteria and GxP rules if pharma sector
- All data fields in DiscrepancyAlert must be logged with timestamp and user_id for GDPR compliance
- InventoryUpdate must be atomic and rollback on failure

## Exception Handling
- Partial delivery: create partial GoodsReceiptConfirmation, flag remaining quantity in DeliverySchedule, and generate backorder alert
- Damaged goods: bypass normal inspection, create immediate DiscrepancyAlert with photo evidence, and quarantine batch

## Success Criteria
- GoodsReceiptConfirmation created with 100% match to PurchaseOrder
- QualityInspectionReport completed within KPI inspection_cycle_time
- InventoryUpdate posted with zero discrepancy and receiving_accuracy >= 99.5%

## Compliance Requirements
- GxP receiving if pharma
- ISO 9001 incoming inspection
- GDPR if personal data in records