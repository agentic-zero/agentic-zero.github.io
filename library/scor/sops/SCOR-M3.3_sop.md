# SOP — Produce and Test (ETO)
**Process ID:** SCOR-M3.3
**Framework:** SCOR | **Domain:** Make
**Generated:** 2026-06-07

## Purpose
Process of fabricating, assembling and testing engineer-to-order products including integration testing, system validation and customer witness testing

## Triggers
- Receipt of approved work packages and engineering drawings from SCOR-M3.2

## Inputs Required
- work packages
- engineering drawings
- test procedures
- customer acceptance criteria
- test equipment

## Process Steps
1. IF integration test fails THEN trigger rework loop before customer witness testing
2. IF customer witness test fails THEN escalate to quality review board and log non-conformance

## Expected Outputs
- ETO finished assemblies
- test records
- acceptance test reports
- as-built documentation

## Business Rules
- AS9100 production and testing: all ETOFinishedAssembly must have traceable serial numbers and test records
- Defense acceptance testing: customer sign-off required on AcceptanceTestReport before release
- Export control: verify end-user certificates before shipping ETOFinishedAssembly in defense or aerospace sectors

## Exception Handling
- Missing customer acceptance criteria: default to sector-specific standards (AS9100 or MIL-STD) and flag for manual review
- Test equipment calibration expired: halt process and schedule recalibration before resuming

## Success Criteria
- ProductionCycleTime <= target
- TestPassRate >= 98%
- CustomerAcceptanceRate >= 95%
- AsBuiltAccuracy >= 99.5%

## Compliance Requirements
- AS9100 production and testing
- defense acceptance testing
- export control
- customer witness test protocols