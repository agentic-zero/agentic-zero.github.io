# SOP — Human Oversight
**Process ID:** EUAIA-ART14
**Framework:** EU AI Act 2024 | **Domain:** EU AI Act
**Generated:** 2026-06-10

## Purpose
Human oversight measures for high-risk AI systems enabling human monitoring, understanding, override and intervention capabilities throughout the AI system operation

## Triggers
- HighRiskAISystem deployment or restart
- Receipt of new AI system output batch
- Scheduled oversight protocol evaluation every 24 hours

## Inputs Required
- AI system outputs
- oversight protocols
- human reviewer assignments
- override mechanisms
- escalation rules

## Process Steps
1. IF AI system output anomaly score > 0.7 THEN trigger HumanReviewer intervention
2. IF intervention response time > 300 seconds THEN escalate via EscalationRule
3. IF override utilization rate < 0.05 THEN adjust OversightProtocol

## Expected Outputs
- human oversight records
- override logs
- intervention records
- oversight effectiveness metrics

## Business Rules
- Human oversight must remain active for 100% of HighRiskAISystem operation time
- Every override action must be logged with reviewer_id, timestamp, and justification
- OversightEffectivenessMetric must be computed daily using coverage, response_time, and intervention_success

## Exception Handling
- IF system is in maintenance mode THEN human oversight coverage requirement is waived for that period with audit log entry
- IF no HumanReviewer available within SLA THEN automated safe-state shutdown is permitted

## Success Criteria
- human oversight coverage >= 0.99
- intervention response time <= 180 seconds (p95)
- override logs complete with 100% required fields

## Compliance Requirements
- EU AI Act Art.14 mandatory
- human-in-the-loop requirements
- GDPR automated decision Art.22