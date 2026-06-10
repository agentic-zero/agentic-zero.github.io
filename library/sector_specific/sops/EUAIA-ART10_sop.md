# SOP — Data Governance for High-Risk AI
**Process ID:** EUAIA-ART10
**Framework:** EU AI Act 2024 | **Domain:** EU AI Act
**Generated:** 2026-06-10

## Purpose
Data governance requirements for training, validation and testing datasets including relevance, representativeness, freedom from errors and completeness requirements

## Triggers
- High-risk AI system training initiation flagged by EUAIA-ART9
- New dataset version uploaded to training pipeline

## Inputs Required
- training datasets
- validation datasets
- test datasets
- data provenance
- bias assessment

## Process Steps
1. IF DataCompletenessRate < 0.95 THEN trigger additional data collection
2. IF BiasMetric > 0.15 THEN require bias mitigation before model training
3. IF RepresentativenessScore < 0.8 THEN expand dataset sampling strategy

## Expected Outputs
- data governance documentation
- dataset quality report
- bias assessment
- data lineage records

## Business Rules
- All training, validation and test datasets must include documented DataProvenance
- DatasetQualityScore must be computed and recorded for every input dataset
- DataLineageRecord must be generated for every output report
- BiasAssessment must be performed on all datasets used in high-risk AI

## Exception Handling
- If sector is defense and data is classified, DataProvenance may reference internal secure ledger instead of public metadata
- If automation_potential < 0.5, manual review step is mandatory before signing DataGovernanceDocumentation

## Success Criteria
- DatasetQualityScore >= 0.9 AND BiasMetric <= 0.1 AND DataCompletenessRate >= 0.95 AND RepresentativenessScore >= 0.85
- DataGovernanceDocumentation signed and linked to DataLineageRecord

## Compliance Requirements
- EU AI Act Art.10 mandatory
- GDPR data quality
- algorithmic bias prevention