# SOP — Package (MTO)
**Process ID:** SCOR-M2.4
**Framework:** SCOR | **Domain:** Make
**Generated:** 2026-06-08

## Purpose
Process of packaging MTO finished products according to customer requirements and specifications including labeling, marking, protective packaging and compliance documentation

## Triggers
- Completion signal from SCOR-M2.3
- Customer order status changed to ready_for_packaging

## Inputs Required
- finished products
- customer packaging specifications
- labeling requirements
- packaging materials
- shipping requirements

## Process Steps
1. IF ShippingRequirement contains dangerous_goods THEN apply_dangerous_goods_compliant_packaging
2. IF LabelingRequirement includes pharma THEN enforce_GxP_labeling
3. IF PackagingMaterial.stock < required_quantity THEN trigger_procurement_or_exception

## Expected Outputs
- packaged products
- customer-specific labels
- packaging records
- packing lists

## Business Rules
- Packaging accuracy must equal 100 percent before release
- Labeling compliance rate must be 100 percent for customer-specific labels
- All packaging records must be created and stored within 24 hours of completion

## Exception Handling
- Missing customer packaging specifications: halt process and request clarification from sales
- Insufficient packaging materials: route to procurement and log delay in PackagingRecord

## Success Criteria
- PackagedProduct created with 100 percent customer specification adherence
- All KPIs (packaging accuracy, labeling compliance rate, cycle time) within defined thresholds
- PackingList and PackagingRecord generated and linked to order

## Compliance Requirements
- GxP packaging if pharma
- dangerous goods packaging regulations
- customer packaging standards
- environmental packaging regulations