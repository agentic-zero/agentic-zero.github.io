# SOP — Issue In-Process Product (ETO)
**Process ID:** SCOR-M3.2
**Framework:** SCOR | **Domain:** Make
**Generated:** 2026-06-10

## Purpose
Process of issuing custom-engineered components and materials to ETO production operations maintaining configuration control and engineering traceability throughout

## Triggers
- WorkPackage status changed to 'released' with linked EngineeringBOM and ConfigurationDocument

## Inputs Required
- engineering BOMs
- configuration documents
- ETO components
- work packages
- production routings

## Process Steps
1. IF configurationDocument.version == engineeringBOM.version AND complianceFlags.exportControl == false THEN issue ETOComponent ELSE route to compliance review

## Expected Outputs
- issued ETO components
- configuration records
- work package assignments
- traceability records

## Business Rules
- traceabilityRecord must capture component serial, workPackage.id and timestamp
- configurationAccuracy must equal 1.0 before issuance
- issueCycleTime must be logged in seconds from workPackage receipt

## Exception Handling
- IF BOM accuracy < 1.0 THEN block issuance and create exception record with mismatch details
- IF sector is defense AND exportControl flag present THEN require dual authorization before component release

## Success Criteria
- All outputs generated
- traceabilityCompleteness == 1.0
- configurationAccuracy == 1.0
- issueCycleTime recorded

## Compliance Requirements
- configuration management standards
- AS9100
- defense acquisition
- export control