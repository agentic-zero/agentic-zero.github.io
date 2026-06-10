# SOP — Month-End Financial Close
**Process ID:** BPMN-FIN-003
**Framework:**  | **Domain:** BPMN
**Generated:** 2026-06-09

## Purpose
Month-end close process from period-end activities to financial statement publication including journal entries, reconciliations, variance analysis and management reporting

## Triggers
- PeriodEnd event received from ERP calendar with fiscal_period identifier

## Inputs Required
- transaction data
- accrual schedules
- reconciliation templates
- reporting requirements

## Process Steps
1. IF AllEntriesPosted == true THEN proceed to InventoryValuation ELSE return to PostAccruals
2. IF Reconciled == true THEN proceed to VarianceAnalysis ELSE return to BalanceSheetReconciliation
3. IF VarianceExplained == true THEN proceed to ManagementReview ELSE return to VarianceAnalysis
4. IF Approved == true THEN proceed to Consolidation ELSE return to ManagementReview

## Expected Outputs
- financial statements
- management reports
- variance analysis
- audit trail

## Business Rules
- All journal entries must be posted before BalanceSheetReconciliation starts
- Reconciliation completion rate must be 100% before VarianceAnalysis
- IFRS/GAAP compliance flag must be validated on every BalanceSheetReconciliation
- SOX controls must be logged on ManagementReview and ApprovedGateway

## Exception Handling
- IF AllEntriesPosted == false after 3 retries THEN escalate to AccountingLane manager and log exception
- IF Reconciled == false for intercompany accounts THEN trigger IntercompanyReconciliation task before retry
- IF VarianceExplained == false after 2 cycles THEN route to ManagementLane for override decision

## Success Criteria
- FinancialStatementsPublished event emitted
- close_cycle_time <= target_days
- journal_entry_accuracy >= 99.5%
- reconciliation_completion_rate == 100%
- reporting_on-time == true

## Compliance Requirements
- IFRS/GAAP compliance
- SOX controls
- GDPR financial data
- audit requirements