# SOP — Schedule Excess Product Return Shipment
**Process ID:** SCOR-SR3.4
**Framework:** SCOR | **Domain:** Return
**Generated:** 2026-06-07

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
2. IF cross-border THEN require customs documentation in ReturnShippingDocument
3. IF cold chain required THEN filter CarrierOption to temperature-controlled only

## Expected Outputs
- return shipment schedule
- carrier booking
- return shipping documents

## Business Rules
- ReturnShipmentSchedule must be created within 24 hours of ExcessReturnAuthorization receipt
- CarrierBooking cost must not exceed return logistics cost KPI threshold
- Shipment lead time must be logged for every CarrierBooking

## Exception Handling
- No valid CarrierOption available: escalate to manual review and log failure in scheduling efficiency KPI
- Expiry date within 7 days: block shipment and trigger SCOR-SR3.5 disposal process

## Success Criteria
- ReturnShipmentSchedule status set to confirmed
- CarrierBooking confirmation code generated
- All compliance_flags satisfied and ReturnShippingDocument issued

## Compliance Requirements
- expiry compliance if perishable
- cold chain if required
- customs if cross-border