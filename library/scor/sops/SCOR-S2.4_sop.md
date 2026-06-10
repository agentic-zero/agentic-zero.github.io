# SOP — Transfer Product (MTO)
**Process ID:** SCOR-S2.4
**Framework:** SCOR | **Domain:** Source
**Generated:** 2026-06-10

## Purpose
Process of transferring verified MTO materials to production staging areas or work-in-progress inventory with full traceability and system updates

## Triggers
- receipt of verification_approval with status approved
- production_order status changed to 'ready for staging'

## Inputs Required
- verification approval
- production orders
- staging locations
- transfer equipment
- WIP inventory data

## Process Steps
1. IF verification_approval.status == 'approved' AND production_order.mto_flag == true THEN execute transfer
2. IF staging_location.capacity >= required_quantity THEN assign location ELSE queue transfer

## Expected Outputs
- materials in production staging
- inventory transfer records
- WIP update
- production readiness confirmation

## Business Rules
- transfer must maintain full traceability via batch/lot records
- system must update WIP inventory within 5 minutes of physical move
- chain_of_custody log required for all pharma or defense transfers

## Exception Handling
- IF pharma sector AND GxP flag active THEN require electronic signature before transfer
- IF personal_data present THEN apply GDPR anonymization to transfer records before storage

## Success Criteria
- materials moved to staging_location with 100 percent transfer_accuracy
- inventory_transfer_record created and WIP_update committed
- production_readiness_confirmation emitted with status 'ready'

## Compliance Requirements
- GxP material transfer if pharma
- chain of custody
- GDPR if personal data