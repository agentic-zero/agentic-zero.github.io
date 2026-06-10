# SOP — Data Governance for High-Risk AI
**Process ID:** EUAIA-ART10
**Framework:** EU AI Act 2024 | **Domain:** EU AI Act
**Generated:** 2026-06-10

## Purpose
Data governance requirements for training, validation and testing datasets including relevance, representativeness, freedom from errors and completeness requirements

## Triggers
- High-risk AI system registration under EU AI Act Art.10
- New training/validation/test dataset ingestion event

## Inputs Required
- training datasets
- validation datasets
- test datasets
- data provenance
- bias assessment

## Process Steps
1. IF representativeness_score < 0.8 THEN trigger dataset augmentation or resampling
2. IF bias_metric > 0.1 THEN execute bias mitigation and re-assessment
3. IF data_completeness_rate < 0.95 THEN reject dataset and request additional data

## Expected Outputs
- data governance documentation
- dataset quality report
- bias assessment
- data lineage records

## Business Rules
- TrainingDataset must satisfy relevance, representativeness, error-free and completeness criteria
- All datasets must maintain documented data lineage
- BiasAssessment must be executed before any model training step
- DatasetQualityReport must include dataset_quality_score, bias_metric, data_completeness_rate and representativeness_score

## Exception Handling
- Defense sector datasets may skip public provenance disclosure if national security flag is set
- Pharma sector datasets require additional GDPR anonymization verification before BiasAssessment

## Success Criteria
- dataset_quality_score >= 0.85
- bias_metric <= 0.05
- data_completeness_rate >= 0.95
- representativeness_score >= 0.8
- DataGovernanceDocumentation and DataLineageRecords generated

## Compliance Requirements
- EU AI Act Art.10 mandatory
- GDPR data quality
- algorithmic bias prevention