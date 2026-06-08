# SOP — Manage Supply Chain Risk
**Process ID:** SCOR-E9
**Framework:** SCOR | **Domain:** Enable
**Generated:** 2026-06-07

## Purpose
Process of identifying, assessing, monitoring and mitigating supply chain risks including operational, financial, geopolitical, cyber, AI and regulatory risks across all SCOR domains

## Triggers
- new risk_signal received
- scheduled daily batch from operational_data
- related_process SCOR-E8 completion event

## Inputs Required
- risk signals
- operational data
- market intelligence
- supplier data
- geopolitical indicators
- AI system outputs

## Process Steps
1. IF risk_exposure_value > 0.7 THEN create MitigationPlan within 24h
2. IF geopolitical_indicator changes > 20% THEN trigger RiskAssessment
3. IF mitigation_effectiveness < 0.8 THEN escalate to ContingencyPlan

## Expected Outputs
- risk register
- risk assessments
- mitigation plans
- early warning alerts
- resilience reports
- contingency plans

## Business Rules
- risk_register must be updated every 24 hours per ISO 31000
- all AI system outputs must pass EU AI Act Art.9 risk management check before inclusion
- supply_chain_resilience_score must be recalculated after every MitigationPlan activation

## Exception Handling
- sector=defense: skip public market_intelligence and use classified supplier_data only
- risk_type=cyber: bypass standard 24h update and require real-time assessment

## Success Criteria
- risk_identification_rate >= 0.95
- risk_exposure_value reduced by >= 30% within 7 days
- all compliance_flags validated with no open violations

## Compliance Requirements
- EU AI Act Art.9 risk management
- ISO 31000 risk management
- NIST AI RMF govern-map-measure-manage
- GDPR risk assessment
- sector-specific risk regulations