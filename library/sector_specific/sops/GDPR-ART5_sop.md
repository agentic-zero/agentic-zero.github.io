# SOP — GDPR Data Processing Principles
**Process ID:** GDPR-ART5
**Framework:** GDPR (EU) 2016/679 | **Domain:** GDPR
**Generated:** 2026-06-12

## Purpose
Core GDPR data processing principles including lawfulness, fairness, transparency, purpose limitation, data minimization, accuracy, storage limitation, integrity, confidentiality and accountability, plus lawful basis and special category data requirements

## Triggers
- New processing activity registered in inventory
- Quarterly compliance audit scheduled

## Inputs Required
- personal data inventory
- processing purposes
- lawful basis assessment
- data subject categories
- retention schedules

## Process Steps
1. IF SpecialCategoryData == true THEN require explicit Art9 condition before processing
2. IF LawfulBasis == consent AND consent withdrawn THEN stop processing unless alternative Art6 basis exists

## Expected Outputs
- lawful basis documentation
- privacy notices
- data minimization controls
- retention policies
- accountability evidence

## Business Rules
- Every PersonalData processing MUST have one documented Art6 lawful basis
- PersonalData MUST be limited to data fields necessary for stated ProcessingPurpose
- RetentionSchedule MUST enforce deletion or anonymization at end of period
- PrivacyNotice MUST be published before processing starts

## Exception Handling
- If legal obligation overrides retention limit, document specific statute and extend RetentionPolicy with justification

## Success Criteria
- lawful_basis_coverage == 100%
- privacy_notice_published == true for all active purposes
- retention_compliance_rate >= 0.95

## Compliance Requirements
- GDPR Art.5 principles
- GDPR Art.6 lawful basis
- GDPR Art.9 special categories