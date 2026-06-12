# SOP — Post-Market Monitoring
**Process ID:** EUAIA-ART72
**Framework:** EU AI Act 2024 | **Domain:** EU AI Act
**Generated:** 2026-06-12

## Purpose
Post-market monitoring system for high-risk AI including proactive data collection, performance analysis, incident reporting to national authorities and serious incident management

## Triggers
- HighRiskAI_System deployment completion
- New incident report received
- Quarterly monitoring cycle start

## Inputs Required
- deployment performance data
- user feedback
- incident reports
- monitoring metrics
- market surveillance data

## Process Steps
1. IF incident.severity == 'serious' THEN notify National_Authority within 72 hours
2. IF monitoring_coverage < 0.95 THEN expand data collection sources

## Expected Outputs
- post-market monitoring plan
- performance reports
- incident notifications
- corrective actions
- market surveillance data

## Business Rules
- PostMarketMonitoring_Plan must be documented and updated quarterly
- All incidents must be logged with timestamp, severity and root cause
- Corrective_Action effectiveness must exceed 0.8 KPI threshold

## Exception Handling
- If national authority is unreachable, log attempt and retry every 24 hours for 5 days before escalation to EU-level body

## Success Criteria
- incident_detection_rate >= 0.95
- reporting_timeliness <= 72 hours for serious incidents
- corrective_action_effectiveness >= 0.8

## Compliance Requirements
- EU AI Act Art.72 mandatory
- serious incident reporting
- national authority notification