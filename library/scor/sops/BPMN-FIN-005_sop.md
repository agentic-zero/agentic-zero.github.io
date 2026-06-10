# SOP — Trade Finance & Letters of Credit
**Process ID:** BPMN-FIN-005
**Framework:**  | **Domain:** BPMN
**Generated:** 2026-06-09

## Purpose
Trade finance process for international transactions including letter of credit application, document preparation, bank submission and payment receipt

## Triggers
- International Order Confirmed event with sales_contract_id

## Inputs Required
- sales contract
- LC terms
- shipping documents
- customs data
- bank instructions

## Process Steps
1. IF LC Required? THEN Apply for LC ELSE Negotiate Payment Terms
2. IF Documents Compliant? THEN Authorize Payment ELSE handle Discrepancy?
3. IF Approved? THEN Receive Payment ELSE Dispute Resolved

## Expected Outputs
- letter of credit
- compliant documents
- payment authorization
- reconciliation

## Business Rules
- UCP 600: all LC documents must match exactly or trigger discrepancy
- AML compliance: screen all parties before LC issuance
- GDPR: mask financial data in reconciliation outputs
- Export control: validate HS codes in customs data before submission

## Exception Handling
- Document discrepancy: return to Prepare Shipping Documents for correction within 5 business days
- LC rejection by ImporterBank: escalate to Dispute Resolved lane
- Payment delay >14 days: trigger AML re-screen and notify compliance

## Success Criteria
- Payment Received status reached with reconciliation_record.status=COMPLETE and document_compliance_rate>=0.98

## Compliance Requirements
- UCP 600 LC rules
- export control
- AML compliance
- GDPR financial data
- customs regulations