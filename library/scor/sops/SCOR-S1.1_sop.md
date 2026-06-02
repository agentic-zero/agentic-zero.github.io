# SOP — Schedule and Issue Purchase Orders
**Process ID:** SCOR-S1.1
**Framework:** SCOR | **Domain:** Source
**Generated:** 2026-06-02

## Purpose
Process of creating and issuing purchase orders to suppliers based on supply chain requirements

## Triggers
- update to Supply Chain Requirements
- low Inventory levels

## Inputs Required
- supply chain requirements
- supplier information
- inventory data

## Process Steps
1. IF Supplier Information is incomplete THEN request additional information
2. IF Inventory levels are below threshold THEN create Purchase Order

## Expected Outputs
- purchase orders
- supplier acknowledgments

## Business Rules
- rule1: Purchase Order must be issued within 24 hours of Supply Chain Requirements update
- rule2: Supplier lead time must be tracked and reported
- rule3: Purchase Order cycle time must be monitored and optimized

## Exception Handling
- exception1: Supplier rejection of Purchase Order - re-issue or cancel Purchase Order
- exception2: Inventory discrepancy - investigate and reconcile

## Success Criteria
- Purchase Order is issued to Supplier within 24 hours
- Supplier Acknowledgment is received within 48 hours
- Inventory levels are updated correctly

## Compliance Requirements
- GxP if pharma
- GDP if distribution