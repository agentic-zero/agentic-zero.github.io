# SOP — Transfer Defective Product Return
**Process ID:** SCOR-DR1.4
**Framework:** SCOR | **Domain:** Return
**Generated:** 2026-06-07

## Purpose
Process of transferring received defective returns to appropriate disposition location including quarantine, repair, scrap or refurbishment areas

## Triggers
- DispositionDecision received and InspectionReport validated
- Related process SCOR-DR1.3 signals defective return ready for transfer

## Inputs Required
- inspection report
- disposition decision
- warehouse locations
- transfer resources

## Process Steps
1. IF DispositionDecision == 'quarantine' THEN route to QuarantineLocation
2. IF DispositionDecision == 'repair' THEN route to RepairLocation
3. IF DispositionDecision == 'scrap' THEN route to ScrapLocation
4. IF DispositionDecision == 'refurbish' THEN route to RefurbishLocation

## Expected Outputs
- product transfer completion
- location update
- disposition initiation

## Business Rules
- Transfer must complete within KPI transfer_cycle_time limit
- Quarantine compliance rate must be 100% for pharma sector
- LocationUpdate must be recorded before DispositionInitiation
- GxP quarantine flag required if sector == 'pharma'

## Exception Handling
- Hazardous material: route to certified hazardous location and log environmental compliance
- Missing disposition decision: hold product and trigger SCOR-DR1.3 escalation
- Transfer accuracy < 99%: initiate manual audit and block auto-location update

## Success Criteria
- ProductTransfer status == 'completed'
- LocationUpdate recorded in warehouse system
- DispositionInitiation triggered for target process
- transfer_accuracy == 100% and quarantine_compliance_rate == 100%

## Compliance Requirements
- GxP quarantine requirements if pharma
- ISO 9001
- environmental if hazardous