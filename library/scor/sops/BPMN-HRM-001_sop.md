# SOP — Production Scheduling
**Process ID:** BPMN-HRM-001
**Framework:**  | **Domain:** BPMN
**Generated:** 2026-06-09

## Purpose
Production scheduling and execution process from work order release to production completion including capacity allocation, material staging and quality control

## Triggers
- Production Order Released event from ERP

## Inputs Required
- production orders
- BOM
- routing
- capacity plan
- material availability
- quality plans

## Process Steps
1. IF MaterialsReady == true THEN StageMaterials ELSE hold and notify Planning
2. IF CapacityAvailable == true THEN ScheduleSequence ELSE reallocate or escalate
3. IF QualityOK == true THEN RecordOutput ELSE IF ReworkRequired == true THEN ExecuteProduction ELSE end as OrderFailed

## Expected Outputs
- production schedule
- work instructions
- production records
- quality data
- finished goods

## Business Rules
- Require valid production_orders, BOM and routing before starting
- Enforce sector compliance: GxP batch records if pharma, HACCP if food
- Track and log all four KPIs after each ProductionComplete
- Automation actions limited to 0.7 potential score

## Exception Handling
- CapacityAvailable false after 2 attempts: escalate to Planning lane and end as OrderFailed
- ReworkRequired true more than 2 times: terminate as OrderFailed
- MaterialAvailability false after staging: return to VerifyMaterialAvailability

## Success Criteria
- End event ProductionComplete reached
- schedule_adherence >= 0.95 AND OEE >= 0.85 AND first_pass_yield >= 0.98

## Compliance Requirements
- GxP batch records if pharma
- HACCP if food
- ISO 9001
- ATEX if applicable