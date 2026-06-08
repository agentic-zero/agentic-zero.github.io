# SOP — Request Defective Product Return Authorization
**Process ID:** SCOR-SR1.3
**Framework:** SCOR | **Domain:** Return
**Generated:** 2026-06-07

## Purpose
Process of formally requesting return merchandise authorization (RMA) from supplier for defective products

## Triggers
- Detection of Defective Product
- Receipt of Defect Documentation

## Inputs Required
- disposition decision
- defect documentation
- supplier contact data
- return policy

## Process Steps
1. IF Defective Product is identified THEN initiate RMA request
2. IF RMA request is approved THEN generate Return Authorization Number

## Expected Outputs
- RMA request
- return authorization number
- supplier acknowledgment

## Business Rules
- RMA request must include Defect Documentation and Disposition Decision
- RMA request must comply with Return Policy and contractual agreements
- RMA approval rate must be tracked and reported

## Exception Handling
- IF Supplier does not respond to RMA request THEN escalate to Supplier management
- IF RMA request is denied THEN review and revise Disposition Decision

## Success Criteria
- RMA request is approved and Return Authorization Number is generated
- Defective Product is returned to Supplier
- RMA approval rate meets or exceeds target

## Compliance Requirements
- GxP if pharma
- GDPR if personal data in documentation
- contractual compliance