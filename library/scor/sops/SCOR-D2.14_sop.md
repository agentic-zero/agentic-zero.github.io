# SOP — Install Product (MTO)
**Process ID:** SCOR-D2.14
**Framework:** SCOR | **Domain:** Deliver
**Generated:** 2026-06-08

## Purpose
Process of installing MTO products at customer site including site preparation support, installation coordination, commissioning and handover

## Triggers
- delivered_product received AND site_readiness_data.is_ready == true

## Inputs Required
- delivered product
- installation instructions
- site readiness data
- installation team schedule
- commissioning plan

## Process Steps
1. IF SiteReadinessData.is_ready == true AND InstallationTeamSchedule.confirmed == true THEN start installation ELSE delay and notify scheduler
2. IF first_time_installation_success == false THEN trigger rework and update KPI

## Expected Outputs
- installed product
- commissioning records
- customer training completion
- warranty initiation

## Business Rules
- installation must complete within scheduled window to meet on-time_rate KPI
- all compliance_flags (site_safety_regulations, equipment_installation_certifications) must be validated before handover
- customer_training_completion must be recorded before warranty_initiation

## Exception Handling
- site not ready: pause process and reschedule using installation_team_schedule
- GDPR personal data detected: require explicit consent record before proceeding with commissioning

## Success Criteria
- installation_on_time_rate == true
- commissioning_cycle_time <= planned_duration
- first_time_installation_success_rate == true
- customer_handover_satisfaction >= 4.5/5

## Compliance Requirements
- site safety regulations
- equipment installation certifications
- GDPR if personal data at site
- warranty compliance