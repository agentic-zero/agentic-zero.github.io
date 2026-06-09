# SOP — Shop Floor Control & Execution
**Process ID:** BPMN-MFG-005
**Framework:**  | **Domain:** BPMN
**Generated:** 2026-06-09

## Purpose
Shop floor control process from work order dispatch to completion including job sequencing, machine assignment, real-time monitoring and exception management

## Triggers
- Work Order Dispatched event received from ERP

## Inputs Required
- work orders
- routings
- work center capacity
- quality specs
- materials

## Process Steps
1. IF Setup OK? THEN Execute Operation ELSE Prepare Setup
2. IF Quality OK? THEN Move to Next Operation ELSE Rework or Scrap
3. IF Rework? THEN return to Execute Operation ELSE Work Order Scrapped
4. IF Last Operation? THEN Report Completion ELSE Move to Next Operation

## Expected Outputs
- completed operations
- production data
- quality records
- OEE data
- inventory updates

## Business Rules
- Every Operation must Record Time & Quantity before completion
- In-Process Inspection required after Execute Operation per ISO 9001
- OEEData must be updated by System/MES after each ProductionRecord
- Final Inspection required before Work Order Completed

## Exception Handling
- If materials unavailable, escalate to Supervisor lane and pause WorkOrder
- If max rework attempts exceeded, route to Work Order Scrapped and update inventory
- If machine fault during Execute Operation, log exception and reassign via System/MES

## Success Criteria
- Work Order Completed status set with first-pass yield >= 95% and schedule adherence >= 90%

## Compliance Requirements
- GxP electronic batch records if pharma
- HACCP if food
- ISO 9001
- safety regulations