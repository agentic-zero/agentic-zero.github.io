# SOP — Post-Market Monitoring
**Process ID:** EUAIA-ART72
**Framework:** EU AI Act 2024 | **Domain:** EU AI Act
**Generated:** 2026-06-10

## Purpose
Post-market monitoring system for high-risk AI including proactive data collection, performance analysis, incident reporting to national authorities and serious incident management

## Triggers
- New deployment_performance_data received post-deployment
- User feedback volume exceeds threshold of 100 entries/day
- Scheduled daily monitoring_metrics evaluation

## Inputs Required
- deployment performance data
- user feedback
- incident reports
- monitoring metrics
- market surveillance data

## Process Steps
1. IF incident.severity == 'serious' THEN notify NationalAuthority within 72 hours
2. IF monitoring_coverage < 0.95 THEN expand data collection sources
3. IF corrective_action_effectiveness < 0.8 THEN escalate to related_process EUAIA-ART9

## Expected Outputs
- post-market monitoring plan
- performance reports
- incident notifications
- corrective actions
- market surveillance data

## Business Rules
- All serious incidents must be logged with timestamp, severity, and root cause within 24 hours
- Post-market monitoring plan must be updated quarterly using KPI thresholds
- National authority notification is mandatory for any incident causing harm as defined in EU AI Act Art.72

## Exception Handling
- If incident involves defense sector, route notification through SCOR-DIG10 instead of direct NationalAuthority submission
- If data source is unavailable, substitute with ISO42001-10 fallback metrics and log deviation

## Success Criteria
- incident_detection_rate >= 0.95
- reporting_timeliness <= 72 hours for 100% of serious incidents
- corrective_action_effectiveness >= 0.85 measured 30 days post-action

## Compliance Requirements
- EU AI Act Art.72 mandatory
- serious incident reporting
- national authority notification