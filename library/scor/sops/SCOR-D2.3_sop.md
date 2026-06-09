# SOP — Reserve Resources and Determine Delivery Date (MTO)
**Process ID:** SCOR-D2.3
**Framework:** SCOR | **Domain:** Deliver
**Generated:** 2026-06-08

## Purpose
Process of reserving production capacity, materials and logistics resources for MTO orders and calculating confirmed delivery dates based on actual availability

## Triggers
- receipt of ValidatedOrder with status=approved from SCOR-D2.2

## Inputs Required
- validated order
- capacity availability
- material availability
- routing data
- logistics capacity

## Process Steps
1. IF CapacityAvailability >= order_quantity AND MaterialAvailability = true THEN reserve capacity and calculate date ELSE escalate to related process SCOR-D2.4

## Expected Outputs
- reserved capacity
- confirmed delivery date
- resource allocation
- supply chain commitment

## Business Rules
- rule1: delivery date must be calculated only from actual availability data with cycle time < 4 hours
- rule2: all customer data handling must satisfy GDPR compliance flag before reservation
- rule3: resource utilization KPI must remain >= 85% after allocation

## Exception Handling
- exception: material shortage detected - trigger SCOR-S2.1 and notify customer within 1 hour without committing date
- exception: logistics capacity < required - re-route via SCOR-M2.1 and update allocation

## Success Criteria
- ConfirmedDeliveryDate emitted with commitment_reliability >= 0.95
- ResourceAllocation persisted and utilization KPI updated

## Compliance Requirements
- GDPR customer data
- contractual delivery obligations
- financial commitment compliance