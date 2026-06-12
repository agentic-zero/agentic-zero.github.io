# SOP — Record-Keeping and Logging
**Process ID:** EUAIA-ART12
**Framework:** EU AI Act 2024 | **Domain:** EU AI Act
**Generated:** 2026-06-12

## Purpose
Automatic logging requirements for high-risk AI systems to enable post-market monitoring, investigation of incidents and demonstration of compliance with requirements

## Triggers
- High-risk AI inference completion
- Human oversight action submission
- System error or anomaly detection event

## Inputs Required
- AI system outputs
- decision logs
- input data logs
- system events
- human oversight actions

## Process Steps
1. IF log_completeness_rate < 0.99 THEN trigger immediate system alert and halt high-risk inference
2. IF retention_period_exceeded THEN execute automated purge after compliance check

## Expected Outputs
- audit logs
- decision audit trail
- incident records
- compliance evidence
- monitoring reports

## Business Rules
- All high-risk outputs and decisions must be logged within 100ms of generation
- Audit logs must be immutable and stored with SHA-256 hash verification
- Log retention must satisfy GDPR minimum of 5 years or sector-specific requirement

## Exception Handling
- System outage: switch to local buffer mode and backfill logs within 60 seconds of recovery
- Human override: log override reason and operator ID before allowing action

## Success Criteria
- log_completeness_rate == 1.0 for all decisions in 24h window
- incident_traceability_rate >= 0.999 with full decision audit trail
- compliance_evidence generated and exportable in <5 seconds

## Compliance Requirements
- EU AI Act Art.12 mandatory
- GDPR audit logs
- data retention requirements