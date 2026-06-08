# SOP — Transfer Defective Product Return
**Process ID:** SCOR-DR1.4
**Framework:** SCOR | **Domain:** Return
**Generated:** 2026-06-08

## Purpose
Process of transferring received defective returns to appropriate disposition location including quarantine, repair, scrap or refurbishment areas

## Triggers
- Receipt of DispositionDecision and InspectionReport from SCOR-DR1.3

## Inputs Required
- inspection report
- disposition decision
- warehouse locations
- transfer resources

## Process Steps
1. IF DispositionDecision == 'quarantine' THEN route to QuarantineArea
2. IF DispositionDecision == 'repair' THEN route to RepairArea
3. IF DispositionDecision == 'scrap' THEN route to ScrapArea
4. IF DispositionDecision == 'refurbish' THEN route to RefurbishmentArea

## Expected Outputs
- product transfer completion
- location update
- disposition initiation

## Business Rules
- Transfer must achieve 100% location accuracy before LocationUpdate
- GxP quarantine requirements apply if sector == 'pharma'
- ISO 9001 documentation required for all transfers
- Environmental handling rules apply if Product is hazardous

## Exception Handling
- Hazardous Product: block transfer until environmental compliance verified and override approval recorded
- Missing DispositionDecision: halt process and escalate to SCOR-DR1.3

## Success Criteria
- Product reaches correct target location
- LocationUpdate recorded in system
- DispositionInitiation triggered
- Transfer cycle time within KPI
- Quarantine compliance rate = 100%

## Compliance Requirements
- GxP quarantine requirements if pharma
- ISO 9001
- environmental if hazardous