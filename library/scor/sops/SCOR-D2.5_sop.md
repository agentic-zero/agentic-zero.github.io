# SOP — Build Loads (MTO)
**Process ID:** SCOR-D2.5
**Framework:** SCOR | **Domain:** Deliver
**Generated:** 2026-06-08

## Purpose
Process of building optimized loads for MTO shipments including load planning, weight and dimension optimization, dangerous goods segregation and carrier assignment

## Triggers
- Receipt of ConsolidatedOrder batch from SCOR-D2.4

## Inputs Required
- consolidated orders
- product dimensions and weights
- carrier constraints
- dangerous goods data
- delivery sequence

## Process Steps
1. IF Product contains dangerous goods THEN apply ADR/IMDG segregation rules before adding to LoadPlan
2. IF total weight exceeds CarrierConstraint.max_weight THEN split into multiple LoadPlans
3. IF load utilization < 85% THEN trigger re-optimization or carrier change

## Expected Outputs
- optimized load plans
- carrier assignments
- loading instructions
- dangerous goods manifests

## Business Rules
- LoadPlan.total_weight <= CarrierConstraint.max_weight
- Dangerous goods must be segregated by compatibility class per ADR/IMDG
- LoadPlan must respect DeliverySequence order
- GDPR-compliant data handling for all shipment fields

## Exception Handling
- If optimization rate < 70% after 3 iterations, escalate to manual planner with partial LoadPlan
- If carrier constraints conflict with dangerous goods, reject and return to order consolidation

## Success Criteria
- load optimization rate >= 90%
- dangerous goods compliance rate = 100%
- carrier utilization >= 85%
- all outputs generated without validation errors

## Compliance Requirements
- ADR/IMDG dangerous goods
- carrier weight limits
- customs load requirements
- GDPR shipment data