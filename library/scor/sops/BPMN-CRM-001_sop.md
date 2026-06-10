# SOP — Customer Complaint Management
**Process ID:** BPMN-CRM-001
**Framework:**  | **Domain:** BPMN
**Generated:** 2026-06-09

## Purpose
Customer complaint handling process from receipt to resolution including acknowledgment, investigation, corrective action and customer follow-up

## Triggers
- ComplaintReceived event with customer_id and complaint_text

## Inputs Required
- customer complaint
- order data
- product data
- regulatory requirements
- resolution options

## Process Steps
1. IF RegulatoryReportable == true THEN create RegulatoryReport and notify authority
2. IF SafetyIssue == true THEN escalate to Management immediately
3. IF ResolutionAccepted == false THEN return to DefineResolution
4. IF CAPARequired == true THEN create and link CAPA record

## Expected Outputs
- complaint record
- resolution
- customer communication
- regulatory report if needed
- CAPA

## Business Rules
- complaint.cycle_time <= 30 days for non-pharma sectors
- customer_data must comply with GDPR encryption and consent
- pharma complaints require GxP audit trail on all status changes
- first_contact_resolution logged as boolean on Complaint entity

## Exception Handling
- SafetyIssue true: bypass normal flow and escalate within 4 hours
- ResolutionAccepted false after 2 attempts: auto-escalate to Management
- Missing order_data: create Complaint with status 'incomplete' and request data from Customer

## Success Criteria
- Complaint.status == closed AND satisfaction_score >= 7 AND cycle_time recorded
- first_contact_resolution == true OR repeat_complaint_rate == 0 within 90 days

## Compliance Requirements
- GxP if pharma
- GDPR customer data
- consumer protection
- product liability