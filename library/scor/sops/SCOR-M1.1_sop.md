# SOP — Schedule Production
**Process ID:** SCOR-M1.1
**Framework:** SCOR | **Domain:** Make
**Generated:** 2026-06-03

## Purpose
Process of creating and managing production schedules to meet customer demand

## Triggers
- receipt of new Production Plans
- changes to Inventory Data or Capacity Data

## Inputs Required
- production plans
- inventory data
- capacity data

## Process Steps
1. IF production capacity is insufficient THEN adjust Production Plans
2. IF inventory levels are low THEN prioritize production of affected items

## Expected Outputs
- production schedules
- work orders

## Business Rules
- rule1: Production Schedules must be created within 24 hours of receiving Production Plans
- rule2: Work Orders must be generated within 1 hour of creating Production Schedules

## Exception Handling
- IF production equipment fails THEN notify maintenance team and adjust Production Schedules
- IF material shortages occur THEN identify alternative suppliers and adjust Production Plans

## Success Criteria
- Production Schedules are created and meet customer demand
- Work Orders are generated and production is completed on time

## Compliance Requirements