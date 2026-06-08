# SOP — Issue In-Process Product (ETO)
**Process ID:** SCOR-M3.2
**Framework:** SCOR | **Domain:** Make
**Generated:** 2026-06-07

## Purpose
Process of issuing custom-engineered components and materials to ETO production operations maintaining configuration control and engineering traceability throughout

## Triggers
- WorkPackage status changed to 'Released' in MES
- ProductionRouting step reached 'Material Issue'

## Inputs Required
- engineering BOMs
- configuration documents
- ETO components
- work packages
- production routings

## Process Steps
1. IF EngineeringBOM version == ConfigurationDocument version THEN proceed to issue ETOComponent ELSE hold for engineering review

## Expected Outputs
- issued ETO components
- configuration records
- work package assignments
- traceability records

## Business Rules
- rule1: All issued ETOComponent must retain original serial/lot traceability from source
- rule2: ConfigurationRecord must be created before any WorkPackage assignment
- rule3: Issue cycle time must be logged with timestamp at each ETOComponent release

## Exception Handling
- Missing configuration signature: route to compliance queue and block issuance until signed
- BOM mismatch detected: auto-create discrepancy record and notify engineering within 4 hours

## Success Criteria
- configuration_accuracy >= 99.5%
- traceability_completeness == 100%
- issue_cycle_time <= target defined in WorkPackage

## Compliance Requirements
- configuration management standards
- AS9100
- defense acquisition
- export control