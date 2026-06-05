# SOP — Manage Delivery Returns
**Process ID:** SCOR-D4.1
**Framework:** SCOR | **Domain:** Deliver
**Generated:** 2026-06-05

## Purpose
Process of managing delivery returns such as defective products or incorrect orders

## Triggers
- customer submits Return Request
- system detects defective Product

## Inputs Required
- return requests
- return policies
- inventory data

## Process Steps
1. IF Return Request is valid THEN process return
2. IF Product is defective THEN initiate refund or exchange
3. IF Return Request is outside policy THEN notify customer

## Expected Outputs
- processed returns
- refund and exchange information

## Business Rules
- rule1: Return Request must include order number and reason for return
- rule2: Return Policy must be clearly communicated to customers
- rule3: Inventory Data must be updated in real-time

## Exception Handling
- exception1: missing or invalid Return Request information - notify customer and request correction
- exception2: Product is no longer in inventory - offer alternative or refund

## Success Criteria
- Return Request is processed within 3 business days
- Customer receives refund or exchange within 7 business days
- Inventory Data is updated accurately

## Compliance Requirements
- EU GDPR if customer data
- CPSC if product safety