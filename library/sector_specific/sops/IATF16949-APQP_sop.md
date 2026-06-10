# SOP — Advanced Product Quality Planning (APQP)
**Process ID:** IATF16949-APQP
**Framework:** IATF 16949:2016 | **Domain:** IATF 16949
**Generated:** 2026-06-10

## Purpose
Structured product quality planning process for automotive supply chain from concept through production launch including design FMEA, process FMEA, control plans and production part approval

## Triggers
- New customer order or design change notification received

## Inputs Required
- customer requirements
- design specifications
- process capabilities
- historical quality data
- risk assessments

## Process Steps
1. IF Phase_Gate compliance == true THEN advance to next APQP phase
2. IF PPAP approval == false THEN trigger corrective action loop

## Expected Outputs
- APQP plan
- design FMEA
- process FMEA
- control plan
- PPAP submission

## Business Rules
- All APQP phases must complete before PPAP submission
- Design_FMEA and Process_FMEA must be updated before Control_Plan release
- Customer-specific requirements override default AIAG APQP timing

## Exception Handling
- Customer waives PPAP submission: log waiver ID and proceed to production with increased audit frequency

## Success Criteria
- PPAP_Submission status == approved
- launch_defect_rate <= 50 PPM
- APQP phase gate compliance == 100%

## Compliance Requirements
- IATF 16949:2016
- VDA 6.3
- customer-specific requirements
- AIAG APQP manual