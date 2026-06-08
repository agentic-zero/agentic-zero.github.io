# SOP — Schedule Excess Product Return Shipment
**Process ID:** SCOR-SR3.4
**Framework:** SCOR | **Domain:** Return
**Generated:** 2026-06-08

## Purpose
Process of planning and scheduling the logistics for returning excess inventory to supplier

## Triggers
- Receipt of ExcessReturnAuthorization with status approved

## Inputs Required
- excess return authorization
- product quantity
- storage location
- carrier options

## Process Steps
1. IF product is perishable THEN enforce expiry compliance check before scheduling
2. IF sector requires cold chain THEN filter CarrierOption for temperature-controlled transport
3. IF shipment is cross-border THEN add customs documentation to ReturnShippingDocument

## Expected Outputs
- return shipment schedule
- carrier booking
- return shipping documents

## Business Rules
- CarrierBooking must be confirmed within 24 hours of ExcessReturnAuthorization receipt
- ReturnShipmentSchedule lead time must not exceed ShipmentLeadTimeKPI target
- All outputs require sector-specific compliance flags to be validated

## Exception Handling
- No valid CarrierOption available: escalate to manual carrier negotiation and log delay in SchedulingEfficiencyKPI
- Missing expiry data on perishable goods: halt scheduling and request updated ExcessReturnAuthorization

## Success Criteria
- ReturnShipmentSchedule status set to confirmed
- CarrierBooking reference generated
- ReturnShippingDocument PDF created and linked
- All KPIs within target thresholds

## Compliance Requirements
- expiry compliance if perishable
- cold chain if required
- customs if cross-border