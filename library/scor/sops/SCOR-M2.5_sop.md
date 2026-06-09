# SOP — Stage Product (MTO)
**Process ID:** SCOR-M2.5
**Framework:** SCOR | **Domain:** Make
**Generated:** 2026-06-08

## Purpose
Process of staging MTO finished goods for outbound delivery including final inspection, documentation completion and handover to deliver operations

## Triggers
- receipt of PackagedProduct from SCOR-M2.4
- arrival of DeliverySchedule with customer_delivery_instructions

## Inputs Required
- packaged products
- delivery schedules
- documentation requirements
- staging area capacity
- customer delivery instructions

## Process Steps
1. IF documentation_completeness == 100% AND staging_accuracy >= 99% THEN execute handover to SCOR-D2.1
2. IF staging_area_capacity < required_space THEN trigger exception reroute to alternate staging

## Expected Outputs
- staged finished goods
- delivery documentation
- handover to deliver
- inventory update

## Business Rules
- staging_cycle_time must be <= target_cycle_time from DeliverySchedule
- all compliance_flags must be validated before handover
- inventory_update must be atomic and logged within 5 minutes of staging completion

## Exception Handling
- IF dangerous_goods_documentation missing THEN block handover and notify compliance team
- IF staging_area full THEN queue PackagedProduct and alert capacity planner

## Success Criteria
- staging_accuracy >= 0.99
- documentation_completeness == 1.0
- delivery_readiness_rate >= 0.98
- handover confirmed by SCOR-D2.1 within staging_cycle_time

## Compliance Requirements
- GxP release if pharma
- dangerous goods documentation
- export documentation if applicable
- GDPR customer data