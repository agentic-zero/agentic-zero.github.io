# SOP — Schedule Engineer-to-Order Production Activities
**Process ID:** SCOR-M3.1
**Framework:** SCOR | **Domain:** Make
**Generated:** 2026-06-08

## Purpose
Process of scheduling ETO production activities integrating engineering design releases with production planning, managing design changes and coordinating multi-discipline project execution

## Triggers
- New EngineeringRelease published in PLM
- ProjectSchedule baseline approved
- DesignChangeNotice issued with severity >= medium

## Inputs Required
- engineering releases
- project schedules
- resource plans
- design change notices
- subcontractor schedules

## Process Steps
1. IF DesignChangeNotice received AND impact > threshold THEN trigger schedule recalculation and notify stakeholders
2. IF engineering releases missing THEN hold production scheduling and escalate to engineering

## Expected Outputs
- ETO production schedules
- resource allocations
- engineering-production interface plans
- milestone tracking

## Business Rules
- All ETOProductionSchedule entries must reference at least one EngineeringRelease before activation
- ResourceAllocation must not exceed ResourcePlan capacity by more than 5%
- DesignChangeNotice processing must complete within 48 hours for ITAR-controlled items

## Exception Handling
- Major design change (>20% scope) requires full re-baseline of MilestoneTracking and approval from project manager before schedule update
- SubcontractorSchedule conflicts trigger manual override flag and fallback to internal resource buffer

## Success Criteria
- schedule_adherence >= 0.95 measured as (actual vs planned milestone dates)
- engineering_production_interface_efficiency >= 0.90 (interface plan tasks completed on time)
- design_change_impact <= 0.15 (percentage of milestones delayed by changes)

## Compliance Requirements
- defense acquisition regulations
- AS9100 aerospace
- export control ITAR
- project management compliance