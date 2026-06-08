# SOP — Manage Supply Chain Contracts
**Process ID:** SCOR-E6
**Framework:** SCOR | **Domain:** Enable
**Generated:** 2026-06-08

## Purpose
Process of managing supplier and customer contracts throughout their lifecycle including negotiation, execution, compliance monitoring and renewal across all SCOR domains

## Triggers
- New supplier onboarding event
- Contract expiration within 90 days
- Regulatory change in compliance_flags
- Quarterly KPI calculation batch job

## Inputs Required
- contract templates
- negotiation parameters
- supplier performance data
- legal requirements
- business terms

## Process Steps
1. IF days_until_expiration <= 90 THEN create RenewalSchedule
2. IF compliance_rate < 0.95 THEN generate ComplianceAlert
3. IF contract_value_deviation > 0.1 THEN flag for value optimization review

## Expected Outputs
- executed contracts
- contract repository
- compliance alerts
- renewal schedules
- performance scorecards

## Business Rules
- Every Contract must reference at least one LegalRequirement for GDPR or EU AI Act if sector is pharma or defense
- Contract cycle time must be calculated as execution_date - start_negotiation_date and stored in PerformanceScorecard
- On-time renewal rate is computed only for contracts with renewal_date within the last 365 days

## Exception Handling
- If LegalRequirement conflicts with BusinessTerm, route to manual legal review before execution
- If supplier performance data is older than 180 days, reject negotiation start

## Success Criteria
- contract_compliance_rate >= 0.95
- on_time_renewal_rate >= 0.90
- contract_cycle_time <= 45 days
- all executed contracts stored in ContractRepository

## Compliance Requirements
- GDPR data processing agreements
- contractual compliance
- EU AI Act supplier obligations
- financial regulations