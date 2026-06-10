# SOP — Operation — Planning and Control
**Process ID:** ISO9001-8
**Framework:** ISO 9001:2015 | **Domain:** ISO 9001
**Generated:** 2026-06-10

## Purpose
Operational planning and control including customer communication, design and development, control of externally provided processes, production and service provision, release and control of nonconforming outputs

## Triggers
- New customer_requirements received
- QualityPlan updated
- SupplierData refresh event

## Inputs Required
- customer requirements
- product specifications
- supplier data
- process parameters
- quality plans

## Process Steps
1. IF inspection_result == 'pass' THEN create ReleaseDecision ELSE create NonconformanceReport
2. IF supplier_quality_rate < 0.95 THEN flag SupplierEvaluation for review

## Expected Outputs
- controlled products/services
- inspection records
- nonconformance reports
- release decisions
- supplier evaluations

## Business Rules
- All outputs must generate InspectionRecord before ReleaseDecision
- NonconformanceReport must be created within 24 hours of detection
- Sector == 'pharma' requires GxP compliance flag on all records

## Exception Handling
- If sector == 'food' and HACCP deviation detected, route to external HACCP review before ReleaseDecision
- If automation_potential check fails, require manual sign-off on ReleaseDecision

## Success Criteria
- first_pass_yield >= 0.95
- nonconformance_closure_rate >= 0.98
- customer_complaint_rate <= 0.02

## Compliance Requirements
- ISO 9001:2015 Clause 8
- GxP if pharma
- HACCP if food
- IATF 16949 if automotive