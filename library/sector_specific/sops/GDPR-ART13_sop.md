# SOP — GDPR Transparency and Data Subject Rights
**Process ID:** GDPR-ART13
**Framework:** GDPR (EU) 2016/679 | **Domain:** GDPR
**Generated:** 2026-06-10

## Purpose
Transparency obligations and data subject rights management including right to access, rectification, erasure, restriction, portability and objection, including rights related to automated decision-making

## Triggers
- DataSubjectRequest received via webform, email or API
- Scheduled 30-day compliance check on open requests

## Inputs Required
- data subject requests
- personal data inventory
- processing records
- automated decision systems
- retention data

## Process Steps
1. IF request_type == 'access' THEN return PersonalDataInventory copy
2. IF request_type == 'erasure' THEN verify legal_basis != 'legal_obligation' THEN create ErasureRecord
3. IF automated_decision_affected == true THEN generate AutomatedDecisionExplanation before response
4. IF response_time_days > 30 THEN escalate to DPO

## Expected Outputs
- privacy notices
- data subject request responses
- automated decision explanations
- erasure records
- portability exports

## Business Rules
- All responses must be provided within 30 calendar days of request receipt
- PrivacyNotice must include controller identity, processing purposes, legal basis, retention periods and data subject rights
- AutomatedDecisionExplanation must include logic, significance and envisaged consequences
- PortabilityExport must be in machine-readable structured format
- Fulfillment rate must be logged per request for KPI calculation

## Exception Handling
- IF identity_verification fails THEN reject request with 403 and log reason
- IF data volume exceeds 100MB THEN provide secure download link instead of attachment
- IF conflicting legal obligation exists THEN partially refuse erasure and document Article 23 derogation

## Success Criteria
- request_response_time <= 30 days
- rights_fulfillment_rate == 100%
- automated_decision_explainability score >= 0.9
- all outputs generated and stored with audit trail

## Compliance Requirements
- GDPR Art.13-14 information
- GDPR Art.15-22 rights
- GDPR Art.22 automated decisions