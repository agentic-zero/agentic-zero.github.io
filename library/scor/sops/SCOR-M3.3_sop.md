# SOP — Produce and Test (ETO)
**Process ID:** SCOR-M3.3
**Framework:** SCOR | **Domain:** Make
**Generated:** 2026-06-08

## Purpose
Process of fabricating, assembling and testing engineer-to-order products including integration testing, system validation and customer witness testing

## Triggers
- WorkPackage status changed to RELEASED in ERP
- EngineeringDrawing revision APPROVED in PDM

## Inputs Required
- work packages
- engineering drawings
- test procedures
- customer acceptance criteria
- test equipment

## Process Steps
1. IF integration test fails THEN execute rework loop before customer witness testing
2. IF customer witness test fails THEN log defect and trigger SCOR-M3.4 disposition

## Expected Outputs
- ETO finished assemblies
- test records
- acceptance test reports
- as-built documentation

## Business Rules
- All outputs must include AS9100 traceability stamps
- CustomerAcceptanceCriteria must be validated before final sign-off
- Export control flagged items require dual authorization before shipment

## Exception Handling
- Missing test equipment: pause process and escalate to procurement with 4-hour SLA
- Customer witness unavailable: substitute with recorded video validation plus remote sign-off

## Success Criteria
- TestPassRate >= 98 percent
- CustomerAcceptanceRate = 100 percent
- AsBuiltAccuracy = 100 percent match to drawings
- all outputs delivered within ProductionCycleTime target

## Compliance Requirements
- AS9100 production and testing
- defense acceptance testing
- export control
- customer witness test protocols