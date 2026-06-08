# SOP — Stage Product (MTO)
**Process ID:** SCOR-M2.5
**Framework:** SCOR | **Domain:** Make
**Generated:** 2026-06-07

## Purpose
Process of staging MTO finished goods for outbound delivery including final inspection, documentation completion and handover to deliver operations

## Triggers
- Receipt of packaged products from SCOR-M2.4 with status=complete
- DeliverySchedule status changed to ready_for_staging

## Inputs Required
- packaged products
- delivery schedules
- documentation requirements
- staging area capacity
- customer delivery instructions

## Process Steps
1. IF StagingArea.capacity >= required_space THEN assign location ELSE queue or escalate
2. IF all compliance_flags satisfied THEN release documentation ELSE hold for review
3. IF customer_delivery_instructions.priority == 'urgent' THEN expedite staging within 2 hours

## Expected Outputs
- staged finished goods
- delivery documentation
- handover to deliver
- inventory update

## Business Rules
- staging_accuracy must be >= 99.5% verified by barcode scan
- documentation_completeness requires all mandatory fields populated before handover
- inventory_update must be written to InventoryRecord within 5 minutes of staging completion

## Exception Handling
- Missing dangerous_goods_documentation: hold shipment and notify compliance team
- StagingArea full: reroute to overflow area and update DeliverySchedule ETA
- GxP release missing for pharma item: block handover and require QA sign-off

## Success Criteria
- staging_accuracy == 100% via scan verification
- delivery_readiness_rate == true
- HandoverRecord created and accepted by SCOR-D2.1
- inventory_update committed with quantity delta

## Compliance Requirements
- GxP release if pharma
- dangerous goods documentation
- export documentation if applicable
- GDPR customer data