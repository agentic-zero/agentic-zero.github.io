# SOP — Records of Processing Activities (ROPA)
**Process ID:** GDPR-ART30
**Framework:** GDPR (EU) 2016/679 | **Domain:** GDPR
**Generated:** 2026-06-10

## Purpose
Maintenance of records of processing activities including controller and processor obligations, mandatory ROPA content and management of processing records as accountability evidence

## Triggers
- new_processing_activity_registered
- annual_compliance_review
- DPA_audit_notification
- material_change_to_purposes_or_transfers

## Inputs Required
- processing activities
- data categories
- purposes
- retention periods
- security measures
- transfers

## Process Steps
1. IF employee_count < 250 AND no_high_risk_processing THEN skip_detailed_ROPA
2. IF cross_border_transfer THEN require_SCC_or_adequacy_documentation
3. IF new_processing_activity THEN trigger_ROPA_update

## Expected Outputs
- ROPA document
- processing activity records
- transfer mapping
- security measure documentation

## Business Rules
- ROPA must contain name_contact_controller, purposes, data_categories, recipients, transfers, retention, security_measures
- ROPA must be updated within 30 days of any material change
- ROPA must be available to supervisory authority on request
- Controller responsible for accuracy and completeness of all recorded fields

## Exception Handling
- Organizations <250 employees exempt from full ROPA unless processing is high-risk or involves special categories
- Public authorities must maintain ROPA regardless of size

## Success Criteria
- ROPA_completeness == 100% for all active activities
- last_updated <= 30 days from any change
- all_transfers_have_documented_legal_basis
- ROPA_exportable_in_machine_readable_format

## Compliance Requirements
- GDPR Art.30 mandatory
- DPA audit readiness
- accountability principle