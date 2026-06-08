# SOP — Schedule Product Deliveries (MTO)
**Process ID:** SCOR-S2.1
**Framework:** SCOR | **Domain:** Source
**Generated:** 2026-06-07

## Purpose
Process of scheduling inbound material deliveries aligned to make-to-order production schedules, coordinating supplier delivery windows with production start dates

## Triggers
- New or updated ProductionOrder received from planning system
- Change in SupplierCapacity or TransportationSchedule detected

## Inputs Required
- production orders
- supplier lead times
- material requirements
- supplier capacity
- transportation schedules

## Process Steps
1. IF supplier capacity < material requirement THEN generate ExpediteAlert
2. IF production start date - supplier lead time < current date THEN trigger expedite
3. IF transportation schedule conflicts with production window THEN adjust DeliverySchedule or alert

## Expected Outputs
- delivery schedules
- supplier delivery confirmations
- expedite alerts
- schedule compliance reports

## Business Rules
- DeliverySchedule must align supplier delivery window to production start date within 24 hours tolerance
- SupplierDeliveryConfirmation required before 48 hours of scheduled delivery
- Lead time variance must not exceed +/- 10% without ExpediteAlert

## Exception Handling
- Supplier capacity shortfall: auto-create ExpediteAlert and notify procurement
- Transportation delay > 4 hours: recalculate DeliverySchedule and update confirmations
- Missing production order data: hold process and flag for planner review

## Success Criteria
- Schedule adherence rate >= 95%
- Supplier on-time delivery >= 98%
- Expedite rate <= 5%
- Lead time variance <= 10%

## Compliance Requirements
- GxP if pharma
- contractual compliance
- GDPR if personal data