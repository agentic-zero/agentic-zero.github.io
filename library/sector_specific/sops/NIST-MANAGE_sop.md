# SOP — MANAGE — AI Risk Treatment and Response
**Process ID:** NIST-MANAGE
**Framework:** NIST AI RMF 1.0 | **Domain:** NIST AI RMF
**Generated:** 2026-06-10

## Purpose
Managing AI risks through treatment plans, prioritization, response activities and recovery from AI incidents including residual risk monitoring and continuous improvement

## Triggers
- New RiskAssessment received
- IncidentData logged
- ResidualRiskLevel exceeds 0.3

## Inputs Required
- risk assessments
- treatment options
- resource constraints
- incident data
- residual risk levels

## Process Steps
1. IF ResidualRiskLevel > threshold THEN execute RecoveryPlan
2. IF incident_response_time > SLA THEN trigger ImprovementAction
3. IF risk_treatment_coverage < 0.8 THEN reallocate ResourceConstraint

## Expected Outputs
- risk treatment plans
- incident response records
- residual risk reports
- improvement actions
- recovery plans

## Business Rules
- RiskTreatmentPlan must cover all inputs from RiskAssessment
- IncidentResponseRecord must be created within 24 hours of IncidentData receipt
- ResidualRiskReport must be generated after every RiskTreatmentPlan

## Exception Handling
- Low automation_potential sectors require manual approval before RecoveryPlan execution
- Defense sector skips automated ImprovementAction if compliance_flags include EU AI Act

## Success Criteria
- risk_treatment_coverage >= 0.9
- incident_response_time <= 3600 seconds
- residual_risk_reduction >= 0.2 per quarter

## Compliance Requirements
- NIST AI RMF 1.0 MANAGE
- EU AI Act incident management
- ISO 42001 improvement