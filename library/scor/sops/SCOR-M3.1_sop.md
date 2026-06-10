# SOP — Schedule Engineer-to-Order Production Activities
**Process ID:** SCOR-M3.1
**Framework:** SCOR | **Domain:** Make
**Generated:** 2026-06-10

## Purpose
Process of scheduling ETO production activities integrating engineering design releases with production planning, managing design changes and coordinating multi-discipline project execution

## Triggers
- Receipt of EngineeringRelease with status=approved
- ProjectSchedule update with new baseline
- DesignChangeNotice with priority=high

## Inputs Required
- engineering releases
- project schedules
- resource plans
- design change notices
- subcontractor schedules

## Process Steps
1. IF DesignChangeNotice received AND impact > 5% schedule THEN trigger rescheduling and notify related_processes SCOR-M3.2
2. IF subcontractor schedule variance > 10% THEN adjust ResourceAllocation and update MilestoneTracking

## Expected Outputs
- ETO production schedules
- resource allocations
- engineering-production interface plans
- milestone tracking

## Business Rules
- All ETOProductionSchedule must reference compliance_flags ITAR and AS9100 before release
- MilestoneTracking must be updated within 24 hours of EngineeringRelease
- ResourceAllocation cannot exceed ResourcePlan capacity by more than 5% without approval

## Exception Handling
- IF export_control ITAR flag active AND subcontractor is non-US THEN block SubcontractorSchedule integration and route to compliance review
- IF design change frequency > 3 per week THEN freeze ETOProductionSchedule updates for 48 hours

## Success Criteria
- ScheduleAdherenceKPI >= 95%
- DesignChangeImpactKPI <= 0.15
- 100% MilestoneTracking milestones achieved within 3 days of target

## Compliance Requirements
- defense acquisition regulations
- AS9100 aerospace
- export control ITAR
- project management compliance