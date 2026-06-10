# SOP — GDPR Data Processing Principles
**Process ID:** GDPR-ART5
**Framework:** GDPR (EU) 2016/679 | **Domain:** GDPR
**Generated:** 2026-06-10

## Purpose
Core GDPR data processing principles including lawfulness, fairness, transparency, purpose limitation, data minimization, accuracy, storage limitation, integrity, confidentiality and accountability, plus lawful basis and special category data requirements

## Triggers
- New processing activity registration
- Quarterly compliance audit
- Data subject request for access or erasure

## Inputs Required
- personal data inventory
- processing purposes
- lawful basis assessment
- data subject categories
- retention schedules

## Process Steps
1. IF LawfulBasis is missing THEN block processing and require assessment
2. IF SpecialCategoryData is true THEN require explicit Art9 exception or consent
3. IF retention period exceeds schedule THEN trigger deletion workflow

## Expected Outputs
- lawful basis documentation
- privacy notices
- data minimization controls
- retention policies
- accountability evidence

## Business Rules
- Every PersonalDataInventory entry must have documented LawfulBasis from Art6
- ProcessingPurpose must be specific, explicit and legitimate before any processing
- DataMinimizationControl must reduce collected fields to minimum necessary for purpose
- RetentionPolicy must enforce storage limitation with automated expiry
- AccountabilityEvidence must log all decisions for audit

## Exception Handling
- Vital interests or legal obligation may override consent requirement for SpecialCategoryData; log justification and notify DPO

## Success Criteria
- lawful_basis_coverage == 100%
- privacy_notice_completeness >= 95%
- retention_compliance_rate >= 98%

## Compliance Requirements
- GDPR Art.5 principles
- GDPR Art.6 lawful basis
- GDPR Art.9 special categories