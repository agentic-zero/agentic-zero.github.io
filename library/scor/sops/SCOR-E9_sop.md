# SOP — Manage Supply Chain Risk
**Process ID:** SCOR-E9
**Framework:** SCOR | **Domain:** Enable
**Generated:** 2026-06-08

## Purpose
Process of identifying, assessing, monitoring and mitigating supply chain risks including operational, financial, geopolitical, cyber, AI and regulatory risks across all SCOR domains

## Triggers
- New risk signal received
- Scheduled daily operational data refresh
- Related process SCOR-P1.5 or SCOR-S1.5 emits alert

## Inputs Required
- risk signals
- operational data
- market intelligence
- supplier data
- geopolitical indicators
- AI system outputs

## Process Steps
1. IF RiskExposureValue > threshold THEN generate EarlyWarningAlert and MitigationPlan
2. IF geopolitical indicator score > 0.7 THEN escalate to ContingencyPlan

## Expected Outputs
- risk register
- risk assessments
- mitigation plans
- early warning alerts
- resilience reports
- contingency plans

## Business Rules
- All risk assessments must reference ISO 31000 and NIST AI RMF
- RiskRegister must be updated within 4 hours of new RiskSignal
- EU AI Act Art.9 compliance flag required for any AI-related risk

## Exception Handling
- If AI system outputs unavailable, fallback to manual supplier data review and log as partial assessment
- If data source latency > 24h, mark RiskSignal as low-confidence and require human validation

## Success Criteria
- Risk identification rate >= 0.9
- Mitigation effectiveness >= 0.8
- RiskRegister contains all active risks with mitigation status

## Compliance Requirements
- EU AI Act Art.9 risk management
- ISO 31000 risk management
- NIST AI RMF govern-map-measure-manage
- GDPR risk assessment
- sector-specific risk regulations