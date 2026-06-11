# SOP — Operation — Planning and Control
**Process ID:** ISO9001-8
**Framework:** ISO 9001:2015 | **Domain:** ISO 9001
**Generated:** 2026-06-10

## Purpose
Operational planning and control including customer communication, design and development, control of externally provided processes, production and service provision, release and control of nonconforming outputs

## Triggers
- New customer order received
- Production schedule released
- Supplier data updated

## Inputs Required
- customer requirements
- product specifications
- supplier data
- process parameters
- quality plans

## Process Steps
1. IF inspection_result == 'pass' AND nonconformance_count == 0 THEN create ReleaseDecision
2. IF supplier_quality_rate < 0.95 THEN trigger SupplierEvaluation and corrective_action

## Expected Outputs
- controlled products/services
- inspection records
- nonconformance reports
- release decisions
- supplier evaluations

## Business Rules
- Every output must have at least one linked InspectionRecord before ReleaseDecision
- NonconformanceReport must be closed within 10 business days or escalate to management
- All customer requirements must be traceable to ProcessParameter settings

## Exception Handling
- IF customer_requirement changes after planning start THEN re-run OperationalPlan and log revision
- IF GxP flag active THEN require electronic signature on ReleaseDecision

## Success Criteria
- first_pass_yield >= 0.98
- nonconformance_closure_rate >= 0.95 within SLA
- customer_complaint_rate <= 0.02

## Compliance Requirements
- ISO 9001:2015 Clause 8
- GxP if pharma
- HACCP if food
- IATF 16949 if automotive