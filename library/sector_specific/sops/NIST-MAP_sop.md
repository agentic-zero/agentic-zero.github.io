# SOP — MAP — AI Risk Context and Categorization
**Process ID:** NIST-MAP
**Framework:** NIST AI RMF 1.0 | **Domain:** NIST AI RMF
**Generated:** 2026-06-12

## Purpose
Contextualizing AI risks by categorizing AI systems, identifying stakeholders and their needs, mapping AI system impacts and establishing risk tolerances for different use cases

## Triggers
- AI use case descriptions received
- DeploymentContext updated

## Inputs Required
- AI use case descriptions
- stakeholder map
- impact categories
- risk tolerance definitions
- deployment context

## Process Steps
1. IF sector in ['defense','pharma'] THEN enforce RiskToleranceThreshold = 'strict'
2. IF stakeholder_needs identified THEN generate StakeholderImpactMap entry

## Expected Outputs
- AI risk categories
- impact assessments
- stakeholder impact map
- risk tolerance thresholds
- AI system inventory

## Business Rules
- Require compliance_flags include 'NIST AI RMF 1.0 MAP' before output generation
- risk_categorization_coverage KPI must equal 1.0
- Only process if sector_applicability matches input sector

## Exception Handling
- If automation_potential < 0.6 require manual approval on all ImpactAssessment outputs

## Success Criteria
- All outputs produced and KPIs met: risk categorization coverage=1.0, stakeholder mapping completeness>=0.95, impact assessment accuracy>=0.9

## Compliance Requirements
- NIST AI RMF 1.0 MAP
- ISO 42001 risk assessment
- EU AI Act risk classification