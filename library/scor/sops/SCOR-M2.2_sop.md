# SOP — Issue Sourced/In-Process Product (MTO)
**Process ID:** SCOR-M2.2
**Framework:** SCOR | **Domain:** Make
**Generated:** 2026-06-10

## Purpose
Process of issuing materials and WIP to MTO production operations including kitting, staging and releasing to production floor with full traceability

## Triggers
- New or updated WorkOrder status = 'Released' received from planning system
- ProductionSchedule update with start_date within next 24 hours

## Inputs Required
- production schedule
- material pick lists
- WIP inventory
- work orders
- production routings

## Process Steps
1. IF material availability check fails for any item in MaterialPickList THEN route to exception queue and notify planner
2. IF kitting verification scan fails THEN block ProductionFloorRelease and require re-kitting
3. IF WIP accuracy < 99.5% THEN pause process and trigger inventory reconciliation

## Expected Outputs
- issued materials kits
- WIP transfers
- production floor readiness
- material consumption records

## Business Rules
- Every MaterialConsumptionRecord must include timestamp, user_id, lot_number and location for full traceability
- KittedMaterialSet must be 100% scanned and matched to MaterialPickList before ProductionFloorRelease
- All outputs must update WIPInventory in real time within 30 seconds of issuance

## Exception Handling
- Discrepancy between physical kit and MaterialPickList: quarantine kit, log variance, require supervisor approval before release
- Missing lot traceability data: block release and route to compliance team

## Success Criteria
- Kitting accuracy = 100% verified by scan
- MaterialConsumptionRecord created for 100% of issued items
- ProductionFloorRelease timestamp recorded and WIPInventory updated
- Production floor wait time KPI <= target threshold

## Compliance Requirements
- GxP dispensing if pharma
- ISO 9001
- GDPR if personal data in records