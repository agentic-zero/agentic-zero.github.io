# SOP — Schedule Engineer-to-Order Production Activities
**Process ID:** SCOR-M3.1
**Framework:** SCOR | **Domain:** Make
**Generated:** 2026-06-07

## Purpose
Process of scheduling ETO production activities integrating engineering design releases with production planning, managing design changes and coordinating multi-discipline project execution

## Triggers
- Receipt of engineering releases or design change notices from engineering system

## Inputs Required
- engineering releases
- project schedules
- resource plans
- design change notices
- subcontractor schedules

## Process Steps
1. IF DesignChangeNotice received THEN recalculate ETOProductionSchedule and ResourceAllocation within 24 hours
2. IF schedule adherence KPI < 0.9 THEN escalate to related process SCOR-M3.2

## Expected Outputs
- ETO production schedules
- resource allocations
- engineering-production interface plans
- milestone tracking

## Business Rules
- All ETOProductionSchedule outputs must reference compliance_flags: defense acquisition regulations or ITAR before release
- ResourceAllocation must integrate inputs from engineering releases and subcontractor schedules with version control

## Exception Handling
- Unresolved design change after 48 hours: freeze ETOProductionSchedule and notify project manager via milestone tracking

## Success Criteria
- Schedule adherence KPI >= 0.95 AND project milestone achievement = 100% with no open design change impacts

## Compliance Requirements
- defense acquisition regulations
- AS9100 aerospace
- export control ITAR
- project management compliance