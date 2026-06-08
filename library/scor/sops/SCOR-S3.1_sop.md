# SOP — Schedule Engineer-to-Order Product Deliveries
**Process ID:** SCOR-S3.1
**Framework:** SCOR | **Domain:** Source
**Generated:** 2026-06-07

## Purpose
Process of scheduling deliveries for engineer-to-order materials and components aligned to project milestones, managing long-lead-time items and custom-engineered parts

## Triggers
- new or updated ProjectSchedule received
- EngineeringBOM revision published
- ProcurementPlan approved for ETO items

## Inputs Required
- project schedules
- engineering BOMs
- supplier engineering lead times
- project milestones
- procurement plans

## Process Steps
1. IF SupplierEngineeringLeadTime > ProjectMilestone.buffer THEN create LongLeadTimeAlert
2. IF scheduleVariance > 10% THEN update ETODeliverySchedule and notify supplier

## Expected Outputs
- ETO delivery schedules
- long-lead-time alerts
- supplier milestone tracking
- procurement status reports

## Business Rules
- ETODeliverySchedule must reference all EngineeringBOM items with lead times > 90 days
- SupplierMilestoneTracking must record compliance with defense acquisition regulations and ITAR/EAR
- milestone adherence KPI must be calculated daily from ProjectMilestone dates

## Exception Handling
- Missing SupplierEngineeringLeadTime: default to 180 days and flag for manual review
- Export-controlled item without ITAR/EAR flag: block ETODeliverySchedule creation until compliance added

## Success Criteria
- milestone adherence >= 95%
- long-lead-time management rate = 100% of items flagged before milestone
- schedule variance <= 5%

## Compliance Requirements
- defense acquisition regulations
- export control ITAR/EAR
- GDPR if personal data
- project compliance requirements