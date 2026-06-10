# SOP — Record-Keeping and Logging
**Process ID:** EUAIA-ART12
**Framework:** EU AI Act 2024 | **Domain:** EU AI Act
**Generated:** 2026-06-10

## Purpose
Automatic logging requirements for high-risk AI systems to enable post-market monitoring, investigation of incidents and demonstration of compliance with requirements

## Triggers
- AI system inference call
- System event (error, timeout, drift detection)
- Human oversight action submission

## Inputs Required
- AI system outputs
- decision logs
- input data logs
- system events
- human oversight actions

## Process Steps
1. IF log_completeness_rate < 1.0 THEN trigger_alert_and_block_deployment
2. IF retention_period_days < regulatory_minimum THEN extend_storage_and_notify
3. IF incident_traceability_rate < 0.99 THEN initiate_manual_audit

## Expected Outputs
- audit logs
- decision audit trail
- incident records
- compliance evidence
- monitoring reports

## Business Rules
- Every AI system output MUST create a LogRecord with timestamp, input_hash, output, and model_version
- All LogRecords MUST be immutable and stored with cryptographic hash chain
- HumanOversightAction MUST be logged within 100ms of occurrence
- Logs MUST be retained for minimum 10 years or as per sector regulation

## Exception Handling
- IF system experiences total storage failure THEN switch to emergency_read_only_mode and alert regulator within 1 hour
- IF data contains personal data under GDPR THEN apply anonymization before long-term retention

## Success Criteria
- log_completeness_rate == 1.0 for all inference calls in 24h window
- incident_traceability_rate >= 0.99 measured by successful root-cause queries
- log_retention_compliance == true verified by automated retention audit

## Compliance Requirements
- EU AI Act Art.12 mandatory
- GDPR audit logs
- data retention requirements