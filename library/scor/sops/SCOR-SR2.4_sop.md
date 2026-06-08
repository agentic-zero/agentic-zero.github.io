# SOP — Schedule MRO Return Shipment
**Process ID:** SCOR-SR2.4
**Framework:** SCOR | **Domain:** Return
**Generated:** 2026-06-07

## Purpose
Process of scheduling logistics for MRO product return including carrier selection, packaging and documentation preparation

## Triggers
- MRO return authorization is approved
- Item quantity and weight are available
- Supplier location is available
- Carrier options are available

## Inputs Required
- MRO return authorization
- item quantity and weight
- supplier location
- carrier options

## Process Steps
1. IF MRO return authorization is approved THEN schedule logistics
2. IF carrier options are available THEN select carrier
3. IF item quantity and weight are available THEN prepare packaging and documentation

## Expected Outputs
- MRO shipment schedule
- carrier booking
- return documentation

## Business Rules
- rule1: MRO return shipment must comply with dangerous goods regulations if applicable
- rule2: MRO return shipment must comply with customs regulations if cross-border
- rule3: Carrier selection must be based on scheduling cycle time, return logistics cost, and carrier on-time performance

## Exception Handling
- exception1: IF no carrier options are available THEN notify supplier and request alternative options
- exception2: IF return documentation is incomplete THEN notify supplier and request completion

## Success Criteria
- MRO shipment schedule is created
- Carrier booking is confirmed
- Return documentation is complete
- Scheduling cycle time is within target
- Return logistics cost is within target
- Carrier on-time performance is within target

## Compliance Requirements
- dangerous goods if applicable
- customs compliance if cross-border