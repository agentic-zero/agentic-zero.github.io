# SOP — Schedule Engineer-to-Order Product Deliveries
**Process ID:** SCOR-S3.1
**Framework:** SCOR | **Domain:** Source
**Generated:** 2026-06-08

## Purpose
Process of scheduling deliveries for engineer-to-order materials and components aligned to project milestones, managing long-lead-time items and custom-engineered parts

## Triggers
- New or updated ProcurementPlan received
- EngineeringBOM revision released
- ProjectMilestone date changed

## Inputs Required
- project schedules
- engineering BOMs
- supplier engineering lead times
- project milestones
- procurement plans

## Process Steps
1. IF SupplierEngineeringLeadTime > ProjectMilestone.buffer THEN create LongLeadTimeAlert and escalate to procurement
2. IF schedule_variance > 10% THEN trigger re-alignment of ETODeliverySchedule with ProjectSchedule

## Expected Outputs
- ETO delivery schedules
- long-lead-time alerts
- supplier milestone tracking
- procurement status reports

## Business Rules
- All ETO deliveries must reference current EngineeringBOM revision before scheduling
- Long-lead-time items require dual approval from engineering and project management
- Compliance with ITAR/EAR must be validated on every supplier milestone update for defense sector

## Exception Handling
- Supplier provides revised lead time after PO issuance: re-run scheduling and regenerate ETODeliverySchedule within 24 hours
- Milestone date change from customer: propagate change to all dependent ProcurementPlans and issue updated alerts

## Success Criteria
- milestone_adherence >= 95%
- long_lead_time_management_rate >= 98%
- schedule_variance <= 5%

## Compliance Requirements
- defense acquisition regulations
- export control ITAR/EAR
- GDPR if personal data
- project compliance requirements