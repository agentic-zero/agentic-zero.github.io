# SOP — Pick Product (MTO)
**Process ID:** SCOR-D2.9
**Framework:** SCOR | **Domain:** Deliver
**Generated:** 2026-06-08

## Purpose
Process of picking MTO finished goods from staging or warehouse locations for outbound shipment preparation

## Triggers
- PickList received from order fulfillment system (SCOR-D2.8)

## Inputs Required
- pick lists
- staging locations
- order documentation
- picking equipment
- scan systems

## Process Steps
1. IF scan_result == 'match' THEN decrement InventoryRecord and generate PickConfirmation ELSE flag exception and hold item

## Expected Outputs
- picked products
- pick confirmation
- inventory depletion
- staging for pack

## Business Rules
- ScanSystem must confirm every item before PickConfirmation is issued
- Only MTO finished goods from designated StagingLocation may be picked
- PickList must be fully completed before staging for pack

## Exception Handling
- Item not found at StagingLocation: trigger supervisor alert and create replenishment request
- Scan mismatch: quarantine item and log discrepancy for inventory audit

## Success Criteria
- PickConfirmation generated for 100% of PickList items
- InventoryRecord updated with depletion
- PickedProduct staged at PackStagingLocation

## Compliance Requirements
- GxP if pharma
- GDPR if personal data
- health and safety picking