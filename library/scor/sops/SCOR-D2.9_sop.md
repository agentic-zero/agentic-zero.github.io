# SOP — Pick Product (MTO)
**Process ID:** SCOR-D2.9
**Framework:** SCOR | **Domain:** Deliver
**Generated:** 2026-06-10

## Purpose
Process of picking MTO finished goods from staging or warehouse locations for outbound shipment preparation

## Triggers
- PickList received from order management system with status 'ready_to_pick'

## Inputs Required
- pick lists
- staging locations
- order documentation
- picking equipment
- scan systems

## Process Steps
1. IF scanned_item_id equals PickList.item_id THEN decrement InventoryRecord.quantity ELSE flag discrepancy and halt pick

## Expected Outputs
- picked products
- pick confirmation
- inventory depletion
- staging for pack

## Business Rules
- rule1: All PickList items must be scanned before PickConfirmation is generated
- rule2: InventoryRecord must be updated within 30 seconds of each scan
- rule3: Pick accuracy must be validated against OrderDocumentation before staging for pack

## Exception Handling
- Item not found at StagingLocation: notify supervisor, create exception ticket, and substitute from alternate location if available

## Success Criteria
- PickConfirmation generated with 100% item match and InventoryRecord updated with no discrepancies

## Compliance Requirements
- GxP if pharma
- GDPR if personal data
- health and safety picking