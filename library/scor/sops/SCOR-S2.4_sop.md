# SOP — Transfer Product (MTO)
**Process ID:** SCOR-S2.4
**Framework:** SCOR | **Domain:** Source
**Generated:** 2026-06-08

## Purpose
Process of transferring verified MTO materials to production staging areas or work-in-progress inventory with full traceability and system updates

## Triggers
- Receipt of VerificationApproval with status approved
- ProductionOrder status changed to released

## Inputs Required
- verification approval
- production orders
- staging locations
- transfer equipment
- WIP inventory data

## Process Steps
1. IF verification_approval.status == 'approved' AND production_order.status == 'released' THEN initiate transfer
2. IF staging_location.capacity >= material.quantity THEN assign location ELSE queue transfer

## Expected Outputs
- materials in production staging
- inventory transfer records
- WIP update
- production readiness confirmation

## Business Rules
- rule1: Maintain full chain-of-custody traceability for every Material transfer
- rule2: Update WIPInventoryData and create InventoryTransferRecord within 5 minutes of physical move
- rule3: Require GxP signature if sector == 'pharma'

## Exception Handling
- Material quantity mismatch: flag discrepancy, hold transfer, and trigger manual audit before proceeding
- StagingLocation unavailable: reroute to alternate location and update ProductionOrder

## Success Criteria
- Material physically located in StagingLocation
- InventoryTransferRecord created with 100% traceability
- WIPInventoryData accuracy == 100%
- ProductionReadinessConfirmation emitted

## Compliance Requirements
- GxP material transfer if pharma
- chain of custody
- GDPR if personal data