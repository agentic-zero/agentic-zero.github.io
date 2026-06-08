# SOP — Pick Product (MTO)
**Process ID:** SCOR-D2.9
**Framework:** SCOR | **Domain:** Deliver
**Generated:** 2026-06-07

## Purpose
Process of picking MTO finished goods from staging or warehouse locations for outbound shipment preparation

## Triggers
- PickList released from SCOR-D2.8
- OrderDocumentation status == released

## Inputs Required
- pick lists
- staging locations
- order documentation
- picking equipment
- scan systems

## Process Steps
1. IF scan_result == mismatch THEN flag_exception_and_hold_product
2. IF pick_quantity < PickList.required_qty THEN trigger_repick_or_backorder

## Expected Outputs
- picked products
- pick confirmation
- inventory depletion
- staging for pack

## Business Rules
- PickList must be validated against OrderDocumentation before execution
- All picks require ScanSystem confirmation to update InventoryRecord
- Compliance: apply GxP audit trail if sector == pharma

## Exception Handling
- Missing item at StagingLocation: log shortage, notify SCOR-D2.8, create backorder record
- Scan failure: require manual override with supervisor approval and dual sign-off

## Success Criteria
- pick_accuracy >= 99.5%
- PickConfirmation generated within SLA
- InventoryRecord updated with no discrepancies

## Compliance Requirements
- GxP if pharma
- GDPR if personal data
- health and safety picking