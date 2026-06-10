# SOP — Issue Sourced/In-Process Product (MTO)
**Process ID:** SCOR-M2.2
**Framework:** SCOR | **Domain:** Make
**Generated:** 2026-06-10

## Purpose
Process of issuing materials and WIP to MTO production operations including kitting, staging and releasing to production floor with full traceability

## Triggers
- WorkOrder status changed to 'Released' in ERP
- ProductionSchedule daily batch job at 06:00

## Inputs Required
- production schedule
- material pick lists
- WIP inventory
- work orders
- production routings

## Process Steps
1. IF all pick list items available in WIPInventory THEN proceed to kitting ELSE hold and escalate shortage
2. IF pharma sector THEN enforce GxP dispensing check ELSE skip
3. IF kitting accuracy >= 99.5% THEN release to floor ELSE quarantine and rework

## Expected Outputs
- issued materials kits
- WIP transfers
- production floor readiness
- material consumption records

## Business Rules
- Require full lot traceability on every IssuedMaterialsKit
- Log timestamp and user ID on every MaterialConsumptionRecord for ISO 9001 audit
- Apply GDPR masking if WorkOrder contains personal data fields

## Exception Handling
- Material shortage: auto-create SCOR-S2.4 replenishment request and pause WorkOrder
- GxP deviation: route to quality hold and require QA sign-off before release

## Success Criteria
- kitting_accuracy >= 99.5%
- material_issue_cycle_time <= 4 hours
- production_floor_wait_time == 0
- WIPTransfer posted with zero variance

## Compliance Requirements
- GxP dispensing if pharma
- ISO 9001
- GDPR if personal data in records