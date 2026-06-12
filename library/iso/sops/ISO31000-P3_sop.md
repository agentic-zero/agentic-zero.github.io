# SOP — Risk Treatment and Monitoring
**Process ID:** ISO31000-P3
**Framework:** ISO 31000:2018 | **Domain:** ISO 31000
**Generated:** 2026-06-12

## Purpose
Selection and implementation of risk treatment options including avoidance, reduction, sharing and retention, followed by continuous monitoring, review and recording of risk management outcomes

## Triggers
- receipt of risk evaluation results from ISO31000-P2
- arrival of scheduled review_schedule date
- detection of monitoring metric threshold breach

## Inputs Required
- risk evaluation results
- treatment options
- resource availability
- monitoring metrics
- review schedule

## Process Steps
1. IF residual_risk_level > risk_tolerance THEN select new RiskTreatmentOption
2. IF treatment_implementation_rate < 0.9 THEN escalate resource allocation
3. IF monitoring_compliance < 1.0 THEN trigger immediate ReviewRecord

## Expected Outputs
- treatment plans
- residual risk assessments
- monitoring reports
- review records
- improvement actions

## Business Rules
- TreatmentPlan must document chosen option type (avoidance|reduction|sharing|retention) and assigned owner
- MonitoringReport must be generated at least once per review_schedule interval
- ResidualRiskAssessment must be recorded before process closure
- All outputs require ISO 31000:2018 compliance flag attachment

## Exception Handling
- If resource_availability = false then default to risk retention and log exception in ReviewRecord
- If sector_applicability excludes current domain then skip automation and require manual approval

## Success Criteria
- treatment_implementation_rate >= 0.95
- residual_risk_level <= medium
- monitoring_compliance == 1.0
- all ImprovementActions closed within 30 days

## Compliance Requirements
- ISO 31000:2018
- risk treatment documentation
- continuous monitoring