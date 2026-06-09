# SOP — Route Shipments (MTO)
**Process ID:** SCOR-D2.6
**Framework:** SCOR | **Domain:** Deliver
**Generated:** 2026-06-08

## Purpose
Process of selecting optimal routing for MTO shipments including mode selection, carrier booking, route optimization and customs clearance planning

## Triggers
- New LoadPlan received from SCOR-D2.5
- DeliveryRequirement updated with new destination or deadline

## Inputs Required
- load plans
- delivery requirements
- carrier options
- customs requirements
- cost constraints

## Process Steps
1. IF total_cost > CostConstraint.max THEN select alternative CarrierOption with lower cost
2. IF customs_clearance_rate < 0.95 THEN escalate to manual review before booking
3. IF dangerous_goods flag = true THEN apply restricted routing mode and add compliance check

## Expected Outputs
- shipment routes
- carrier bookings
- customs documentation
- routing cost analysis

## Business Rules
- All CarrierBookings must include valid customs documentation before shipment departure
- RouteOptimization must minimize cost while satisfying on-time departure KPI >= 0.98
- GDPR shipment data must be anonymized in RoutingCostAnalysis output

## Exception Handling
- Export control restriction detected: halt CarrierBooking and route to compliance officer for approval
- No valid CarrierOption within cost constraints: trigger fallback to SCOR-D2.7 process

## Success Criteria
- routing_optimization_savings >= target_threshold
- carrier_booking_accuracy == 1.0
- customs_clearance_rate >= 0.98
- on_time_shipment_departure == true

## Compliance Requirements
- customs compliance
- export control
- dangerous goods routing
- GDPR shipment data