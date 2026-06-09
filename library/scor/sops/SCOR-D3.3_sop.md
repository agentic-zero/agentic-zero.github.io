# SOP — Reserve Resources and Determine Delivery Date (ETO)
**Process ID:** SCOR-D3.3
**Framework:** SCOR | **Domain:** Deliver
**Generated:** 2026-06-08

## Purpose
Process of reserving engineering, production and logistics resources for ETO projects and establishing contractual delivery milestones and completion dates

## Triggers
- Receipt of ProjectProposal with status=='approved' AND RiskAdjustedSchedule present

## Inputs Required
- project proposal
- resource availability
- engineering capacity
- subcontractor availability
- risk adjusted schedule

## Process Steps
1. IF ResourceAvailability < required_capacity THEN trigger schedule buffer increase ELSE create ResourceReservation
2. IF SubcontractorAvailability == false THEN evaluate alternative supplier OR extend milestone by risk buffer days

## Expected Outputs
- resource reservations
- project milestones
- contractual delivery schedule
- resource allocation plan

## Business Rules
- All ResourceReservations must include schedule_risk_buffer >= 0.15 of total duration for sector_applicability in ['defense','aerospace']
- ContractualDeliverySchedule must satisfy government_contracting_schedule_compliance flag before output
- ResourceAllocationPlan utilization target >= 0.85 measured by KPI resource_utilization

## Exception Handling
- Missing RiskAdjustedSchedule: default to 20% buffer and log compliance_flag export_control_project_planning
- GDPR project data flag active: anonymize all subcontractor data fields before storing ResourceReservation

## Success Criteria
- ResourceReservation accuracy >= 0.9 per KPI
- All ProjectMilestones have contractual dates with milestone_reliability >= 0.95
- ResourceAllocationPlan generated with utilization KPI recorded

## Compliance Requirements
- government contracting schedule compliance
- export control project planning
- GDPR project data