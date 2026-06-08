# SOP — Transfer Product (MTO)
**Process ID:** SCOR-S2.4
**Framework:** SCOR | **Domain:** Source
**Generated:** 2026-06-07

## Purpose
Process of transferring verified MTO materials to production staging areas or work-in-progress inventory with full traceability and system updates

## Triggers
- Receipt of verification_approval with status approved
- ProductionOrder status changed to released with staging_location assigned

## Inputs Required
- verification approval
- production orders
- staging locations
- transfer equipment
- WIP inventory data

## Process Steps
1. IF verification_approval.status == 'approved' AND production_order.status == 'released' THEN initiate transfer
2. IF material.quantity_verified == production_order.quantity THEN proceed to staging ELSE flag discrepancy

## Expected Outputs
- materials in production staging
- inventory transfer records
- WIP update
- production readiness confirmation

## Business Rules
- Transfer must record chain_of_custody with timestamp and operator_id
- WIP_inventory.accuracy must be updated within 5 minutes of physical move
- Full traceability required: lot_id and serial_numbers must be logged

## Exception Handling
- IF transfer_equipment unavailable THEN queue request and alert logistics with SLA timer
- IF quantity mismatch > 0 THEN halt transfer, create audit record, and notify quality

## Success Criteria
- Materials physically at staging_location
- InventoryTransferRecord created with 100% quantity match
- WIPInventory updated and ProductionReadinessConfirmation emitted

## Compliance Requirements
- GxP material transfer if pharma
- chain of custody
- GDPR if personal data