# SOP — Issue In-Process Product (ETO)
**Process ID:** SCOR-M3.2
**Framework:** SCOR | **Domain:** Make
**Generated:** 2026-06-08

## Purpose
Process of issuing custom-engineered components and materials to ETO production operations maintaining configuration control and engineering traceability throughout

## Triggers
- WorkPackage status changed to 'released' with linked ProductionRouting
- New ETOComponent batch arrives from receiving with configuration_documents attached

## Inputs Required
- engineering BOMs
- configuration documents
- ETO components
- work packages
- production routings

## Process Steps
1. IF configuration_documents.version == engineering_BOMs.version AND all compliance_flags satisfied THEN issue ETOComponent
2. IF traceability_completeness == true THEN close WorkPackage assignment

## Expected Outputs
- issued ETO components
- configuration records
- work package assignments
- traceability records

## Business Rules
- Maintain configuration control: every ETOComponent must have linked ConfigurationRecord before issuance
- Enforce engineering traceability: all inputs and outputs must log to TraceabilityRecord with timestamp and user_id
- Sector compliance: defense and aerospace require AS9100 and export_control checks before output

## Exception Handling
- If BOM_accuracy < 1.0: block issuance and route to engineering review queue
- If export_control flag active: require dual authorization before generating IssuedETOComponent

## Success Criteria
- configuration_accuracy == 1.0
- traceability_completeness == true
- all IssuedETOComponent have non-null ConfigurationRecord and TraceabilityRecord

## Compliance Requirements
- configuration management standards
- AS9100
- defense acquisition
- export control