# SOP — MAP — AI Risk Context and Categorization
**Process ID:** NIST-MAP
**Framework:** NIST AI RMF 1.0 | **Domain:** NIST AI RMF
**Generated:** 2026-06-10

## Purpose
Contextualizing AI risks by categorizing AI systems, identifying stakeholders and their needs, mapping AI system impacts and establishing risk tolerances for different use cases

## Triggers
- AI use case descriptions received
- deployment context updated

## Inputs Required
- AI use case descriptions
- stakeholder map
- impact categories
- risk tolerance definitions
- deployment context

## Process Steps
1. IF risk categorization coverage < 1.0 THEN add missing AIRiskCategory to AISystemInventory
2. IF stakeholder mapping completeness < 0.9 THEN request additional StakeholderMap entries

## Expected Outputs
- AI risk categories
- impact assessments
- stakeholder impact map
- risk tolerance thresholds
- AI system inventory

## Business Rules
- Every AIUseCaseDescription must map to at least one AIRiskCategory
- RiskToleranceThreshold must be set per sector_applicability entry before ImpactAssessment
- All outputs require compliance_flags check for NIST AI RMF 1.0 MAP

## Exception Handling
- defense sector: require extra EUAIA-ART6 flag before producing StakeholderImpactMap

## Success Criteria
- risk categorization coverage == 1.0
- stakeholder mapping completeness >= 0.9
- impact assessment accuracy >= 0.85

## Compliance Requirements
- NIST AI RMF 1.0 MAP
- ISO 42001 risk assessment
- EU AI Act risk classification