# SOP — Supplier Performance Management
**Process ID:** BPMN-SPM-001
**Framework:**  | **Domain:** BPMN
**Generated:** 2026-06-09

## Purpose
Supplier performance monitoring and improvement process from KPI collection to supplier development including scorecarding, review meetings and corrective action plans

## Triggers
- Performance Period End event scheduled every 30/90 days

## Inputs Required
- delivery data
- quality data
- invoice data
- supplier contracts
- performance targets

## Process Steps
1. IF Performance Acceptable? == true THEN end with Supplier Plan Approved ELSE Identify Gaps
2. IF Improvement Possible? == true THEN Agree Improvement Plan ELSE Supplier Disqualified
3. IF Strategic Supplier? == true THEN escalate to development actions ELSE standard monitoring
4. IF Actions Completed? == true THEN Update Approved Supplier List ELSE continue Monitor_Actions

## Expected Outputs
- supplier scorecard
- improvement plans
- approved supplier list
- development actions

## Business Rules
- supplier OTD must be calculated from delivery data within 5 business days of period end
- Scorecard must include supplier quality rate, cost index and development ROI
- All improvement plans require sign-off from Procurement and Supplier lanes
- GDPR supplier data must be anonymized before scorecard storage
- ISO 9001 supplier evaluation record must be retained for 3 years

## Exception Handling
- IF data missing from any ERP system THEN pause process and raise data quality ticket before Calculate Scorecard
- IF supplier disqualified THEN immediately remove from Approved Supplier List and notify Operations lane
- IF Actions Completed? remains false after 3 review cycles THEN force Supplier Disqualified gateway

## Success Criteria
- end event Supplier Plan Approved reached with Improvement_Plan status = approved and at least one KPI improved

## Compliance Requirements
- GDPR supplier data
- anti-corruption
- ISO 9001 supplier evaluation
- GxP supplier qualification if pharma