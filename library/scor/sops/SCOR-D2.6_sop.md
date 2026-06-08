# SOP — Route Shipments (MTO)
**Process ID:** SCOR-D2.6
**Framework:** SCOR | **Domain:** Deliver
**Generated:** 2026-06-07

## Purpose
Process of selecting optimal routing for MTO shipments including mode selection, carrier booking, route optimization and customs clearance planning

## Triggers
- LoadPlan status = ready AND DeliveryRequirement received

## Inputs Required
- load plans
- delivery requirements
- carrier options
- customs requirements
- cost constraints

## Process Steps
1. IF multiple carrier options exist THEN select lowest cost with on-time KPI >= 95%
2. IF customs requirements flagged THEN generate CustomsDocumentation before booking
3. IF dangerous goods in LoadPlan THEN apply restricted routing mode

## Expected Outputs
- shipment routes
- carrier bookings
- customs documentation
- routing cost analysis

## Business Rules
- CarrierBooking must achieve booking accuracy >= 98%
- ShipmentRoute must satisfy all CostConstraint limits before finalization
- CustomsDocumentation must be validated against export control compliance

## Exception Handling
- IF carrier booking fails THEN fallback to secondary carrier from options list and log accuracy drop
- IF customs clearance rate < 90% THEN escalate to SCOR-E7 and delay departure

## Success Criteria
- on-time shipment departure >= 95%
- routing optimization savings > 0
- customs clearance rate = 100%

## Compliance Requirements
- customs compliance
- export control
- dangerous goods routing
- GDPR shipment data