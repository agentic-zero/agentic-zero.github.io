# SOP — Warehouse Outbound Operations
**Process ID:** BPMN-WMS-002
**Framework:**  | **Domain:** BPMN
**Generated:** 2026-06-08

## Purpose
Warehouse outbound process from order release to shipment dispatch including picking, packing, labeling, loading and documentation

## Triggers
- Order Released for Picking event from sales order system

## Inputs Required
- sales orders
- pick lists
- inventory data
- carrier booking
- packaging specs

## Process Steps
1. IF Pick Complete? THEN Verify Pick ELSE return to Pick Products
2. IF Quality Check OK? THEN Pack Shipment ELSE reject pick
3. IF Hazardous Goods? THEN apply special labeling ELSE standard Label & Document
4. IF Cross-dock? THEN bypass staging ELSE Stage for Loading

## Expected Outputs
- picked orders
- packed shipments
- shipping documents
- dispatched vehicle

## Business Rules
- Pick accuracy must exceed 99.5% before Pack Shipment
- All shipments require carrier booking before Load Vehicle
- GDPR shipment data must be anonymized after Dispatch
- GxP compliance required for pharma sector

## Exception Handling
- Hazardous Goods? routes to special handling lane with extra documentation
- Cross-dock? skips Stage for Loading and goes direct to Load Vehicle
- Quality Check failure triggers re-pick and logs KPI impact

## Success Criteria
- Shipment Dispatched status reached
- pick_accuracy >= 99.5
- on-time dispatch = true
- all lines fulfilled

## Compliance Requirements
- dangerous goods
- GxP if pharma
- customs export
- GDPR shipment data