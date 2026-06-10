# SOP — Production Part Approval Process (PPAP)
**Process ID:** IATF16949-PPAP
**Framework:** IATF 16949:2016 | **Domain:** IATF 16949
**Generated:** 2026-06-10

## Purpose
Production part approval process to demonstrate that supplier production processes can produce parts meeting customer requirements consistently at production rates

## Triggers
- engineering change notice received
- new product launch initiated
- supplier process change detected

## Inputs Required
- engineering drawings
- material certifications
- dimensional results
- capability studies
- control plans

## Process Steps
1. IF Cpk >= 1.67 for all critical characteristics THEN include in PPAPSubmissionPackage
2. IF dimensional_results conform to EngineeringDrawing tolerances THEN proceed to capability validation
3. IF customer-specific requirements exist THEN override AIAG defaults

## Expected Outputs
- PPAP submission package
- customer approval
- PSW (Part Submission Warrant)
- capability data

## Business Rules
- PPAPSubmissionPackage must include all inputs: engineering drawings, material certifications, dimensional results, capability studies, control plans
- PartSubmissionWarrant must be signed by customer for process completion
- Capability data must demonstrate production at quoted rate

## Exception Handling
- IF customer-specific requirements conflict with AIAG PPAP manual THEN apply customer-specific requirements and document deviation
- IF first-time submission rejected THEN trigger resubmission with root cause analysis within 10 business days

## Success Criteria
- CustomerApproval status == 'approved'
- PartSubmissionWarrant signed and dated
- PPAP first-time approval achieved

## Compliance Requirements
- IATF 16949:2016
- AIAG PPAP manual
- customer-specific requirements
- VDA 2