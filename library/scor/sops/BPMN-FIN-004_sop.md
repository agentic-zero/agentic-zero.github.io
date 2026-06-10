# SOP — Credit Management & Risk Assessment
**Process ID:** BPMN-FIN-004
**Framework:**  | **Domain:** BPMN
**Generated:** 2026-06-09

## Purpose
Customer credit assessment and management process from new customer request to credit limit management including risk scoring, approval and ongoing monitoring

## Triggers
- CreditRequestReceived start event containing customer_id and requested_amount

## Inputs Required
- customer financial data
- credit bureau data
- payment history
- order data
- risk parameters

## Process Steps
1. IF NewCustomer? == true THEN GatherCustomerData ELSE SkipToCreditScoreAssessment
2. IF RiskAcceptable? == false THEN CreditDenied ELSE ProceedToApprovalWorkflow
3. IF ApprovalLevel? == Management THEN RouteToManagementLane ELSE CreditManagementLane
4. IF LimitExceeded? == true THEN CreditSuspended ELSE ContinueMonitoring

## Expected Outputs
- credit limit
- credit terms
- risk classification
- monitoring alerts

## Business Rules
- Credit limit must be set only after RiskClassification completes with score >= threshold
- All financial data access must log GDPR consent timestamp
- ApprovalWorkflow requires dual sign-off for limits > 50000
- RiskClassification must incorporate Basel III capital requirement factor

## Exception Handling
- Missing credit bureau data: halt and create manual review task in CreditManagement lane
- AML compliance flag: immediately route to Management lane and set CreditSuspended
- Payment history older than 90 days: require fresh bureau pull before RiskClassification

## Success Criteria
- End event CreditApproved reached with CreditLimit persisted to SAP FSCM
- credit_approval_cycle_time <= 48 hours measured from trigger timestamp
- bad_debt_rate <= 2 percent on all approved limits after 12 months

## Compliance Requirements
- GDPR financial data
- consumer credit regulations
- AML compliance
- data retention