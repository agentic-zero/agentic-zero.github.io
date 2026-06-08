# SOP — Authorize Defective Product Return
**Process ID:** SCOR-DR1.1
**Framework:** SCOR | **Domain:** Return
**Generated:** 2026-06-07

## Purpose
Process of evaluating and authorizing customer requests to return defective products, issuing RMA and defining return terms

## Triggers
- Receipt of CustomerReturnRequest containing defect_evidence and product_serial

## Inputs Required
- customer return request
- defect evidence
- product warranty data
- return policy

## Process Steps
1. IF defect_evidence matches warranty_data AND within_return_policy THEN issue RMAAuthorization ELSE reject request
2. IF product_sector is pharma AND GxP_flag true THEN require compliance_review before authorization

## Expected Outputs
- RMA authorization
- return terms
- credit or replacement decision

## Business Rules
- authorization_cycle_time must be <= 48 hours from request receipt
- RMA must include unique authorization_id and expiration_date
- GDPR personal_data must be anonymized in all outputs if present

## Exception Handling
- If defect_evidence is incomplete, auto-request additional evidence and pause process for 72 hours
- If customer is flagged for fraud, route to manual review and block auto-approval

## Success Criteria
- RMAAuthorization generated with status=approved
- authorization_cycle_time KPI recorded
- CreditOrReplacementDecision emitted to downstream process

## Compliance Requirements
- consumer protection regulations
- warranty compliance
- GDPR if personal data
- GxP if pharma