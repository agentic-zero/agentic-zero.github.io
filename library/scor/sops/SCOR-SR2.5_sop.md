# SOP — Return MRO Product to Supplier
**Process ID:** SCOR-SR2.5
**Framework:** SCOR | **Domain:** Return
**Generated:** 2026-06-07

## Purpose
Physical execution of MRO product return to supplier including packaging, shipment and credit confirmation tracking

## Triggers
- receipt of Return Authorization from Supplier
- availability of Packaging and Carrier

## Inputs Required
- MRO shipment schedule
- return authorization
- packaging
- carrier pickup

## Process Steps
1. IF Return Authorization is approved THEN proceed with Packaging and Shipment
2. IF Shipment is delivered THEN confirm Proof of Delivery and issue Credit Confirmation

## Expected Outputs
- returned MRO shipment
- proof of delivery
- credit confirmation

## Business Rules
- rule1: MRO Product return must be authorized by Supplier
- rule2: Packaging must comply with environmental regulations
- rule3: Shipment must be tracked and confirmed by Carrier

## Exception Handling
- exception1: IF Return Authorization is denied THEN notify Supplier and cancel return process
- exception2: IF Shipment is lost or damaged THEN investigate and reship or refund

## Success Criteria
- return completion rate > 90%
- credit recovery rate > 95%
- return cycle time < 30 days

## Compliance Requirements
- chain of custody
- environmental compliance
- customs if cross-border