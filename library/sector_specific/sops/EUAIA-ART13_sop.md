# SOP — Transparency and User Information
**Process ID:** EUAIA-ART13
**Framework:** EU AI Act 2024 | **Domain:** EU AI Act
**Generated:** 2026-06-10

## Purpose
Transparency requirements for high-risk AI systems including instructions for use, capability and limitation disclosure and information enabling users to interpret AI outputs correctly

## Triggers
- High-risk AI system registration in deployment pipeline
- New version of AI_System released
- User access request to system documentation

## Inputs Required
- AI system capabilities
- limitation assessments
- use case definitions
- user profile
- output interpretability

## Process Steps
1. IF User_Profile.expertise_level == 'non-technical' THEN generate simplified Instructions_For_Use
2. IF Limitations_Assessment.critical == true THEN include in every Transparency_Documentation
3. IF sector in ['defense','pharma'] THEN add sector_specific compliance_flags to documentation

## Expected Outputs
- instructions for use
- transparency documentation
- user guidance
- limitation disclosures
- interpretability reports

## Business Rules
- Transparency_Documentation must include all items from Capabilities_List and Limitations_Assessment before deployment
- User_Comprehension_Metric must be measured via post-use survey with minimum 80% threshold
- All outputs must contain explicit limitation disclosures per EU AI Act Art.13

## Exception Handling
- IF automation_potential < 0.3 THEN require manual legal review before publishing Transparency_Documentation
- IF use_case is internal-only and no external users THEN skip user_guidance generation

## Success Criteria
- Transparency_Documentation completeness score == 100% on all mandatory fields
- User_Comprehension_Metric >= 0.8
- Transparency audit score passes external review

## Compliance Requirements
- EU AI Act Art.13 mandatory
- explainability requirements
- user rights