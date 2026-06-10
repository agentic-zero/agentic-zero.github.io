# SOP — Controlled Item & Serialization Management
**Process ID:** BPMN-DEF-001
**Framework:**  | **Domain:** BPMN
**Generated:** 2026-06-09

## Purpose
Controlled item lifecycle management process from registration to disposition including serialization, tracking, custody transfer and disposition reporting

## Triggers
- ControlledItemRegistered event with item specifications and classification data

## Inputs Required
- item specifications
- serial numbers
- classification data
- transfer orders
- disposal regulations

## Process Steps
1. IF ClassificationLevel == 'High' THEN route to Security lane
2. IF TransferAuthorized == false THEN return to Management for review
3. IF DispositionApproved == true THEN execute PrepareDisposition else reject
4. IF AuditRequired == true THEN execute ConductInventory before end event

## Expected Outputs
- item registry
- custody records
- audit trail
- regulatory reports
- disposition records

## Business Rules
- SerialNumber must be unique and immutable after assignment
- Every custody transfer requires dual-lane approval (InventoryControl + Security)
- All regulatory reports must be generated within 24 hours of disposition
- ClassificationLevel must be validated against ITAR/EAR before any transfer

## Exception Handling
- Transfer not authorized: escalate to Management lane and log exception in AuditTrail
- Serial number collision: halt process and trigger manual registry reconciliation
- Missing classification data: block task execution until data is provided

## Success Criteria
- End event reached with valid ItemDisposed or ItemTransferred status
- AuditTrail contains complete immutable record of all tasks and decisions
- RegulatoryReport successfully transmitted to authority system

## Compliance Requirements
- ITAR/EAR export control
- defense acquisition regulations
- government property regulations
- security clearance requirements