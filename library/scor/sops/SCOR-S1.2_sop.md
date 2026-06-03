# SOP — Authorize and Pay for Products and Services
**Process ID:** SCOR-S1.2
**Framework:** SCOR | **Domain:** Source
**Generated:** 2026-06-03

## Purpose
Process of authorizing and paying for products and services received from suppliers

## Triggers
- receipt of Supplier Invoice
- confirmation of Receipt

## Inputs Required
- purchase orders
- supplier invoices
- receipts

## Process Steps
1. IF Supplier Invoice is accurate THEN process Payment
2. IF Receipt does not match Purchase Order THEN investigate discrepancy

## Expected Outputs
- payments to suppliers
- updated inventory records

## Business Rules
- rule1: Payment must be made within payment cycle time
- rule2: Invoice accuracy must be verified before Payment
- rule3: Compliance with GxP or GDP regulations must be ensured if applicable

## Exception Handling
- exception1: missing or inaccurate Supplier Invoice - notify Supplier and request correction
- exception2: Payment failure - retry Payment or contact Supplier

## Success Criteria
- Payment is made to Supplier within payment cycle time
- Inventory Record is updated accurately
- Supplier Invoice is verified for accuracy

## Compliance Requirements
- GxP if pharma
- GDP if distribution