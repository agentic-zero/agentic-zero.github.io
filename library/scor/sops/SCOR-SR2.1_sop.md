# SOP — Identify MRO Product Return
**Process ID:** SCOR-SR2.1
**Framework:** SCOR | **Domain:** Return
**Generated:** 2026-06-07

## Purpose
Process of identifying maintenance, repair and operations (MRO) items requiring return due to over-ordering, wrong specification or end of need

## Triggers
- Scheduled review of MRO Inventory
- Notification of changes to Maintenance Records or Purchase Orders
- Asset Management Data updates

## Inputs Required
- MRO inventory data
- maintenance records
- purchase orders
- asset management data

## Process Steps
1. IF MRO Item is over-ordered THEN initiate return process
2. IF MRO Item has wrong specification THEN initiate return process
3. IF MRO Item is no longer needed THEN initiate return process

## Expected Outputs
- MRO return identification
- return justification
- item classification

## Business Rules
- All MRO Items must be tracked in Inventory
- Maintenance Records must be up-to-date for all MRO Items
- Purchase Orders must be verified for accuracy
- Asset Management Data must be consulted for return decisions
- Return Identification must be documented and justified

## Exception Handling
- IF MRO Item is critical to operations THEN do not initiate return process
- IF return process is not feasible THEN document reason and escalate

## Success Criteria
- MRO return identification rate meets target
- Excess MRO rate is reduced
- Return value recovered meets target

## Compliance Requirements
- asset management compliance
- GDPR if personal data involved
- environmental if hazardous MRO