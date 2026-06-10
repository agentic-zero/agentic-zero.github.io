# SOP — MAP — AI Risk Context and Categorization
**Process ID:** NIST-MAP
**Framework:** NIST AI RMF 1.0 | **Domain:** NIST AI RMF
**Generated:** 2026-06-10

## Purpose
Contextualizing AI risks by categorizing AI systems, identifying stakeholders and their needs, mapping AI system impacts and establishing risk tolerances for different use cases

## Triggers
- New AI use case description received
- Scheduled quarterly AI system inventory refresh
- Related process NIST-GOVERN or NIST-MEASURE completion signal

## Inputs Required
- AI use case descriptions
- stakeholder map
- impact categories
- risk tolerance definitions
- deployment context

## Process Steps
1. IF risk_categorization_coverage < 0.9 THEN request additional use case descriptions
2. IF stakeholder_mapping_completeness < 1.0 THEN trigger stakeholder interview workflow
3. IF impact_assessment_accuracy < 0.85 THEN rerun impact scoring with updated categories

## Expected Outputs
- AI risk categories
- impact assessments
- stakeholder impact map
- risk tolerance thresholds
- AI system inventory

## Business Rules
- All inputs must be validated against NIST AI RMF 1.0 MAP schema before processing
- Risk tolerance thresholds must be numeric values between 0.0 and 1.0
- Every AI_System must be assigned at least one Risk_Category
- Compliance flags NIST AI RMF 1.0 MAP and EU AI Act risk classification must be recorded

## Exception Handling
- Missing stakeholder map: default to generic stakeholder list and log warning
- Zero automation_potential: route to manual review queue

## Success Criteria
- risk_categorization_coverage >= 0.95
- stakeholder_mapping_completeness == 1.0
- impact_assessment_accuracy >= 0.9
- All compliance_flags populated

## Compliance Requirements
- NIST AI RMF 1.0 MAP
- ISO 42001 risk assessment
- EU AI Act risk classification