# SOP — Select Carriers and Rate Shipments (MTO)
**Process ID:** SCOR-D2.7
**Framework:** SCOR | **Domain:** Deliver
**Generated:** 2026-06-07

## Purpose
Process of selecting carriers and rating MTO shipments based on service requirements, cost optimization and carrier performance

## Triggers
- routing_plan received from SCOR-D2.6
- MTO order confirmation with shipment details

## Inputs Required
- routing plans
- carrier rate cards
- service requirements
- carrier performance data
- budget constraints

## Process Steps
1. IF carrier_cost <= budget_constraint AND carrier_score >= 0.85 THEN select_carrier
2. IF multiple_carriers_match THEN choose_lowest_cost_carrier
3. IF carrier_compliance_flag == false THEN reject_carrier

## Expected Outputs
- carrier selections
- rated shipments
- carrier performance scorecards
- freight cost records

## Business Rules
- carrier_selection must verify trade_compliance before rating
- freight_cost_record must include GDPR_shipment_data consent flag
- rate_accuracy must be validated against carrier_rate_card within 2% tolerance

## Exception Handling
- no_carrier_meets_requirements: escalate to manual review and log exception in carrier_performance_scorecard
- rate_card_expired: trigger refresh from carrier and pause shipment rating

## Success Criteria
- carrier_selection_accuracy >= 0.95
- freight_cost_per_unit within 5% of target
- all rated_shipments have valid compliance_flags

## Compliance Requirements
- carrier compliance requirements
- customs broker regulations
- GDPR shipment data
- trade compliance