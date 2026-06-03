# SOP — Schedule and Issue Purchase Orders
**Process ID:** SCOR-S1.1
**Framework:** SCOR | **Domain:** Source
**Generated:** 2026-06-03

## Purpose
Process of creating and issuing purchase orders to suppliers based on supply chain requirements

## Triggers
- update to Supply Chain Requirements
- low Inventory levels
- scheduled Purchase Order review

## Inputs Required
- supply chain requirements
- supplier information
- inventory data

## Process Steps
1. IF Supplier Information is incomplete THEN request additional information
2. IF Inventory levels are below threshold THEN create Purchase Order
3. IF Supply Chain Requirements change THEN update Purchase Order

## Expected Outputs
- purchase orders
- supplier acknowledgments

## Business Rules
- rule1: Purchase Orders must be issued within 24 hours of Supply Chain Requirements update
- rule2: Suppliers must acknowledge Purchase Orders within 48 hours
- rule3: Inventory levels must be updated in real-time

## Exception Handling
- exception1: Supplier is unavailable, THEN find alternative Supplier
- exception2: Inventory levels are inconsistent, THEN investigate and correct
- exception3: Supply Chain Requirements are unclear, THEN clarify with stakeholders

## Success Criteria
- Purchase Order is issued and acknowledged by Supplier
- Inventory levels are updated and consistent
- Supply Chain Requirements are met

## Compliance Requirements
- GxP if pharma
- GDP if distribution