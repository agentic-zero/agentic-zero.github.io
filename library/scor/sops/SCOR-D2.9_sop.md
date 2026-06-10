# SOP — Pick Product (MTO)
**Process ID:** SCOR-D2.9
**Framework:** SCOR | **Domain:** Deliver
**Generated:** 2026-06-10

## Purpose
Process of picking MTO finished goods from staging or warehouse locations for outbound shipment preparation

## Triggers
- PickList received from order management system (SCOR-D2.8)

## Inputs Required
- pick lists
- staging locations
- order documentation
- picking equipment
- scan systems

## Process Steps
1. IF scan mismatch THEN flag exception and hold product
2. IF quantity < PickList.quantity THEN trigger partial pick and notify WMS

## Expected Outputs
- picked products
- pick confirmation
- inventory depletion
- staging for pack

## Business Rules
- Every item must be scanned before leaving StagingLocation
- Pick accuracy must be logged per PickList line
- Comply with health and safety picking protocol before equipment use

## Exception Handling
- Product missing from StagingLocation: create exception ticket and request replenishment
- Equipment failure: switch to backup device and log downtime

## Success Criteria
- 100% of PickList lines confirmed via scan
- InventoryRecord decremented correctly
- PickConfirmation sent within SLA cycle time

## Compliance Requirements
- GxP if pharma
- GDPR if personal data
- health and safety picking