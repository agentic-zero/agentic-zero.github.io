# SOP — Good Distribution Practice (GDP)
**Process ID:** GXP-GDP
**Framework:** EU GDP Guidelines 2013/C 343/01 | **Domain:** GxP
**Generated:** 2026-06-12

## Purpose
Good Distribution Practice requirements for pharmaceutical distribution including quality system, personnel, premises, documentation, operations, complaints and returns management

## Triggers
- Customer order received in WMS
- Product receipt at warehouse dock
- Scheduled temperature monitoring interval

## Inputs Required
- product specifications
- storage requirements
- distribution routes
- customer qualifications
- temperature monitoring data

## Process Steps
1. IF temperature > StorageRequirement.max OR temperature < StorageRequirement.min THEN create TemperatureRecord.excursion and initiate investigation
2. IF Customer.qualification_status == false THEN reject distribution request
3. IF complaint received THEN log ComplaintRecord and trigger investigation within 24h

## Expected Outputs
- GDP-compliant distribution
- qualification records
- temperature records
- complaint records
- return records

## Business Rules
- All TemperatureRecord values must be logged every 15 minutes with timestamp and sensor_id
- Personnel must complete GDP training before handling products
- DistributionRoute must maintain continuous temperature chain compliance
- All QualificationRecord must be signed and version-controlled

## Exception Handling
- Temperature excursion < 30 minutes with documented risk assessment may be approved by QA
- Emergency distribution without full customer qualification requires documented deviation and post-approval within 48h

## Success Criteria
- GDP audit compliance rate == 100%
- temperature excursion rate < 0.5%
- delivery quality rate >= 99.5%
- All outputs generated with complete audit trail

## Compliance Requirements
- EU GDP Guidelines 2013
- WHO GDP
- GDPR serialization data
- temperature chain compliance