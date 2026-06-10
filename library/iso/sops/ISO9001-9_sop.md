# SOP — Performance Evaluation — Monitoring and Internal Audit
**Process ID:** ISO9001-9
**Framework:** ISO 9001:2015 | **Domain:** ISO 9001
**Generated:** 2026-06-10

## Purpose
Monitoring, measurement, analysis and evaluation of QMS performance including customer satisfaction, internal audit program and management review

## Triggers
- quarterly scheduled job on first business day of quarter
- manual trigger via management review request

## Inputs Required
- KPI data
- customer feedback
- audit findings
- process performance data
- supplier performance data

## Process Steps
1. IF audit_completion_rate < 0.9 THEN escalate to management review
2. IF finding_closure_rate < 0.8 THEN create corrective action within 14 days
3. IF customer_satisfaction_score < 3.5 THEN trigger root cause analysis

## Expected Outputs
- performance reports
- audit reports
- management review minutes
- improvement actions
- customer satisfaction data

## Business Rules
- audit_completion_rate must be >= 0.95 per quarter
- internal_audit_independence must be enforced (no auditor audits own process)
- all GDPR-related audit data must be anonymized before storage

## Exception Handling
- If supplier_performance_data is missing, use last 3 months average and flag as incomplete
- If customer feedback volume < 50 responses, apply statistical weighting before scoring

## Success Criteria
- audit_completion_rate >= 0.95
- finding_closure_rate >= 0.85 within SLA
- all outputs generated and stored with timestamp

## Compliance Requirements
- ISO 9001:2015 Clause 9
- internal audit independence
- GDPR audit data