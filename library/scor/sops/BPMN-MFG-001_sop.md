# SOP — Engineering Change Order (ECO)
**Process ID:** BPMN-MFG-001
**Framework:**  | **Domain:** BPMN
**Generated:** 2026-06-09

## Purpose
Engineering change order process from change request to production implementation including design review, impact analysis, BOM update and work instruction revision

## Triggers
- ChangeRequestSubmitted event received via ERP integration

## Inputs Required
- change request
- engineering drawings
- BOM
- cost data
- regulatory requirements

## Process Steps
1. IF DesignFeasible == false THEN reject ECO
2. IF CostApproved == false THEN reject ECO
3. IF RegulatoryImpact == true THEN require QualityLane approval
4. IF ImmediateOrScheduled == immediate THEN execute ImplementInProduction else schedule

## Expected Outputs
- updated BOM
- revised drawings
- updated work instructions
- change implementation record

## Business Rules
- ECO must complete within defined cycle time KPI
- All BOM changes require FinanceLane cost sign-off
- Aerospace sector requires AS9100 compliance flag
- Export control compliance must be checked before ProductionImplementation

## Exception Handling
- ChangeRejected: log reason and notify submitter
- HighReworkRate: trigger additional Cross-functionalReview before implementation

## Success Criteria
- end_event == ChangeImplemented
- implementation_on_time_rate >= target
- rework_rate_post_change <= threshold
- cost_variance <= approved_limit

## Compliance Requirements
- AS9100 if aerospace
- IATF 16949 automotive
- GDPR if personal data
- export control