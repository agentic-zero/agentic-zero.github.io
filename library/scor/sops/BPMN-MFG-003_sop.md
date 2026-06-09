# SOP — New Product Introduction (NPI)
**Process ID:** BPMN-MFG-003
**Framework:**  | **Domain:** BPMN
**Generated:** 2026-06-09

## Purpose
New product introduction process from concept approval to production readiness including design, prototyping, validation, supply chain setup and commercial launch

## Triggers
- Product_Concept_Approved event received from R&D Lane

## Inputs Required
- product concept
- market requirements
- regulatory guidelines
- technical specifications
- supply chain requirements

## Process Steps
1. IF Stage_Gate_1 passed THEN execute Design_Engineering ELSE end with Product_Cancelled
2. IF Regulatory_OK THEN proceed to Supply_Chain_Setup ELSE return to Testing_Validation
3. IF Stage_Gate_3 passed THEN execute Commercial_Launch ELSE end with Product_Cancelled

## Expected Outputs
- product design
- validated product
- regulatory approval
- production-ready process
- commercial launch plan

## Business Rules
- Regulatory_Approval required before Pilot_Production when sector is pharma or food
- All Task outputs must be stored in connected ERP system (SAP_PLM or Windchill)
- Stage_Gate pass rate KPI must be logged after each gateway evaluation

## Exception Handling
- Product_Cancelled at any Stage_Gate: archive all artifacts and notify all Lanes within 24 hours
- Regulatory rejection: route back to Testing_Validation with documented gap list and restart clock on NPI_cycle_time

## Success Criteria
- end_event equals Product_Launched AND time-to-market <= target AND launch_quality_score >= 85

## Compliance Requirements
- regulatory approval if pharma/food
- export control
- GDPR product data
- IP protection