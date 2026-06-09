# SOP — Produce and Test (MTO)
**Process ID:** SCOR-M2.3
**Framework:** SCOR | **Domain:** Make
**Generated:** 2026-06-08

## Purpose
Process of executing MTO production operations including manufacturing, assembly, in-process quality control and functional testing against customer specifications

## Triggers
- WorkOrder status changed to Released with attached ProductionRouting and QualityPlan

## Inputs Required
- work orders
- production routings
- quality plans
- test specifications
- tooling and equipment

## Process Steps
1. IF first_pass_yield < 0.95 THEN trigger root_cause_analysis
2. IF test_pass_rate < 1.0 THEN execute rework_or_scrap logic
3. IF in_process_defect_rate > threshold THEN pause line and log exception

## Expected Outputs
- manufactured products
- test results
- in-process quality records
- production completion confirmations

## Business Rules
- All production steps must record ISO 9001 compliant timestamps and operator IDs
- Pharma batches require GxP batch manufacturing record creation before completion
- ATEX certified equipment must be validated before use in explosive atmospheres
- HACCP critical control points must be checked and logged for food sector

## Exception Handling
- Missing tooling calibration: block start and route to maintenance queue
- Customer spec change mid-process: require new WorkOrder version and restart affected routing steps

## Success Criteria
- All TestResult records show pass, ProductionCompletionConfirmation issued, and KPIs within target (cycle_time <= plan, first_pass_yield >= 0.95)

## Compliance Requirements
- GxP batch manufacturing records if pharma
- ISO 9001 production
- ATEX if explosive atmosphere
- food safety HACCP