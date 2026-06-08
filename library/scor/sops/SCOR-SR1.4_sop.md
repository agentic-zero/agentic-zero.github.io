# SOP — Schedule Defective Product Return Shipment
**Process ID:** SCOR-SR1.4
**Framework:** SCOR | **Domain:** Return
**Generated:** 2026-06-07

## Purpose
Process of scheduling and coordinating logistics for returning defective products to supplier including carrier selection and documentation

## Triggers
- Receipt of Return Authorization from supplier
- Detection of defective product in inventory

## Inputs Required
- return authorization
- product quantity
- supplier address
- carrier contracts

## Process Steps
1. IF Return Authorization is approved THEN create Shipment Schedule
2. IF Carrier contracts are available THEN select Carrier
3. IF Supplier address is valid THEN schedule shipment

## Expected Outputs
- shipment schedule
- carrier booking
- return shipping documentation

## Business Rules
- rule1: Defective Product must have a valid Return Authorization
- rule2: Carrier selection must be based on available contracts and capacity
- rule3: Shipment Schedule must be created within a reasonable timeframe

## Exception Handling
- exception1: Invalid Return Authorization - notify supplier and request correction
- exception2: Carrier unavailability - select alternative carrier or reschedule shipment
- exception3: Invalid Supplier address - notify supplier and request correction

## Success Criteria
- Shipment Schedule is created and confirmed with carrier
- Return Shipping Documentation is generated and sent to supplier
- Defective Product is received by supplier and acknowledged

## Compliance Requirements
- dangerous goods regulations if applicable
- GxP if pharma
- customs compliance if cross-border