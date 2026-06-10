# SOP — Production Part Approval Process (PPAP)
**Process ID:** IATF16949-PPAP
**Framework:** IATF 16949:2016 | **Domain:** IATF 16949
**Generated:** 2026-06-10

## Purpose
Production part approval process to demonstrate that supplier production processes can produce parts meeting customer requirements consistently at production rates

## Triggers
- new_part_release OR engineering_change_level_update OR customer PPAP_request_date

## Inputs Required
- engineering drawings
- material certifications
- dimensional results
- capability studies
- control plans

## Process Steps
1. IF all DimensionalResult within tolerance AND Cpk >= 1.33 THEN generate PartSubmissionWarrant
2. IF submission completeness == 100% THEN submit PPAPSubmissionPackage

## Expected Outputs
- PPAP submission package
- customer approval
- PSW (Part Submission Warrant)
- capability data

## Business Rules
- PPAPSubmissionPackage must include all inputs listed in AIAG PPAP manual 4th Edition
- CapabilityStudy must report Cpk and Ppk per customer-specific requirements
- PartSubmissionWarrant must be signed by supplier quality representative before submission

## Exception Handling
- IF first-time approval fails THEN trigger resubmission with corrective action records within 10 business days
- IF customer-specific requirements conflict with AIAG PPAP THEN apply stricter customer requirement

## Success Criteria
- customer_approval_status == APPROVED
- psw_signed_date IS NOT NULL
- PPAP first-time approval rate >= 0.9

## Compliance Requirements
- IATF 16949:2016
- AIAG PPAP manual
- customer-specific requirements
- VDA 2