# SOP — Change Control Management
**Process ID:** BPMN-GXP-002
**Framework:**  | **Domain:** BPMN
**Generated:** 2026-06-09

## Purpose
Change control process from change request to implementation and closure including risk assessment, regulatory impact assessment, validation requirements and effectiveness check

## Triggers
- Change Request Initiated event from Initiator lane

## Inputs Required
- change request
- risk data
- regulatory requirements
- validation protocols
- approval matrix

## Process Steps
1. IF Regulatory Impact? == true THEN execute RegulatoryImpactAssessment and create regulatory filing
2. IF Validation Required? == true THEN execute DefineValidationPlan and ValidateChange
3. IF All Approvals Obtained? == false THEN route back to ObtainApprovals or reject
4. IF Effective? == true THEN execute CloseChange ELSE trigger rework or rejection

## Expected Outputs
- change record
- risk assessment
- regulatory filing if needed
- validation report
- training records

## Business Rules
- All tasks must record actor lane and timestamp for GxP audit trail
- RiskAssessment must be completed before any Approval
- Regulatory filing output required when RegulatoryImpactAssessment identifies impact
- EffectivenessCheck must pass before Change Closed state is allowed
- ERP integration must update Veeva Vault or SAP QM with ChangeRecord

## Exception Handling
- Change Rejected at any gateway routes directly to end event Change Rejected and logs rejection reason
- Missing approval from required lane blocks ObtainApprovals until resolved or escalated
- Validation failure after ImplementChange requires new ValidationPlan iteration

## Success Criteria
- Change Closed end event reached with EffectivenessCheck == true and all outputs generated
- change_success_rate KPI >= target and regulatory_compliance_rate == 100%

## Compliance Requirements
- GxP ICH Q10
- FDA 21 CFR
- EU GMP
- ISO 13485 medical devices