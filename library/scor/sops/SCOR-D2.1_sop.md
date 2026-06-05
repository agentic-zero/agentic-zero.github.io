# SOP — Deliver Service
**Process ID:** SCOR-D2.1
**Framework:** SCOR | **Domain:** Deliver
**Generated:** 2026-06-05

## Purpose
Process of delivering services to customers

## Triggers
- Customer Request is received
- Service Schedule is updated
- Resource availability changes

## Inputs Required
- customer requests
- service schedules
- resource availability

## Process Steps
1. IF Customer Request is received THEN initiate Service delivery
2. IF Resource availability is low THEN adjust Service Schedule
3. IF SLA compliance is at risk THEN escalate to management

## Expected Outputs
- delivered services
- invoice and payment information

## Business Rules
- rule1: Ensure SLA compliance for all Services
- rule2: Validate Customer Request against Service Schedule
- rule3: Verify Resource availability before delivering Service

## Exception Handling
- exception1: Handle cases where Customer Request cannot be fulfilled
- exception2: Manage situations where Resource availability is unexpectedly low
- exception3: Resolve issues with Invoice and Payment processing

## Success Criteria
- Service is delivered on time and to Customer satisfaction
- SLA compliance is maintained
- Invoice and Payment are processed correctly

## Compliance Requirements
- EU GDPR if customer data
- HIPAA if healthcare