# SOP — MANAGE — AI Risk Treatment and Response
**Process ID:** NIST-MANAGE
**Framework:** NIST AI RMF 1.0 | **Domain:** NIST AI RMF
**Generated:** 2026-06-10

## Purpose
Managing AI risks through treatment plans, prioritization, response activities and recovery from AI incidents including residual risk monitoring and continuous improvement

## Triggers
- New RiskAssessment received
- IncidentData logged
- Scheduled residual risk review (daily)

## Inputs Required
- risk assessments
- treatment options
- resource constraints
- incident data
- residual risk levels

## Process Steps
1. IF residual_risk_level > acceptable_threshold THEN create new RiskTreatmentPlan
2. IF incident_severity == 'high' THEN activate RecoveryPlan within 1 hour

## Expected Outputs
- risk treatment plans
- incident response records
- residual risk reports
- improvement actions
- recovery plans

## Business Rules
- RiskTreatmentPlan must allocate resources within documented constraints
- IncidentResponseRecord must be created within 4 hours of IncidentData receipt
- All outputs require audit log entry with timestamp and actor

## Exception Handling
- If resource constraints block full treatment, log residual risk and escalate to NIST-GOVERN within 24 hours

## Success Criteria
- risk_treatment_coverage >= 0.95
- incident_response_time <= 3600 seconds
- residual_risk_reduction >= 0.20 over 30 days

## Compliance Requirements
- NIST AI RMF 1.0 MANAGE
- EU AI Act incident management
- ISO 42001 improvement