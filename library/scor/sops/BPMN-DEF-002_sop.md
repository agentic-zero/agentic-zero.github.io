# SOP — Export Control Clearance
**Process ID:** BPMN-DEF-002
**Framework:**  | **Domain:** BPMN
**Generated:** 2026-06-09

## Purpose
Export control screening and clearance process for shipments, technology transfers and services to international customers including denied party screening, license determination and compliance documentation

## Triggers
- Export Transaction Initiated event from ERP order creation

## Inputs Required
- product ECCN classification
- customer data
- country data
- denied party lists
- license data

## Process Steps
1. IF Party matches DeniedPartyList THEN block export
2. IF ECCN requires license AND no exception THEN apply for License
3. IF License Approved? == true THEN Clear Shipment ELSE block
4. IF Exception Applies? == true THEN skip License application

## Expected Outputs
- export clearance
- export license
- AES filing
- compliance documentation

## Business Rules
- All Items must have valid ECCN/USML classification before screening
- Denied party screening must complete before license determination
- AES filing required for all cleared exports >$2500
- License must be obtained before physical shipment release

## Exception Handling
- Party on denied list: immediately route to Export Blocked and notify Legal
- License application rejected: log reason, update compliance record, notify Sales/Operations
- Missing ECCN: pause process and require classification task completion

## Success Criteria
- End event Export Cleared reached
- ComplianceDocument generated with all required fields
- ElectronicExportInfo filed with AES confirmation number

## Compliance Requirements
- ITAR 22 CFR 120-130
- EAR 15 CFR 730-774
- OFAC sanctions
- EU dual-use regulations