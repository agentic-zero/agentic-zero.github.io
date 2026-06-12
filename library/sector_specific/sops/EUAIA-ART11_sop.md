# SOP — Technical Documentation Requirements
**Process ID:** EUAIA-ART11
**Framework:** EU AI Act 2024 | **Domain:** EU AI Act
**Generated:** 2026-06-12

## Purpose
Mandatory technical documentation for high-risk AI systems covering system description, design specifications, training methodology, performance metrics and conformity assessment evidence

## Triggers
- HighRiskAISystem design approval completed
- new training run finished
- scheduled quarterly review triggered

## Inputs Required
- AI system design
- training documentation
- test results
- risk assessment
- conformity evidence

## Process Steps
1. IF documentation_completeness_score < 0.95 THEN trigger update cycle before CE marking submission
2. IF conformity_assessment_pass_rate < 1.0 THEN return to risk_assessment for remediation

## Expected Outputs
- technical file
- system card
- conformity declaration
- Annex IV documentation

## Business Rules
- TechnicalDocumentation must contain system_description, design_specifications, training_methodology, performance_metrics and conformity_assessment_evidence per EU AI Act Art.11
- AnnexIVDocumentation must be included for all high-risk systems before CE marking
- update_frequency must be at minimum every 6 months or after any material model change

## Exception Handling
- If AI system is not classified as high-risk under EU AI Act Annex III then TechnicalDocumentation requirements are waived but voluntary SystemCard is recommended

## Success Criteria
- documentation_completeness_score >= 0.95
- conformity_assessment_pass_rate == 1.0
- TechnicalFile, SystemCard, ConformityDeclaration and AnnexIVDocumentation all generated and version-controlled

## Compliance Requirements
- EU AI Act Art.11 mandatory
- Annex IV documentation
- CE marking requirements