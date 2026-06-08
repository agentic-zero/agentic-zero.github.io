# SOP — Issue Sourced/In-Process Product (MTO)
**Process ID:** SCOR-M2.2
**Framework:** SCOR | **Domain:** Make
**Generated:** 2026-06-07

## Purpose
Process of issuing materials and WIP to MTO production operations including kitting, staging and releasing to production floor with full traceability

## Triggers
- New approved WorkOrder received from production_schedule
- MaterialPickList generated and WIPInventory allocated

## Inputs Required
- production schedule
- material pick lists
- WIP inventory
- work orders
- production routings

## Process Steps
1. IF sector == 'pharma' THEN enforce GxP dispensing and batch traceability before kitting release
2. IF kitting_accuracy < 99.5% THEN block WIPTransfer and trigger exception review

## Expected Outputs
- issued materials kits
- WIP transfers
- production floor readiness
- material consumption records

## Business Rules
- All issued materials must maintain full lot/batch traceability to work_order_id
- Material issue must occur only after production_schedule approval timestamp
- WIP accuracy must be validated via system scan before floor release

## Exception Handling
- Missing pick list items: hold release and notify planner with delta report
- GDPR personal data in records: anonymize consumption records before storage

## Success Criteria
- IssuedMaterialsKit delivered with 100% traceability
- ProductionFloorReadiness status set to true within material_issue_cycle_time SLA
- MaterialConsumptionRecord created and posted

## Compliance Requirements
- GxP dispensing if pharma
- ISO 9001
- GDPR if personal data in records