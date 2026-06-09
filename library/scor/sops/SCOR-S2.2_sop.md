# SOP — Receive Product (MTO)
**Process ID:** SCOR-S2.2
**Framework:** SCOR | **Domain:** Source
**Generated:** 2026-06-08

## Purpose
Process of receiving, inspecting and verifying MTO materials against purchase orders and quality specifications before releasing to production

## Triggers
- ASN or delivery notification received matching open PurchaseOrder
- Scheduled receipt date/time from DeliverySchedule reached

## Inputs Required
- delivery schedule
- purchase orders
- quality specifications
- receiving dock capacity
- inspection criteria

## Process Steps
1. IF all line items match PurchaseOrder AND pass InspectionCriteria THEN generate GoodsReceiptConfirmation ELSE create DiscrepancyAlert
2. IF QualityInspectionReport status == PASS THEN trigger InventoryUpdate ELSE hold material and notify procurement

## Expected Outputs
- goods receipt confirmation
- quality inspection report
- inventory update
- discrepancy alerts

## Business Rules
- Every MTO receipt must validate quantity and specs against PurchaseOrder before any InventoryUpdate
- Inspection must complete within inspection criteria before goods receipt confirmation is issued
- Receiving dock capacity must not be exceeded without rescheduling

## Exception Handling
- Quantity or spec mismatch: create DiscrepancyAlert, quarantine material, block InventoryUpdate until resolution
- Dock capacity exceeded: reject delivery or reroute to overflow staging and update DeliverySchedule

## Success Criteria
- receiving_accuracy == 100% (zero discrepancies)
- inspection_cycle_time <= defined SLA
- goods_receipt_on_time_rate >= 98%

## Compliance Requirements
- GxP receiving if pharma
- ISO 9001 incoming inspection
- GDPR if personal data in records