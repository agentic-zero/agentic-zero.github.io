# SOP — Reserve Resources and Determine Delivery Date (MTO)
**Process ID:** SCOR-D2.3
**Framework:** SCOR | **Domain:** Deliver
**Generated:** 2026-06-07

## Purpose
Process of reserving production capacity, materials and logistics resources for MTO orders and calculating confirmed delivery dates based on actual availability

## Triggers
- receipt of validated_order with status=approved

## Inputs Required
- validated order
- capacity availability
- material availability
- routing data
- logistics capacity

## Process Steps
1. IF CapacityAvailability >= order_quantity AND MaterialAvailability >= order_quantity THEN reserve_capacity ELSE calculate_next_available_slot
2. IF LogisticsCapacity < required_transport THEN delay_delivery_date_by_days(3)

## Expected Outputs
- reserved capacity
- confirmed delivery date
- resource allocation
- supply chain commitment

## Business Rules
- resource_reservation_accuracy >= 0.95
- delivery_date_confirmation_cycle_time <= 4 hours
- GDPR: mask customer_data fields before storage
- contractual_delivery_obligations: commit only if all inputs validated

## Exception Handling
- material shortage: escalate to SCOR-S2.1 and return partial allocation
- capacity conflict with SCOR-M2.1: prioritize by commitment_reliability score

## Success Criteria
- SupplyChainCommitment.status == committed
- ConfirmedDeliveryDate within original customer window
- resource_utilization >= 0.85

## Compliance Requirements
- GDPR customer data
- contractual delivery obligations
- financial commitment compliance