# SOP — Request Excess Product Return Authorization
**Process ID:** SCOR-SR3.3
**Framework:** SCOR | **Domain:** Return
**Generated:** 2026-06-07

## Purpose
Process of negotiating and obtaining authorization from supplier to return excess inventory for credit, exchange or future order offset

## Triggers
- Excess Inventory exceeds threshold
- Disposition Decision is made to return excess inventory

## Inputs Required
- disposition decision
- excess inventory data
- supplier terms
- negotiation parameters

## Process Steps
1. IF Excess Inventory exceeds threshold THEN initiate Request Excess Product Return Authorization
2. IF Supplier Terms are acceptable THEN accept Excess Return Authorization

## Expected Outputs
- excess return authorization
- credit terms
- return quantity approval

## Business Rules
- rule1: Excess Return Authorization must be obtained from Supplier before returning excess inventory
- rule2: Credit Terms must be negotiated and agreed upon with Supplier
- rule3: Return Quantity Approval must be based on valid Disposition Decision

## Exception Handling
- exception1: Supplier does not respond to Excess Return Authorization request - escalate to Supplier management
- exception2: Credit Terms are not acceptable - renegotiate with Supplier

## Success Criteria
- Excess Return Authorization is obtained from Supplier
- Credit Terms are negotiated and agreed upon
- Return Quantity Approval is received from Supplier

## Compliance Requirements
- contractual compliance
- GDPR if personal data
- financial reporting