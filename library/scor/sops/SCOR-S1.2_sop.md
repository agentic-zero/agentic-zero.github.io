# SOP — Authorize and Pay for Products and Services
**Process ID:** SCOR-S1.2
**Framework:** SCOR | **Domain:** Source
**Generated:** 2026-06-02

## Purpose
Process of authorizing and paying for products and services received from suppliers

## Triggers
- receipt of Supplier Invoice
- verification of Receipt

## Inputs Required
- purchase orders
- supplier invoices
- receipts

## Process Steps
1. IF Supplier Invoice is accurate AND Receipt is verified THEN authorize Payment
2. IF Payment is successful THEN update Inventory Record

## Expected Outputs
- payments to suppliers
- updated inventory records

## Business Rules
- rule1: Payment must be made within a specified payment cycle time
- rule2: Invoice accuracy must be verified before authorizing Payment
- rule3: Compliance with GxP or GDP regulations is required if applicable

## Exception Handling
- exception1: IF Supplier Invoice is inaccurate THEN notify Supplier and request correction
- exception2: IF Payment fails THEN retry Payment or notify Finance team

## Success Criteria
- Payment is made successfully
- Inventory Record is updated accurately
- Payment cycle time is within specified limit

## Compliance Requirements
- GxP if pharma
- GDP if distribution