# SOP — Returns Management (RMA)
**Process ID:** BPMN-RMA-001
**Framework:**  | **Domain:** BPMN
**Generated:** 2026-06-10

## Purpose
End-to-end returns management from customer return request to disposition including authorization, receipt, inspection, disposition decision and credit/replacement

## Triggers
- Return Request Received event from customer portal or email

## Inputs Required
- return request
- order history
- return policy
- product condition criteria
- credit terms

## Process Steps
1. IF WithinPolicy == true THEN IssueRMA ELSE reject and NotifyCustomer
2. IF Defective == true THEN route to Quality inspection ELSE skip to RestockPossible
3. IF RestockPossible == true THEN RestockInventory ELSE ScrapItem
4. IF CreditOrReplace == 'credit' THEN ProcessCredit ELSE CreateReplacementOrder

## Expected Outputs
- RMA authorization
- received return
- inspection report
- credit note
- restocked inventory

## Business Rules
- ValidateReturnRequest must check order_history and return_policy before issuing RMA
- InspectionReport must record product_condition_criteria results
- CreditNote issuance requires FinanceLane approval and credit_terms check
- All customer data handling must comply with GDPR
- RMA must be issued within consumer_protection_regulations timeframe

## Exception Handling
- ReturnRequest outside policy: notify customer and end process without RMA
- Inspection fails quality criteria: escalate to QualityLane for manual review
- Restock not possible due to damage: force ScrapItem and log loss
- ERP integration failure: queue for retry with MS Dynamics or SAP HANA

## Success Criteria
- End event ReturnResolved reached with status 'closed'
- CustomerCredited event emitted with valid CreditNote
- RMA cycle time KPI under target threshold
- return_processing_accuracy == 100%

## Compliance Requirements
- consumer protection regulations
- GDPR customer data
- warranty compliance