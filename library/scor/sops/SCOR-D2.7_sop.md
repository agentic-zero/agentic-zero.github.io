# SOP — Select Carriers and Rate Shipments (MTO)
**Process ID:** SCOR-D2.7
**Framework:** SCOR | **Domain:** Deliver
**Generated:** 2026-06-08

## Purpose
Process of selecting carriers and rating MTO shipments based on service requirements, cost optimization and carrier performance

## Triggers
- new RoutingPlan received from SCOR-D2.6
- updated CarrierPerformanceData available

## Inputs Required
- routing plans
- carrier rate cards
- service requirements
- carrier performance data
- budget constraints

## Process Steps
1. IF carrier_performance_score >= 0.85 AND freight_cost_per_unit <= budget_constraint THEN create CarrierSelection
2. IF multiple carriers meet criteria THEN rank by carrier_selection_accuracy KPI and select top 2

## Expected Outputs
- carrier selections
- rated shipments
- carrier performance scorecards
- freight cost records

## Business Rules
- carrier_selection must satisfy carrier_compliance_requirements before RatedShipment creation
- rate_accuracy must be validated against carrier_rate_cards within 2% tolerance
- GDPR_shipment_data must be anonymized in all FreightCostRecord outputs

## Exception Handling
- IF no carrier meets budget_constraint THEN flag for manual review and log exception in CarrierPerformanceScorecard
- IF customs_broker_regulations violated THEN halt process and trigger SCOR-E6 compliance check

## Success Criteria
- CarrierSelection created for 100% of shipments with carrier_selection_accuracy >= 0.9
- FreightCostRecord generated with rate_accuracy >= 0.95

## Compliance Requirements
- carrier compliance requirements
- customs broker regulations
- GDPR shipment data
- trade compliance