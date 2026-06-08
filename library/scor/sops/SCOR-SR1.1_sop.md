# SOP — Identify Defective Product Return
**Process ID:** SCOR-SR1.1
**Framework:** SCOR | **Domain:** Return
**Generated:** 2026-06-07

## Purpose
Process of identifying and classifying defective products that require return to supplier, including quality inspection and documentation

## Triggers
- Receipt of defective product
- Completion of quality inspection
- Submission of defect report

## Inputs Required
- quality inspection results
- defect reports
- product specifications
- supplier contracts

## Process Steps
1. IF Defect Identification Rate exceeds threshold THEN notify Supplier
2. IF Return Processing Time exceeds threshold THEN escalate to Manager
3. IF Supplier Defect Rate exceeds threshold THEN review Supplier Contract

## Expected Outputs
- defective product identification
- return classification
- defect documentation

## Business Rules
- Defective products must be returned to supplier within 30 days
- All defect reports must be documented and stored for 2 years
- Quality inspection results must be reviewed and approved by Quality Manager

## Exception Handling
- IF no supplier contract exists THEN contact Procurement to establish contract
- IF product specifications are unclear THEN consult with Product Manager to clarify
- IF defect reports are incomplete THEN request additional information from Quality Inspector

## Success Criteria
- Defective products are returned to supplier within 30 days
- Defect identification rate is below threshold
- Return processing time is below threshold
- Supplier defect rate is below threshold

## Compliance Requirements
- GxP if pharma
- ISO 9001 quality management
- GDPR if personal data involved