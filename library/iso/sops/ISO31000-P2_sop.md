# SOP — Risk Assessment Process
**Process ID:** ISO31000-P2
**Framework:** ISO 31000:2018 | **Domain:** ISO 31000
**Generated:** 2026-06-10

## Purpose
Systematic risk assessment process including risk identification, risk analysis and risk evaluation to support informed decision-making across all organizational domains

## Triggers
- New event data received
- Scheduled quarterly assessment
- Related process ISO31000-P1 completion

## Inputs Required
- risk sources
- event data
- consequence data
- likelihood data
- controls inventory

## Process Steps
1. IF (likelihood * consequence) > 12 THEN create TreatmentPriority
2. IF control_effectiveness < 0.6 THEN flag for re-evaluation
3. IF new event data received THEN trigger risk identification

## Expected Outputs
- risk register
- risk heat map
- risk evaluation results
- treatment priorities
- risk reports

## Business Rules
- Every Risk must have both likelihood and consequence values before evaluation
- RiskRegister must be updated within 24 hours of new event data
- All Controls must be linked to at least one Risk

## Exception Handling
- If likelihood or consequence data is missing, default to expert judgment value of 3 and log data_gap flag
- If controls inventory is empty, skip control effectiveness calculation and mark risk as uncontrolled

## Success Criteria
- RiskRegister contains all identified risks with complete likelihood and consequence
- RiskHeatMap generated with no null values
- TreatmentPriority list produced for all high risks

## Compliance Requirements
- ISO 31000:2018
- risk assessment methodology
- enterprise risk