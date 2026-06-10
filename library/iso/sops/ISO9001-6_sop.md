# SOP — Planning — Risk and Opportunity Management
**Process ID:** ISO9001-6
**Framework:** ISO 9001:2015 | **Domain:** ISO 9001
**Generated:** 2026-06-10

## Purpose
Actions to address risks and opportunities, quality objectives and planning to achieve them, planning of changes to the QMS

## Triggers
- new context_analysis or stakeholder_needs received
- performance_data update or change_trigger detected

## Inputs Required
- context analysis
- stakeholder needs
- quality policy
- performance data
- change triggers

## Process Steps
1. IF risk.likelihood * risk.impact > 12 THEN create ActionPlan with mitigation steps
2. IF opportunity.impact > 8 THEN create ActionPlan with exploitation steps
3. IF change_trigger.priority == 'high' THEN generate ChangePlan within 30 days

## Expected Outputs
- risk register
- opportunity register
- quality objectives
- action plans
- change plans

## Business Rules
- Every Risk must have likelihood and impact scores before RiskRegister update
- QualityObjective must reference at least one quality_policy clause
- All ActionPlans must define owner, due_date and success_metric
- RiskRegister must be reviewed before any ChangePlan approval

## Exception Handling
- If no change_triggers present, skip ChangePlan creation and log waiver
- If performance_data missing for >20% of risks, flag for manual review instead of auto-register

## Success Criteria
- risk_mitigation_effectiveness >= 0.8
- objective_achievement_rate >= 0.9
- change_success_rate >= 0.85

## Compliance Requirements
- ISO 9001:2015 Clause 6
- ISO 31000 risk management