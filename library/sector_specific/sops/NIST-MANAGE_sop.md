# SOP — MANAGE — AI Risk Treatment and Response
**Process ID:** NIST-MANAGE
**Framework:** NIST AI RMF 1.0 | **Domain:** NIST AI RMF
**Generated:** 2026-06-12

## Purpose
Managing AI risks through treatment plans, prioritization, response activities and recovery from AI incidents including residual risk monitoring and continuous improvement

## Triggers
- New RiskAssessment received from MEASURE
- Incident logged with severity >= MEDIUM
- Quarterly residual risk review scheduled

## Inputs Required
- risk assessments
- treatment options
- resource constraints
- incident data
- residual risk levels

## Process Steps
1. IF residual_risk_level > 0.3 THEN escalate to GOVERN and allocate additional resources
2. IF incident_severity >= HIGH THEN execute RecoveryPlan within 4 hours
3. IF risk_treatment_coverage < 0.8 THEN reprioritize TreatmentOption list

## Expected Outputs
- risk treatment plans
- incident response records
- residual risk reports
- improvement actions
- recovery plans

## Business Rules
- Every RiskAssessment must have corresponding RiskTreatmentPlan within 72 hours
- All IncidentResponseRecord entries require timestamp and root_cause fields
- ResidualRiskReport must be generated at least quarterly

## Exception Handling
- IF resource_constraints prevent full treatment THEN document partial coverage and schedule re-assessment in 30 days
- IF related_process (NIST-MEASURE) data missing THEN use last known values and flag for audit

## Success Criteria
- risk_treatment_coverage >= 0.9
- incident_response_time <= 4 hours
- residual_risk_reduction >= 0.2 over 90 days

## Compliance Requirements
- NIST AI RMF 1.0 MANAGE
- EU AI Act incident management
- ISO 42001 improvement