# SOP — Operation — Planning and Control
**Process ID:** ISO9001-8
**Framework:** ISO 9001:2015 | **Domain:** ISO 9001
**Generated:** 2026-06-12

## Purpose
Operational planning and control including customer communication, design and development, control of externally provided processes, production and service provision, release and control of nonconforming outputs

## Triggers
- receipt of new customer order containing requirements
- scheduled production start date reached with approved QualityPlan

## Inputs Required
- customer requirements
- product specifications
- supplier data
- process parameters
- quality plans

## Process Steps
1. IF inspection_result == 'pass' AND process_parameters_met THEN create ReleaseDecision ELSE create NonconformanceReport
2. IF nonconformance_closure_rate >= 0.95 THEN close NonconformanceReport ELSE escalate to CAPA

## Expected Outputs
- controlled products/services
- inspection records
- nonconformance reports
- release decisions
- supplier evaluations

## Business Rules
- Every output must have at least one linked InspectionRecord before ReleaseDecision
- SupplierEvaluation score must be calculated from supplier_data before any externally provided process is used
- All NonconformanceReport must record root_cause and corrective_action within 5 business days

## Exception Handling
- IF customer_requirement changes after OperationalPlan approval THEN trigger revision of QualityPlan and re-execution of planning step
- IF GxP flag active in pharma sector THEN enforce additional batch record validation before ReleaseDecision

## Success Criteria
- first_pass_yield >= target AND customer_complaint_rate <= threshold AND all ReleaseDecision issued with linked InspectionRecord

## Compliance Requirements
- ISO 9001:2015 Clause 8
- GxP if pharma
- HACCP if food
- IATF 16949 if automotive