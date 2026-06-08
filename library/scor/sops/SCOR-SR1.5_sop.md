# SOP — Return Defective Product to Supplier
**Process ID:** SCOR-SR1.5
**Framework:** SCOR | **Domain:** Return
**Generated:** 2026-06-07

## Purpose
Physical execution of returning defective products to supplier including packaging, labeling, handover to carrier and shipment tracking

## Triggers
- receipt of Defective Product
- approval of Return Authorization

## Inputs Required
- shipment schedule
- return authorization
- packaging materials
- carrier pickup

## Process Steps
1. IF Defective Product is received THEN initiate Return Authorization
2. IF Return Authorization is approved THEN schedule Carrier pickup
3. IF Returned Shipment is delivered THEN generate Proof of Delivery

## Expected Outputs
- returned shipment
- proof of delivery
- credit note request

## Business Rules
- rule1: Defective Product must be packaged with correct Packaging Materials
- rule2: Return Authorization must be obtained before returning Defective Product
- rule3: Carrier must be notified of Shipment Schedule

## Exception Handling
- IF Carrier fails to pick up Returned Shipment THEN notify Supplier and reschedule pickup
- IF Proof of Delivery is not received THEN investigate and resolve issue

## Success Criteria
- Returned Shipment is delivered to Supplier
- Proof of Delivery is received
- Credit Note Request is generated

## Compliance Requirements
- GxP if pharma
- chain of custody documentation
- customs if cross-border