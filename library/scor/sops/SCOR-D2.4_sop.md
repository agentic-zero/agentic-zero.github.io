# SOP — Consolidate Orders (MTO)
**Process ID:** SCOR-D2.4
**Framework:** SCOR | **Domain:** Deliver
**Generated:** 2026-06-08

## Purpose
Process of consolidating multiple MTO orders for the same customer or delivery destination to optimize shipping costs and delivery efficiency

## Triggers
- New ConfirmedOrder received with status='confirmed'
- DeliverySchedule updated for existing orders

## Inputs Required
- confirmed orders
- delivery schedules
- customer shipping preferences
- logistics options
- cost parameters

## Process Steps
1. IF orders.share(customerId OR deliveryDestination) AND totalCost(sameDestination) < sum(individualCosts) THEN create ConsolidatedShipmentPlan
2. IF LogisticsOption.compliance == 'dangerousGoods' THEN route to separate handling workflow

## Expected Outputs
- consolidated shipment plans
- optimized delivery schedules
- customer notifications
- shipping cost savings

## Business Rules
- Consolidation allowed only for orders with matching customerId or deliveryDestination
- Customer data access must satisfy GDPR compliance flag before consolidation
- ConsolidatedShipmentPlan must reduce total shipping cost by minimum 5% to be valid

## Exception Handling
- Orders with conflicting delivery dates cannot be consolidated: split into separate plans and log exception
- Customs consolidation regulations violated: abort plan and notify compliance officer

## Success Criteria
- ConsolidationRate >= 0.6
- ShippingCostReduction >= 0.05
- CustomerNotification sent within 4 hours of plan creation

## Compliance Requirements
- GDPR customer data
- customs consolidation regulations
- dangerous goods if applicable