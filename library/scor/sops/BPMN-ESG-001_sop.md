# SOP — Carbon Footprint & Scope 3 Tracking
**Process ID:** BPMN-ESG-001
**Framework:**  | **Domain:** BPMN
**Generated:** 2026-06-09

## Purpose
Supply chain carbon footprint calculation and reporting process including Scope 1, 2 and 3 emissions data collection, calculation, verification and reporting

## Triggers
- Reporting Period Start event with fixed calendar date or fiscal quarter close

## Inputs Required
- energy consumption data
- supplier emissions data
- transport data
- emission factors
- reporting standards

## Process Steps
1. IF DataComplete == false THEN loop to Collect tasks
2. IF ThirdPartyVerification == true THEN route to ExternalAuditor else internal VerifyData
3. IF TargetMet == false THEN execute SetReductionTargets
4. IF MaterialScope3 == true THEN include supplier and transport data in Scope3 calculation

## Expected Outputs
- carbon footprint report
- Scope 1/2/3 data
- reduction targets
- ESG disclosure

## Business Rules
- All emissions calculations must apply GHG Protocol emission factors
- Scope3 data collection requires supplier data with minimum 70% coverage for CSRD compliance
- Data quality score must exceed 0.8 before PublishReport
- Reduction targets must be numeric and time-bound per TCFD

## Exception Handling
- IF supplier emissions data missing THEN substitute with industry-average factors and flag in report
- IF verification fails THEN return to VerifyData with audit notes and extend reporting period by 5 days
- IF Scope3 coverage below threshold THEN mark as MaterialScope3 and trigger Procurement lane

## Success Criteria
- ESGReportPublished event emitted
- KPI:target_achievement_rate >= 0.9
- all compliance_flags satisfied with no open flags

## Compliance Requirements
- GHG Protocol
- CSRD EU reporting
- TCFD
- SEC climate disclosure
- GDPR supplier data