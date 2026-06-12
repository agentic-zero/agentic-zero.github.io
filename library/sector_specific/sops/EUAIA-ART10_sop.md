# SOP — Data Governance for High-Risk AI
**Process ID:** EUAIA-ART10
**Framework:** EU AI Act 2024 | **Domain:** EU AI Act
**Generated:** 2026-06-12

## Purpose
Data governance requirements for training, validation and testing datasets including relevance, representativeness, freedom from errors and completeness requirements

## Triggers
- High-risk AI system training initiation under EU AI Act Art.10
- New dataset ingestion into training pipeline

## Inputs Required
- training datasets
- validation datasets
- test datasets
- data provenance
- bias assessment

## Process Steps
1. IF data_completeness_rate < 0.95 THEN require additional data collection
2. IF bias_metric > 0.1 THEN trigger mitigation review before model training

## Expected Outputs
- data governance documentation
- dataset quality report
- bias assessment
- data lineage records

## Business Rules
- All datasets must have representativeness_score >= 0.85
- Data provenance must be recorded for every training, validation and test dataset
- Dataset quality score must be computed and logged before any model training step

## Exception Handling
- If sector is defense and data is classified, completeness_rate threshold may be lowered to 0.80 with documented justification

## Success Criteria
- dataset_quality_score >= 0.9 AND bias_metric <= 0.1 AND data_completeness_rate >= 0.95 AND representativeness_score >= 0.85

## Compliance Requirements
- EU AI Act Art.10 mandatory
- GDPR data quality
- algorithmic bias prevention