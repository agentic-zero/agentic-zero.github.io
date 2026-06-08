# SOP — Manage Supply Chain Regulatory Compliance
**Process ID:** SCOR-E8
**Framework:** SCOR | **Domain:** Enable
**Generated:** 2026-06-08

## Purpose
Process of identifying, monitoring and ensuring compliance with all applicable regulations across the supply chain including EU AI Act, GDPR, GxP, customs, environmental and sector-specific requirements

## Triggers
- new regulatory_update received
- scheduled compliance audit
- audit_finding created
- operational_data change affecting compliance_flags

## Inputs Required
- regulatory landscape
- compliance requirements
- audit findings
- regulatory updates
- operational data

## Process Steps
1. IF sector in ['pharma'] THEN enforce GxP flag
2. IF compliance_rate < 1.0 THEN create RemediationPlan
3. IF regulatory_update received THEN refresh compliance_flags

## Expected Outputs
- compliance status reports
- audit trails
- remediation plans
- regulatory filings
- compliance certificates

## Business Rules
- compliance_flags must include EU AI Act, GDPR, ISO 42001, NIST AI RMF for all sectors
- GxP flag required only when sector=pharma
- audit finding resolution time must be logged in audit_trails
- regulatory penalty incidence must remain zero

## Exception Handling
- non-pharma sector: skip GxP checks and set compliance_flags without GxP
- customs regulations apply only for cross-border flows in operational_data

## Success Criteria
- compliance_rate == 1.0
- regulatory_penalty_incidence == 0
- all compliance_certificates issued and audit_trails complete

## Compliance Requirements
- EU AI Act full compliance
- GDPR
- GxP if pharma
- ISO 42001
- NIST AI RMF
- customs regulations
- environmental law