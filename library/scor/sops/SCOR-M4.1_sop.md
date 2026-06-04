# SOP — Test and Inspect Products
**Process ID:** SCOR-M4.1
**Framework:** SCOR | **Domain:** Make
**Generated:** 2026-06-04

## Purpose
Process of testing and inspecting products to ensure quality and compliance

## Triggers
- confirmed Production
- update to Quality Standards

## Inputs Required
- confirmed production
- quality standards

## Process Steps
1. IF Defect Rate > threshold THEN notify Quality Control
2. IF Test Coverage < threshold THEN re-test Product

## Expected Outputs
- tested and inspected products
- quality reports

## Business Rules
- rule1: Product must meet Quality Standards
- rule2: Test Report must be generated for each Product
- rule3: Quality Report must be generated after testing

## Exception Handling
- exception1: Product fails testing - re-test or reject Product
- exception2: Quality Standards are updated - re-test Product

## Success Criteria
- Defect Rate is below threshold
- Test Coverage is above threshold
- Quality Report is generated

## Compliance Requirements
- GxP if pharma
- FDA if medical devices