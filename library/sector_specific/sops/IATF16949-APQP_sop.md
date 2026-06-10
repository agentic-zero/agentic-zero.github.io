# SOP — Advanced Product Quality Planning (APQP)
**Process ID:** IATF16949-APQP
**Framework:** IATF 16949:2016 | **Domain:** IATF 16949
**Generated:** 2026-06-10

## Purpose
Structured product quality planning process for automotive supply chain from concept through production launch including design FMEA, process FMEA, control plans and production part approval

## Triggers
- New customer purchase order received
- Design specification revision released

## Inputs Required
- customer requirements
- design specifications
- process capabilities
- historical quality data
- risk assessments

## Process Steps
1. IF Design_FMEA highest RPN > 100 THEN require risk mitigation action before phase gate approval
2. IF PPAP submission status == 'rejected' THEN trigger corrective action loop and resubmission

## Expected Outputs
- APQP plan
- design FMEA
- process FMEA
- control plan
- PPAP submission

## Business Rules
- All APQP phases must achieve 100% gate compliance before advancing
- Design_FMEA and Process_FMEA must be completed prior to Control_Plan release
- PPAP submission requires signed PSW and full documentation per AIAG manual

## Exception Handling
- Customer waives PPAP level 3-5 requirements: downgrade to level 2 with documented approval and retain all FMEA records
- Low-volume prototype run: skip full process capability study but retain control plan

## Success Criteria
- APQP phase gate compliance == 100%
- PPAP approval status == 'approved'
- Launch defect rate < 50 PPM

## Compliance Requirements
- IATF 16949:2016
- VDA 6.3
- customer-specific requirements
- AIAG APQP manual