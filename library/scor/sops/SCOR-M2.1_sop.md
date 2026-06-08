# SOP — Schedule Make-to-Order Production Activities
**Process ID:** SCOR-M2.1
**Framework:** SCOR | **Domain:** Make
**Generated:** 2026-06-07

## Purpose
Process of scheduling MTO production activities against customer orders, allocating capacity and sequencing work orders to meet customer delivery commitments

## Triggers
- New or updated CustomerOrder received from order management system
- Daily batch of capacity plans refreshed from ERP

## Inputs Required
- customer orders
- capacity plans
- material availability
- routing data
- equipment schedules

## Process Steps
1. IF material_availability.status == 'available' AND capacity_plan.utilization < 0.85 THEN release WorkOrder
2. IF routing_data.setup_time + processing_time > customer_order.due_date THEN escalate to related_process SCOR-M2.2

## Expected Outputs
- MTO production schedules
- work order releases
- capacity commitments
- delivery date confirmations

## Business Rules
- MTOProductionSchedule must achieve schedule_adherence >= 0.95
- WorkOrder release requires ISO 9001 documented approval
- GDPR customer data must be anonymized in DeliveryConfirmation

## Exception Handling
- Pharma sector: require GxP batch record attachment before WorkOrder release or block schedule
- Capacity_utilization > 0.95: auto-trigger related_process SCOR-P1.3 for overtime approval

## Success Criteria
- schedule_adherence >= 0.95
- on_time_delivery >= 0.98
- capacity_utilization between 0.70-0.90
- order_cycle_time <= customer_order.lead_time

## Compliance Requirements
- GxP batch records if pharma
- ISO 9001 production planning
- GDPR customer data