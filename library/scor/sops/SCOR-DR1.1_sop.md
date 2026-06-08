# SOP — Authorize Defective Product Return
**Process ID:** SCOR-DR1.1
**Framework:** SCOR | **Domain:** Return
**Generated:** 2026-06-08

## Purpose
Process of evaluating and authorizing customer requests to return defective products, issuing RMA and defining return terms

## Triggers
- Receipt of CustomerReturnRequest via API or portal

## Inputs Required
- customer return request
- defect evidence
- product warranty data
- return policy

## Process Steps
1. IF defectEvidence.valid == true AND productWarrantyData.expiry > currentDate AND returnPolicy.allowed == true THEN issue RMAAuthorization
2. IF creditOrReplacementDecision == credit THEN trigger refund ELSE trigger replacement order

## Expected Outputs
- RMA authorization
- return terms
- credit or replacement decision

## Business Rules
- authorizationCycleTime must be <= 48 hours
- RMA must include unique authorization number and expiry date
- GDPR: mask personal data in DefectEvidence if sector == pharma

## Exception Handling
- IF no DefectEvidence provided THEN reject request and notify customer within 24 hours
- IF warranty expired THEN route to SCOR-SR1.3 for goodwill exception review

## Success Criteria
- RMAAuthorization issued with status=approved AND authorizationCycleTime recorded AND CreditOrReplacementDecision generated

## Compliance Requirements
- consumer protection regulations
- warranty compliance
- GDPR if personal data
- GxP if pharma