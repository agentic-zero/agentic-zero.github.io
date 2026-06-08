# SOP — Produce and Test (MTO)
**Process ID:** SCOR-M2.3
**Framework:** SCOR | **Domain:** Make
**Generated:** 2026-06-07

## Purpose
Process of executing MTO production operations including manufacturing, assembly, in-process quality control and functional testing against customer specifications

## Triggers
- WorkOrder status changed to released from planning system
- ProductionRouting and QualityPlan attached to WorkOrder

## Inputs Required
- work orders
- production routings
- quality plans
- test specifications
- tooling and equipment

## Process Steps
1. IF in-process defect rate > threshold THEN trigger rework or scrap
2. IF test pass rate < 95% THEN initiate root cause analysis
3. IF tooling unavailable THEN reschedule work order

## Expected Outputs
- manufactured products
- test results
- in-process quality records
- production completion confirmations

## Business Rules
- All production must log ISO 9001 compliant records
- GxP batch records required for pharma sector
- HACCP critical control points must be checked for food sector
- First-pass yield must be calculated per work order

## Exception Handling
- Equipment failure: pause process, log downtime, notify maintenance
- Non-conforming test result: quarantine product, create deviation record
- Missing quality plan: block execution until plan is attached

## Success Criteria
- ProductionCompletionConfirmation generated for all units
- Test pass rate >= target KPI
- In-process quality records complete with zero open deviations

## Compliance Requirements
- GxP batch manufacturing records if pharma
- ISO 9001 production
- ATEX if explosive atmosphere
- food safety HACCP