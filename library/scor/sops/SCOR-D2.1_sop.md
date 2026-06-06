# SOP — Deliver Service
**Process ID:** SCOR-D2.1
**Framework:** SCOR | **Domain:** Deliver
**Generated:** 2026-06-06

## Purpose
Process of delivering services to customers

## Triggers
- Customer Request receipt
- Scheduled Service delivery

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
- rule2: Validate Customer Request against Service Schedule and Resource availability
- rule3: Generate Invoice and Payment information according to Service delivery

## Exception Handling
- exception1: Handle cases where Customer Request cannot be fulfilled due to Resource unavailability
- exception2: Manage situations where SLA compliance is breached

## Success Criteria
- SLA compliance is met
- Customer satisfaction is high
- Invoice and Payment information is accurate and timely

## Compliance Requirements
- EU GDPR if customer data
- HIPAA if healthcare