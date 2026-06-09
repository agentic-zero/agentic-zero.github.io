# SOP — Deviation & OOS Investigation
**Process ID:** BPMN-GXP-003
**Framework:**  | **Domain:** BPMN
**Generated:** 2026-06-09

## Purpose
Deviation and out-of-specification investigation process from detection to closure including immediate containment, investigation, root cause analysis and CAPA

## Triggers
- Deviation Detected event from LIMS, MES or manual entry in Veeva Vault/SAP QM

## Inputs Required
- deviation report
- batch data
- OOS result
- investigation protocol
- regulatory requirements

## Process Steps
1. IF RegulatoryReportable == true THEN create RegulatoryNotification within 24h
2. IF Phase2Required == true THEN execute InvestigationPhase2
3. IF RootCauseFound == false THEN escalate to extended RCA or reject batch
4. IF ProductImpact == true THEN execute ImpactAssessment and set BatchDisposition to rejected

## Expected Outputs
- investigation report
- root cause
- CAPA
- regulatory notification if needed
- batch disposition

## Business Rules
- All deviations must be reported within 24 hours per 21 CFR 211.192
- Root cause must be identified before CAPA definition
- CAPA effectiveness must be verified within 90 days
- Regulatory notifications must be filed within regulatory timelines (e.g., 15 days for FDA)

## Exception Handling
- No root cause identified after Phase2: escalate to management review and document as unknown cause
- Product impact confirmed: force BatchDisposition to rejected and trigger recall assessment
- Regulatory reportable but missed deadline: auto-generate deviation on the deviation process

## Success Criteria
- Deviation status == Closed
- RootCause identified with confidence >= 80%
- CAPA implemented and effectiveness verified
- All regulatory notifications sent on time

## Compliance Requirements
- GxP 21 CFR 211.192
- EU GMP Chapter 6
- ICH Q10
- FDA OOS guidance