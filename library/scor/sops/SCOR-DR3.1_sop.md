# SOP — Authorize Excess Product Return
**Process ID:** SCOR-DR3.1
**Framework:** SCOR | **Domain:** Return
**Generated:** 2026-06-08

## Purpose
Process of evaluating and authorizing excess inventory return requests, negotiating credit terms and defining acceptable return quantities and conditions

## Triggers
- Receipt of ExcessReturnRequest via API or portal

## Inputs Required
- excess return request
- inventory data
- customer purchase history
- market conditions
- return policy

## Process Steps
1. IF ExcessReturnRequest.quantity <= InventoryData.available AND matches ReturnPolicy THEN issue ExcessReturnAuthorization ELSE negotiate quantity
2. IF customer tier from CustomerPurchaseHistory is premium THEN offer extended CreditTerms ELSE standard terms

## Expected Outputs
- excess return authorization
- approved return quantity
- credit terms
- return schedule

## Business Rules
- ReturnPolicy must be checked before any authorization
- CreditTerms must comply with financial reporting compliance
- ApprovedReturnQuantity cannot exceed ExcessReturnRequest.quantity

## Exception Handling
- If sector is pharma and expiry compliance fails then reject return and log in compliance_flags
- If GDPR applies and personal data missing then pause process until consent obtained

## Success Criteria
- ExcessReturnAuthorization generated with status=approved
- authorization_cycle_time < target_threshold
- credit_terms_quality score >= 0.8

## Compliance Requirements
- financial reporting compliance
- GDPR if personal data
- expiry compliance if perishable