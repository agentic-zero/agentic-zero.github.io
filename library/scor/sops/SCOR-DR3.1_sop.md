# SOP — Authorize Excess Product Return
**Process ID:** SCOR-DR3.1
**Framework:** SCOR | **Domain:** Return
**Generated:** 2026-06-07

## Purpose
Process of evaluating and authorizing excess inventory return requests, negotiating credit terms and defining acceptable return quantities and conditions

## Triggers
- receipt of ExcessReturnRequest via API or portal submission

## Inputs Required
- excess return request
- inventory data
- customer purchase history
- market conditions
- return policy

## Process Steps
1. IF excess_return_request.quantity <= return_policy.max_excess_pct * customer_purchase_history.total_purchases AND inventory_data.available_capacity >= approved_quantity THEN create ExcessReturnAuthorization
2. IF market_conditions.demand_forecast < 0.8 THEN negotiate reduced CreditTerms.value

## Expected Outputs
- excess return authorization
- approved return quantity
- credit terms
- return schedule

## Business Rules
- authorization_cycle_time must be <= 48 hours
- approved_return_quantity must be <= 15% of customer_purchase_history.last_12m_purchases
- credit_terms.payment_window_days must be between 30 and 90
- return_schedule must specify pickup_date within 14 days of authorization

## Exception Handling
- IF product is perishable and expiry_date < return_schedule.pickup_date + 30 days THEN reject request and log expiry_compliance violation
- IF GDPR applies and customer_personal_data missing consent flag THEN require explicit consent before processing

## Success Criteria
- ExcessReturnAuthorization.status == 'approved' AND authorization_cycle_time <= 48 AND excess_return_recovery_rate >= 0.85

## Compliance Requirements
- financial reporting compliance
- GDPR if personal data
- expiry compliance if perishable