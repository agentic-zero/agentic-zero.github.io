# SOP — Leadership and Quality Policy
**Process ID:** ISO9001-5
**Framework:** ISO 9001:2015 | **Domain:** ISO 9001
**Generated:** 2026-06-10

## Purpose
Leadership commitment, quality policy establishment and communication, organizational roles responsibilities and authorities for the QMS

## Triggers
- fiscal_year_start
- organizational_structure_change
- external_audit_nonconformance

## Inputs Required
- strategic direction
- quality objectives
- organizational structure
- resource plans

## Process Steps
1. IF leadership_commitment_evidence exists AND resource_plans allocated THEN approve QualityPolicy
2. IF policy_communication_rate < 0.95 THEN trigger communication campaign

## Expected Outputs
- quality policy
- quality objectives
- role assignments
- management commitment evidence

## Business Rules
- QualityPolicy must be documented, signed by top management and reviewed annually
- All RoleAssignment entries must specify authority limits and reporting lines
- QualityObjectives must be measurable and linked to strategic_direction

## Exception Handling
- Organizations <50 employees may combine RoleAssignment entries for multiple functions if documented in ManagementReviewRecord
- If no regulatory change occurs, QualityPolicy review interval may extend to 24 months with documented justification

## Success Criteria
- policy_communication_rate >= 0.95
- objective_achievement_rate >= 0.80
- ManagementReviewRecord created within 12 months of prior review

## Compliance Requirements
- ISO 9001:2015 Clause 5
- corporate governance