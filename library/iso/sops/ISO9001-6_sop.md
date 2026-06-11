# SOP — Planning — Risk and Opportunity Management
**Process ID:** ISO9001-6
**Framework:** ISO 9001:2015 | **Domain:** ISO 9001
**Generated:** 2026-06-10

## Purpose
Actions to address risks and opportunities, quality objectives and planning to achieve them, planning of changes to the QMS

## Triggers
- new ContextAnalysis available
- PerformanceData updated
- StakeholderNeed changed
- scheduled quarterly review

## Inputs Required
- context analysis
- stakeholder needs
- quality policy
- performance data
- change triggers

## Process Steps
1. IF risk.likelihood * risk.impact > 12 THEN create ActionPlan with mitigation steps
2. IF change_trigger exists THEN generate ChangePlan with impact assessment
3. IF objective_achievement_rate < 0.8 THEN revise QualityObjective and ActionPlan

## Expected Outputs
- risk register
- opportunity register
- quality objectives
- action plans
- change plans

## Business Rules
- Risk must have likelihood (1-5), impact (1-5) and owner before register entry
- QualityObjective must be SMART and linked to at least one Risk or Opportunity
- All ActionPlans require due_date and kpi_link before approval

## Exception Handling
- IF no change_triggers in review period THEN skip ChangePlan creation and log waiver
- IF sector is 'defense' THEN require additional compliance_flags check before Risk approval

## Success Criteria
- risk_mitigation_effectiveness >= 0.85
- objective_achievement_rate >= 0.9
- change_success_rate >= 0.95

## Compliance Requirements
- ISO 9001:2015 Clause 6
- ISO 31000 risk management