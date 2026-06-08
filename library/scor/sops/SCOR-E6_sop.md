# SOP — Manage Supply Chain Contracts
**Process ID:** SCOR-E6
**Framework:** SCOR | **Domain:** Enable
**Generated:** 2026-06-07

## Purpose
Process of managing supplier and customer contracts throughout their lifecycle including negotiation, execution, compliance monitoring and renewal across all SCOR domains

## Triggers
- New supplier performance data received
- Contract expiry within 90 days detected
- Legal requirement update published

## Inputs Required
- contract templates
- negotiation parameters
- supplier performance data
- legal requirements
- business terms

## Process Steps
1. IF contract_compliance_rate < 0.95 THEN generate ComplianceAlert and notify legal team
2. IF days_until_expiry <= 90 THEN create RenewalSchedule and start negotiation
3. IF cycle_time > 30 days THEN escalate to contract manager

## Expected Outputs
- executed contracts
- contract repository
- compliance alerts
- renewal schedules
- performance scorecards

## Business Rules
- All ExecutedContract must include GDPR data processing agreements
- Contract value optimization must be recalculated on every PerformanceScorecard update
- EU AI Act supplier obligations must be flagged in ComplianceAlert for pharma and defense sectors

## Exception Handling
- Missing supplier performance data: default to last known scorecard and set 14-day data collection task
- Non-compliant renewal: auto-reject and route to legal review before execution

## Success Criteria
- contract_compliance_rate >= 0.98
- on-time_renewal_rate >= 0.95
- contract_cycle_time <= 21 days

## Compliance Requirements
- GDPR data processing agreements
- contractual compliance
- EU AI Act supplier obligations
- financial regulations