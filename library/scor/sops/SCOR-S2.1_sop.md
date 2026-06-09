# SOP — Schedule Product Deliveries (MTO)
**Process ID:** SCOR-S2.1
**Framework:** SCOR | **Domain:** Source
**Generated:** 2026-06-08

## Purpose
Process of scheduling inbound material deliveries aligned to make-to-order production schedules, coordinating supplier delivery windows with production start dates

## Triggers
- New or changed ProductionOrder published from planning system
- Daily batch update of supplier_lead_times or capacities

## Inputs Required
- production orders
- supplier lead times
- material requirements
- supplier capacity
- transportation schedules

## Process Steps
1. IF supplier_lead_time + transport_days > production_start_date THEN create ExpediteAlert and notify sourcing
2. IF supplier_capacity < material_requirement_qty THEN flag alternative_supplier and log exception
3. IF transportation_schedule.conflict == true THEN recalculate delivery_window with 1-day buffer

## Expected Outputs
- delivery schedules
- supplier delivery confirmations
- expedite alerts
- schedule compliance reports

## Business Rules
- DeliverySchedule.delivery_date must be <= ProductionOrder.start_date - 1 day
- All SupplierConfirmation must be received >= 48 hours before scheduled delivery
- Schedule must enforce contractual lead times from Supplier master data
- Apply GxP validation steps if sector == pharma

## Exception Handling
- SupplierCapacity shortfall: auto-create SCOR-S1.1 alternative sourcing request and pause schedule
- GDPR personal data flag: mask supplier contact fields before storing ScheduleComplianceReport
- Transportation delay > 24h: regenerate DeliverySchedule and increment expedite_rate KPI

## Success Criteria
- schedule_adherence_rate >= 0.98
- supplier_on_time_delivery == 1.0 for all confirmed deliveries
- expedite_rate <= 0.05
- all outputs generated with zero missing SupplierConfirmation

## Compliance Requirements
- GxP if pharma
- contractual compliance
- GDPR if personal data