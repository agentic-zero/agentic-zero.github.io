# SOP — Performance Evaluation — Monitoring and Internal Audit
**Process ID:** ISO9001-9
**Framework:** ISO 9001:2015 | **Domain:** ISO 9001
**Generated:** 2026-06-12

## Purpose
Monitoring, measurement, analysis and evaluation of QMS performance including customer satisfaction, internal audit program and management review

## Triggers
- quarterly scheduled timer
- annual management review calendar event
- regulatory or customer audit notification

## Inputs Required
- KPI data
- customer feedback
- audit findings
- process performance data
- supplier performance data

## Process Steps
1. IF audit_completion_rate < 0.95 THEN escalate to management and reschedule audits
2. IF customer_satisfaction_score < 80 THEN create Improvement_Action and link to related_processes

## Expected Outputs
- performance reports
- audit reports
- management review minutes
- improvement actions
- customer satisfaction data

## Business Rules
- audit independence: auditor must not audit own process or department
- finding_closure_rate must reach 100% within 30 days or escalate
- all performance data must be retained for minimum 3 years per ISO 9001 Clause 9

## Exception Handling
- missing KPI data source: substitute with manual validated entry and flag for automation review
- independence conflict detected: assign external or cross-department auditor and document justification

## Success Criteria
- audit_completion_rate >= 0.95 AND finding_closure_rate >= 0.9 AND customer_satisfaction_score >= 80

## Compliance Requirements
- ISO 9001:2015 Clause 9
- internal audit independence
- GDPR audit data