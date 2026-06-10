# SOP — GDPR Data Processing Principles
**Process ID:** GDPR-ART5
**Framework:** GDPR (EU) 2016/679 | **Domain:** GDPR
**Generated:** 2026-06-10

## Purpose
Core GDPR data processing principles including lawfulness, fairness, transparency, purpose limitation, data minimization, accuracy, storage limitation, integrity, confidentiality and accountability, plus lawful basis and special category data requirements

## Triggers
- New processing activity registration
- Periodic compliance audit
- Data subject request or regulatory inquiry

## Inputs Required
- personal data inventory
- processing purposes
- lawful basis assessment
- data subject categories
- retention schedules

## Process Steps
1. IF LawfulBasis is missing THEN block processing and require assessment
2. IF SpecialCategoryData is true THEN enforce Art9 explicit basis or prohibition
3. IF RetentionSchedule exceeds necessity THEN trigger minimization review

## Expected Outputs
- lawful basis documentation
- privacy notices
- data minimization controls
- retention policies
- accountability evidence

## Business Rules
- Every PersonalData processing must have documented Art6 lawful basis before execution
- Purpose limitation: PersonalData must only be used for declared ProcessingPurpose
- Storage limitation: PersonalData must be deleted or anonymized at RetentionSchedule end
- Data minimization: only collect fields required for ProcessingPurpose

## Exception Handling
- Special category processing allowed without consent only for vital interests, legal claims or substantial public interest with documented DPIA

## Success Criteria
- lawful_basis_coverage == 100%
- privacy_notice_completeness >= 95%
- retention_compliance_rate == 100%

## Compliance Requirements
- GDPR Art.5 principles
- GDPR Art.6 lawful basis
- GDPR Art.9 special categories