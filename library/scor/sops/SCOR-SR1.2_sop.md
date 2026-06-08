# SOP — Disposition Defective Product
**Process ID:** SCOR-SR1.2
**Framework:** SCOR | **Domain:** Return
**Generated:** 2026-06-07

## Purpose
Process of determining the appropriate disposition for defective products including repair, rework, scrap, or return to supplier

## Triggers
- Defective Product identification
- Quality Assessment completion

## Inputs Required
- defective product identification
- quality assessment
- cost analysis
- supplier agreements

## Process Steps
1. IF Defective Product quality is below threshold THEN disposition is Scrap
2. IF Defective Product cost analysis shows repair is cheaper THAN disposition is Repair
3. IF Supplier Agreements allow for return THEN disposition is Return to Supplier

## Expected Outputs
- disposition decision
- return authorization request
- scrap/rework order

## Business Rules
- rule1: Disposition Decision must be based on Quality Assessment and Cost Analysis
- rule2: Return Authorization Request must be generated for all returns to supplier
- rule3: Scrap/Rework Order must be generated for all scrap or rework dispositions

## Exception Handling
- IF Defective Product is hazardous THEN special handling procedures must be followed
- IF Supplier Agreements do not allow for return THEN alternative disposition methods must be explored

## Success Criteria
- Disposition Decision is made within disposition cycle time
- Return Authorization Request is generated and sent to supplier
- Scrap/Rework Order is generated and executed

## Compliance Requirements
- GxP if pharma
- ISO 9001
- environmental compliance if hazardous