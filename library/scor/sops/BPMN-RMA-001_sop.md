# SOP — Returns Management (RMA)
**Process ID:** BPMN-RMA-001
**Framework:**  | **Domain:** BPMN
**Generated:** 2026-06-09

## Purpose
End-to-end returns management from customer return request to disposition including authorization, receipt, inspection, disposition decision and credit/replacement

## Triggers
- Return Request Received event from customer portal or email ingestion

## Inputs Required
- return request
- order history
- return policy
- product condition criteria
- credit terms

## Process Steps
1. IF WithinPolicy == true THEN IssueRMA ELSE RejectAndNotify
2. IF Defective == true THEN RouteToQuality ELSE RouteToRestock
3. IF RestockPossible == true THEN Restock ELSE Scrap
4. IF CreditOrReplace == 'credit' THEN IssueCredit ELSE CreateReplacement

## Expected Outputs
- RMA authorization
- received return
- inspection report
- credit note
- restocked inventory

## Business Rules
- ReturnRequest must include order_id and match return_policy window
- InspectionReport.condition must be one of ['new','used','defective','damaged']
- CreditNote.amount must equal original_line_item_value minus restocking_fee
- All customer PII must be GDPR-masked before storage
- RMA.expiry_date must be set to now + 14 days

## Exception Handling
- ReturnRequest outside policy: auto-reject and log reason in audit_trail
- InspectionReport missing photos: hold in Quality queue and request resubmission
- Credit issuance fails: escalate to Finance supervisor and pause RMA
- Inventory update conflict: mark item Quarantine and trigger manual review

## Success Criteria
- End event ReturnResolved reached with status='closed'
- CustomerCredited event emitted with matching credit_note_id
- RMA cycle time <= KPI threshold
- No open exceptions on RMA record

## Compliance Requirements
- consumer protection regulations
- GDPR customer data
- warranty compliance