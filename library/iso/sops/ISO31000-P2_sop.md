# SOP — Risk Assessment Process
**Process ID:** ISO31000-P2
**Framework:** ISO 31000:2018 | **Domain:** ISO 31000
**Generated:** 2026-06-12

## Purpose
Systematic risk assessment process including risk identification, risk analysis and risk evaluation to support informed decision-making across all organizational domains

## Triggers
- New event_data received from monitoring systems
- Scheduled quarterly assessment from ISO31000-P1
- Controls inventory change notification

## Inputs Required
- risk sources
- event data
- consequence data
- likelihood data
- controls inventory

## Process Steps
1. IF likelihood * consequence > 12 THEN escalate to TreatmentPriority
2. IF control effectiveness < 0.6 THEN flag for reassessment

## Expected Outputs
- risk register
- risk heat map
- risk evaluation results
- treatment priorities
- risk reports

## Business Rules
- Every Risk must have at least one Likelihood and one Consequence value
- RiskRegister must be updated within 24 hours of new Event data
- All Controls must be linked to at least one Risk

## Exception Handling
- Missing likelihood data: default to 0.3 and mark as estimated
- No controls inventory: skip mitigation scoring and log exception

## Success Criteria
- RiskRegister contains all input events with evaluation results
- RiskHeatMap generated with no missing cells
- TreatmentPriority list produced for all high risks

## Compliance Requirements
- ISO 31000:2018
- risk assessment methodology
- enterprise risk