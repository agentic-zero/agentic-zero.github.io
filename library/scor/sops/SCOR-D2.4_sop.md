# SOP — Consolidate Orders (MTO)
**Process ID:** SCOR-D2.4
**Framework:** SCOR | **Domain:** Deliver
**Generated:** 2026-06-07

## Purpose
Process of consolidating multiple MTO orders for the same customer or delivery destination to optimize shipping costs and delivery efficiency

## Triggers
- New ConfirmedOrder received that matches existing open orders on customer_id or delivery_destination

## Inputs Required
- confirmed orders
- delivery schedules
- customer shipping preferences
- logistics options
- cost parameters

## Process Steps
1. IF orders share customer_id OR delivery_destination AND delivery_window_overlap >= 24h THEN consolidate
2. IF projected_cost_savings >= cost_threshold THEN approve consolidation ELSE keep separate

## Expected Outputs
- consolidated shipment plans
- optimized delivery schedules
- customer notifications
- shipping cost savings

## Business Rules
- Only consolidate orders with status='confirmed'
- Apply GDPR masking to all customer data in ConsolidatedShipmentPlan
- Dangerous goods flag requires separate shipment unless hazmat certification present

## Exception Handling
- Mismatched delivery windows > 48h: split into separate shipments and log reason
- Customs consolidation regulations violated: flag for manual review and block auto-consolidation

## Success Criteria
- consolidation_rate >= 0.7
- shipping_cost_reduction >= 0.15
- customer_notification_sent within 4h of plan creation

## Compliance Requirements
- GDPR customer data
- customs consolidation regulations
- dangerous goods if applicable