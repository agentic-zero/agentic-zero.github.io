# SOP — Request MRO Return Authorization
**Process ID:** SCOR-SR2.3
**Framework:** SCOR | **Domain:** Return
**Generated:** 2026-06-07

## Purpose
Process of requesting authorization from supplier to return MRO items and negotiating credit or replacement terms

## Triggers
- receipt of defective MRO item
- expiration of MRO item warranty

## Inputs Required
- disposition decision
- MRO item data
- supplier contact
- purchase history

## Process Steps
1. IF MRO item is defective THEN request Return Authorization
2. IF Supplier agrees to return THEN negotiate Credit Terms Agreement

## Expected Outputs
- MRO return authorization
- credit terms agreement
- return instructions

## Business Rules
- rule1: Return Authorization must be obtained from Supplier before returning MRO item
- rule2: Credit Terms Agreement must be negotiated with Supplier
- rule3: Return Instructions must be followed to ensure proper return

## Exception Handling
- exception1: Supplier denies Return Authorization, THEN escalate to procurement team
- exception2: Credit Terms Agreement cannot be negotiated, THEN consider alternative suppliers

## Success Criteria
- Return Authorization is obtained from Supplier
- Credit Terms Agreement is negotiated with Supplier
- MRO item is returned and replaced or credited

## Compliance Requirements
- contractual compliance
- GDPR if personal data
- procurement policy