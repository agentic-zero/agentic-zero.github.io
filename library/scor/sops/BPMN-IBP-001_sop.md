# SOP — Integrated Business Planning (IBP)
**Process ID:** BPMN-IBP-001
**Framework:**  | **Domain:** BPMN
**Generated:** 2026-06-08

## Purpose
IBP process connecting strategic, financial and operational planning in a rolling 24-month horizon integrating S&OP with portfolio management and strategic review

## Triggers
- Rolling Cycle Trigger: scheduled monthly event from BPMN start event

## Inputs Required
- strategic plan
- portfolio data
- market intelligence
- financial targets
- capacity constraints
- demand signals

## Process Steps
1. IF Portfolio Change? is yes THEN update portfolio data and re-run Demand Sensing
2. IF Financial Target Met? is no THEN trigger Scenario Modeling
3. IF Supply Feasible? is no THEN escalate to Supply Planning Lane for constraint relaxation
4. IF Strategic Alignment? is no THEN return to Executive Business Review for plan revision

## Expected Outputs
- integrated business plan
- financial forecast
- supply network plan
- strategic decisions
- risk register

## Business Rules
- All plans must integrate SCOR-P1.1 to SCOR-P1.5 metrics before Executive Business Review
- Cycle must complete within 24-month rolling horizon with GDPR-compliant data handling
- Automation potential capped at 0.55 requiring human approval on Financial Target Met Gateway
- ERP integration required with SAP IBP, Kinaxis or o9 Solutions for data sync

## Exception Handling
- If capacity constraints input missing, halt at Supply Network Planning and request Finance Lane override
- If regulatory planning constraints violated, flag compliance exception and route to Executive Lane for manual review before approval

## Success Criteria
- End event Integrated Business Plan Approved reached
- KPIs: plan accuracy >= 0.85 and financial target achievement >= 0.95 and cycle time <= 20 days

## Compliance Requirements
- financial reporting
- GDPR strategic data
- regulatory planning constraints