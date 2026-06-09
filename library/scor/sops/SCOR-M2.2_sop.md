# SOP — Issue Sourced/In-Process Product (MTO)
**Process ID:** SCOR-M2.2
**Framework:** SCOR | **Domain:** Make
**Generated:** 2026-06-08

## Purpose
Process of issuing materials and WIP to MTO production operations including kitting, staging and releasing to production floor with full traceability

## Triggers
- New or updated WorkOrder with status 'released' received from planning system
- MaterialPickList generated from production schedule

## Inputs Required
- production schedule
- material pick lists
- WIP inventory
- work orders
- production routings

## Process Steps
1. IF material availability < pick list quantity THEN create exception hold and notify planner
2. IF routing step requires serial tracking THEN enforce scan of each item before staging
3. IF WIP transfer crosses cost center THEN require approval code before release

## Expected Outputs
- issued materials kits
- WIP transfers
- production floor readiness
- material consumption records

## Business Rules
- Every issued item must record lot/serial, timestamp, operator ID and destination work order
- Kitting accuracy must be verified by barcode scan before staging completion
- Production floor release only permitted when all pick list items show status 'staged'

## Exception Handling
- Short pick: flag WorkOrder, partial kit released only with planner override and updated consumption record
- Expired material detected: block issue, route to quarantine and trigger replacement requisition

## Success Criteria
- All pick list items issued with 100% traceability records created
- KittedMaterial staged and ProductionFloorRelease timestamp recorded within target cycle time
- WIP accuracy delta = 0 after transfer confirmation

## Compliance Requirements
- GxP dispensing if pharma
- ISO 9001
- GDPR if personal data in records