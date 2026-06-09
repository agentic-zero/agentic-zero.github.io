# SOP — Purchase-to-Pay
**Process ID:** BPMN-PTP-001
**Framework:**  | **Domain:** BPMN
**Generated:** 2026-06-08

## Purpose
End-to-end Purchase-to-Pay process from purchase requisition to supplier payment including approval workflows, PO creation, goods receipt and invoice matching

## Triggers
- Purchase Requisition Created event with status=SUBMITTED

## Inputs Required
- purchase requisition
- supplier catalog
- budget data
- approval matrix
- receiving data

## Process Steps
1. IF Approval Required? THEN route to Approver lane ELSE auto-approve
2. IF Goods Accepted? THEN proceed to MatchInvoice ELSE create return shipment
3. IF 3-Way Match OK? THEN ApprovePayment ELSE flag ExceptionCase
4. IF Exception? THEN escalate to Finance lane for manual resolution

## Expected Outputs
- purchase order
- goods receipt
- approved invoice
- payment
- supplier performance data

## Business Rules
- PurchaseOrder.status must equal APPROVED before SendPOtoSupplier
- 3-WayMatch requires exact match on PO_line_items, GoodsReceipt_quantity and Invoice_amount
- Payment can only execute after Invoice.status = APPROVED
- All approvals must record approver_id, timestamp and approval_matrix_version

## Exception Handling
- Goods inspection failure: create return order and notify Procurement lane within 24h
- 3-WayMatch failure: hold invoice, notify supplier and create ExceptionCase record with mismatch details
- Approval timeout > 48h: auto-escalate to next approver in matrix

## Success Criteria
- Payment.status = COMPLETED
- invoice_match_rate >= 0.95
- PO_cycle_time <= SLA_hours
- Payment on-time flag = true

## Compliance Requirements
- GDPR supplier data
- financial controls
- anti-corruption
- tax compliance