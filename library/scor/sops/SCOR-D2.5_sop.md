# SOP — Build Loads (MTO)
**Process ID:** SCOR-D2.5
**Framework:** SCOR | **Domain:** Deliver
**Generated:** 2026-06-07

## Purpose
Process of building optimized loads for MTO shipments including load planning, weight and dimension optimization, dangerous goods segregation and carrier assignment

## Triggers
- Receipt of consolidated orders from SCOR-D2.4
- Update to product master or carrier constraints

## Inputs Required
- consolidated orders
- product dimensions and weights
- carrier constraints
- dangerous goods data
- delivery sequence

## Process Steps
1. IF Product contains dangerous goods THEN apply ADR/IMDG segregation rules before adding to LoadPlan
2. IF Carrier weight or dimension limit exceeded THEN split LoadPlan and reassign Carrier
3. IF delivery sequence conflicts with load stability THEN reorder sequence and re-optimize LoadPlan

## Expected Outputs
- optimized load plans
- carrier assignments
- loading instructions
- dangerous goods manifests

## Business Rules
- Load optimization rate must exceed 85% by volume and weight
- Carrier utilization must be >= 75% before final assignment
- All dangerous goods must have compliant manifests before carrier assignment
- Total load weight must not exceed carrier limit by more than 0 kg

## Exception Handling
- Missing product dimensions: flag order and route to manual review queue
- No carrier meets constraints: trigger fallback to SCOR-D2.6 and log KPI violation

## Success Criteria
- All outputs generated with load optimization rate >= 85%
- dangerous goods compliance rate = 100%
- carrier assignments accepted by carriers

## Compliance Requirements
- ADR/IMDG dangerous goods
- carrier weight limits
- customs load requirements
- GDPR shipment data