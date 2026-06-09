# SOP — Schedule Make-to-Order Production Activities
**Process ID:** SCOR-M2.1
**Framework:** SCOR | **Domain:** Make
**Generated:** 2026-06-08

## Purpose
Process of scheduling MTO production activities against customer orders, allocating capacity and sequencing work orders to meet customer delivery commitments

## Triggers
- New or updated CustomerOrder received
- CapacityPlan or EquipmentSchedule changed
- MaterialAvailability updated

## Inputs Required
- customer orders
- capacity plans
- material availability
- routing data
- equipment schedules

## Process Steps
1. IF material_availability.quantity < work_order.required_qty THEN hold release and escalate to procurement
2. IF capacity_utilization > 0.9 THEN sequence by customer_priority DESC then due_date ASC
3. IF routing_data.changeover_time > 4h THEN batch similar orders before sequencing

## Expected Outputs
- MTO production schedules
- work order releases
- capacity commitments
- delivery date confirmations

## Business Rules
- MTOProductionSchedule must confirm capacity_commitment before releasing any WorkOrder
- All WorkOrders must have delivery_confirmation timestamp before customer commit
- Schedule must achieve on_time_delivery >= 0.95 and schedule_adherence >= 0.92

## Exception Handling
- Rush customer_order with priority=1 overrides standard sequencing but requires documented capacity override approval
- EquipmentSchedule downtime > 2h triggers rescheduling of affected WorkOrders within 4h

## Success Criteria
- MTOProductionSchedule generated with all KPIs above thresholds
- WorkOrder releases created and capacity_commitments recorded
- Delivery date confirmations sent within SLA

## Compliance Requirements
- GxP batch records if pharma
- ISO 9001 production planning
- GDPR customer data