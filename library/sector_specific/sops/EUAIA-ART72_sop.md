# SOP — Post-Market Monitoring
**Process ID:** EUAIA-ART72
**Framework:** EU AI Act 2024 | **Domain:** EU AI Act
**Generated:** 2026-06-10

## Purpose
Post-market monitoring system for high-risk AI including proactive data collection, performance analysis, incident reporting to national authorities and serious incident management

## Triggers
- new deployment_performance_data arrival
- user_feedback containing incident keyword
- scheduled daily monitoring job
- external market_surveillance_data update

## Inputs Required
- deployment performance data
- user feedback
- incident reports
- monitoring metrics
- market surveillance data

## Process Steps
1. IF incident.severity == 'serious' THEN trigger notification within 24 hours to NationalAuthority
2. IF monitoring_coverage < 0.95 THEN expand data collection sources
3. IF corrective_action_effectiveness < 0.8 THEN escalate to related_process EUAIA-ART9

## Expected Outputs
- post-market monitoring plan
- performance reports
- incident notifications
- corrective actions
- market surveillance data

## Business Rules
- EU AI Act Art.72 mandatory: all high-risk AI must maintain post-market monitoring plan
- serious incident reporting: notify national authority within regulatory deadline
- report timeliness KPI must be logged with timestamp for every notification

## Exception Handling
- non-high-risk AI systems: skip mandatory notification but retain internal incident log for 5 years
- defense sector: route notifications through SCOR-DIG10 instead of direct national authority

## Success Criteria
- incident_detection_rate >= 0.95
- reporting_timeliness <= regulatory_deadline_hours
- corrective_action_effectiveness >= 0.8 measured 30 days post-action

## Compliance Requirements
- EU AI Act Art.72 mandatory
- serious incident reporting
- national authority notification