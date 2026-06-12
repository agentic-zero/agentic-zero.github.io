# SOP — Human Oversight
**Process ID:** EUAIA-ART14
**Framework:** EU AI Act 2024 | **Domain:** EU AI Act
**Generated:** 2026-06-12

## Purpose
Human oversight measures for high-risk AI systems enabling human monitoring, understanding, override and intervention capabilities throughout the AI system operation

## Triggers
- New high-risk AI_System_Output received
- Oversight_Protocol scheduled interval reached
- Escalation_Rule condition met

## Inputs Required
- AI system outputs
- oversight protocols
- human reviewer assignments
- override mechanisms
- escalation rules

## Process Steps
1. IF AI_System_Output.confidence < Oversight_Protocol.threshold THEN assign Human_Reviewer via Escalation_Rule
2. IF Human_Reviewer initiates override THEN activate Override_Mechanism and create Override_Log

## Expected Outputs
- human oversight records
- override logs
- intervention records
- oversight effectiveness metrics

## Business Rules
- Human_Oversight_Record must be created for every high-risk AI_System_Output per EU AI Act Art.14
- Intervention response time must be logged and <= SLA defined in Oversight_Protocol
- All Override_Log entries require reviewer_id and timestamp

## Exception Handling
- IF no Human_Reviewer available THEN pause AI system and trigger safe-mode fallback
- IF GDPR Art.22 automated decision detected THEN force mandatory human review regardless of confidence

## Success Criteria
- human_oversight_coverage >= 0.99
- intervention_response_time <= Oversight_Protocol.max_response_seconds
- 100% of overrides have corresponding Override_Log and Intervention_Record

## Compliance Requirements
- EU AI Act Art.14 mandatory
- human-in-the-loop requirements
- GDPR automated decision Art.22