# SOP — Human Oversight
**Process ID:** EUAIA-ART14
**Framework:** EU AI Act 2024 | **Domain:** EU AI Act
**Generated:** 2026-06-10

## Purpose
Human oversight measures for high-risk AI systems enabling human monitoring, understanding, override and intervention capabilities throughout the AI system operation

## Triggers
- AI_System output received
- High-risk AI system deployment event
- Scheduled oversight audit timer

## Inputs Required
- AI system outputs
- oversight protocols
- human reviewer assignments
- override mechanisms
- escalation rules

## Process Steps
1. IF AI_System output confidence < 0.85 OR risk_score > threshold THEN escalate to Human_Reviewer
2. IF Human_Reviewer response_time > 300 seconds THEN auto-apply Override_Mechanism
3. IF override utilized THEN log Override_Log and update oversight_effectiveness metric

## Expected Outputs
- human oversight records
- override logs
- intervention records
- oversight effectiveness metrics

## Business Rules
- Human_Reviewer must be assigned before AI_System enters production
- All interventions require human confirmation within SLA of 5 minutes
- Override utilization rate must be logged for every high-risk decision
- GDPR Art.22 automated decision flag must be set when no human intervention occurs

## Exception Handling
- IF sector is defense AND classified mode active THEN allow 30-minute delayed review with post-hoc audit
- IF automation_potential > 0.8 AND KPI oversight_effectiveness > 0.95 THEN reduce human coverage to 60% with documented approval

## Success Criteria
- human_oversight_coverage >= 0.95
- intervention_response_time <= 300 seconds
- override_utilization_rate logged for 100% of escalated cases
- oversight_effectiveness metric >= 0.9

## Compliance Requirements
- EU AI Act Art.14 mandatory
- human-in-the-loop requirements
- GDPR automated decision Art.22