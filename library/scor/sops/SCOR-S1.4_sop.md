# SOP — Manage Supplier Contracts and Agreements
**Process ID:** SCOR-S1.4
**Framework:** SCOR | **Domain:** Source
**Generated:** 2026-06-03

## Purpose
Process of managing supplier contracts and agreements

## Triggers
- new contract creation
- agreement expiration
- supplier notification

## Inputs Required
- supplier contracts
- agreements
- negotiation data

## Process Steps
1. IF contract compliance rate is below threshold THEN notify supplier
2. IF agreement renewal rate is below threshold THEN renegotiate agreement

## Expected Outputs
- updated contracts
- agreement summaries

## Business Rules
- rule1: contracts must be updated within 30 days of negotiation
- rule2: agreements must be renewed at least 60 days before expiration
- rule3: compliance rate must be above 90% to meet regulatory requirements

## Exception Handling
- exception1: contract non-compliance - notify supplier and trigger renegotiation
- exception2: agreement renewal failure - trigger escalation to management

## Success Criteria
- contract compliance rate above 90%
- agreement renewal rate above 80%
- supplier satisfaction rating above 4/5

## Compliance Requirements
- GxP if pharma
- GDP if distribution