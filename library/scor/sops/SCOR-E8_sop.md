# SOP — Manage Supply Chain Regulatory Compliance
**Process ID:** SCOR-E8
**Framework:** SCOR | **Domain:** Enable
**Generated:** 2026-06-07

## Purpose
Process of identifying, monitoring and ensuring compliance with all applicable regulations across the supply chain including EU AI Act, GDPR, GxP, customs, environmental and sector-specific requirements

## Triggers
- receipt of regulatory_update
- scheduled compliance audit
- new operational_data ingestion
- related_process completion (SCOR-E1, SCOR-E3, SCOR-E9, SCOR-S1.5)

## Inputs Required
- regulatory landscape
- compliance requirements
- audit findings
- regulatory updates
- operational data

## Process Steps
1. IF sector == 'pharma' THEN activate GxP flag and require GxP compliance check
2. IF new regulatory update received THEN trigger compliance gap analysis within 24 hours
3. IF audit finding severity == 'critical' THEN escalate to remediation plan within 48 hours

## Expected Outputs
- compliance status reports
- audit trails
- remediation plans
- regulatory filings
- compliance certificates

## Business Rules
- compliance_rate must be >= 0.98
- audit finding resolution time must be <= 30 days
- regulatory penalty incidence must be 0
- all active ComplianceFlags must have corresponding audit trails

## Exception Handling
- IF conflicting regulations detected (e.g. GDPR vs local law) THEN apply strictest requirement and log exception with legal review flag
- IF sector applicability changes mid-process THEN re-evaluate all ComplianceFlags and regenerate compliance status report

## Success Criteria
- compliance_rate >= 0.98
- all audit_findings resolved within SLA
- compliance_certificates issued for all active ComplianceFlags
- zero regulatory penalties recorded

## Compliance Requirements
- EU AI Act full compliance
- GDPR
- GxP if pharma
- ISO 42001
- NIST AI RMF
- customs regulations
- environmental law