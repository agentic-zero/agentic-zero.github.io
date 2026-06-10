# SOP — Schedule Engineer-to-Order Product Deliveries
**Process ID:** SCOR-S3.1
**Framework:** SCOR | **Domain:** Source
**Generated:** 2026-06-10

## Purpose
Process of scheduling deliveries for engineer-to-order materials and components aligned to project milestones, managing long-lead-time items and custom-engineered parts

## Triggers
- New or updated ProjectSchedule received from project management system
- EngineeringBOM revision released in PLM system

## Inputs Required
- project schedules
- engineering BOMs
- supplier engineering lead times
- project milestones
- procurement plans

## Process Steps
1. IF SupplierEngineeringLeadTime > ProjectMilestone.buffer_days THEN create LongLeadTimeAlert and notify procurement
2. IF schedule_variance > 10% THEN trigger rescheduling of ETODeliverySchedule

## Expected Outputs
- ETO delivery schedules
- long-lead-time alerts
- supplier milestone tracking
- procurement status reports

## Business Rules
- All ETO delivery schedules must reference latest EngineeringBOM revision before release
- Supplier engineering compliance must be validated against defense acquisition regulations before milestone approval
- Long-lead-time items require dual-source validation if lead time exceeds 90 days

## Exception Handling
- Missing SupplierEngineeringLeadTime: default to 120-day estimate and flag for manual review within 48 hours
- ITAR/EAR restricted item detected: route to compliance officer and halt schedule publication

## Success Criteria
- Milestone adherence >= 95%
- Schedule variance <= 5 days
- Long-lead-time alerts generated for 100% of items exceeding threshold

## Compliance Requirements
- defense acquisition regulations
- export control ITAR/EAR
- GDPR if personal data
- project compliance requirements