# SOP — Record-Keeping and Logging
**Process ID:** EUAIA-ART12
**Framework:** EU AI Act 2024 | **Domain:** EU AI Act
**Generated:** 2026-06-10

## Purpose
Automatic logging requirements for high-risk AI systems to enable post-market monitoring, investigation of incidents and demonstration of compliance with requirements

## Triggers
- High-risk AI system activation
- Post-market monitoring schedule
- Incident report submission

## Inputs Required
- AI system outputs
- decision logs
- input data logs
- system events
- human oversight actions

## Process Steps
1. IF log_completeness_rate < 1.0 THEN trigger retention_check and alert
2. IF incident_detected THEN create Incident_Record and link to Decision_Audit_Trail

## Expected Outputs
- audit logs
- decision audit trail
- incident records
- compliance evidence
- monitoring reports

## Business Rules
- All inputs must be logged with immutable timestamp and hash before any output is produced
- Audit_Log retention must satisfy GDPR and EU AI Act Art.12 minimum periods
- Every Human_Oversight_Action must be recorded with actor_id and timestamp

## Exception Handling
- Non-high-risk systems bypass automatic logging but must still produce manual Compliance_Evidence on request

## Success Criteria
- log_completeness_rate == 1.0
- incident_traceability_rate >= 0.95
- all Audit_Logs retained for required period with zero tampering

## Compliance Requirements
- EU AI Act Art.12 mandatory
- GDPR audit logs
- data retention requirements