# SOP — Release Production
**Process ID:** SCOR-M2.1
**Framework:** SCOR | **Domain:** Make
**Generated:** 2026-06-03

## Purpose
Process of releasing production orders to the shop floor

## Triggers
- new Production Schedule is created
- Work Order is updated

## Inputs Required
- production schedules
- work orders

## Process Steps
1. IF Production Schedule is available AND Work Order is ready THEN release Production Order
2. IF Material Requirement is not met THEN adjust Production Order

## Expected Outputs
- production orders
- material requirements

## Business Rules
- rule1: Production Order must be released within a certain timeframe
- rule2: Material Requirement must be fulfilled before Production Order can start

## Exception Handling
- exception1: Production Schedule is delayed - re-evaluate Production Order release
- exception2: Material Requirement cannot be fulfilled - notify production team and adjust Production Order

## Success Criteria
- Production Order is successfully released to Shop Floor
- Material Requirement is fulfilled
- Production lead time is within acceptable range

## Compliance Requirements