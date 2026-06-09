# SOP — Stock Shelf
**Process ID:** SCOR-D4.4
**Framework:** SCOR | **Domain:** Deliver
**Generated:** 2026-06-08

## Purpose
Process of stocking retail shelves and display areas ensuring planogram compliance, FIFO rotation, price label accuracy and optimal product placement

## Triggers
- Event: products marked 'received' in inventory system
- Schedule: daily replenishment job at store opening
- Alert: on-shelf_availability KPI drops below threshold

## Inputs Required
- received products
- planogram data
- shelf capacity
- pricing data
- promotional instructions

## Process Steps
1. IF Product.category == 'perishable' THEN apply FIFO rotation by expiration_date before placement
2. IF Planogram.compliance < 100% THEN reposition Product until compliant
3. IF PromotionalInstruction.active == true THEN override standard placement for affected SKUs

## Expected Outputs
- stocked shelves
- planogram compliance records
- price accuracy
- promotional compliance

## Business Rules
- FIFO rotation required for all food sector products
- PriceLabel.price must exactly equal pricing_data.price for each Product
- Planogram compliance must reach 100% before process completion
- Shelf.replenishment_cycle_time must be logged on every run

## Exception Handling
- If received Product.damaged == true: quarantine item, create incident record, skip placement
- If planogram_data missing for SKU: log exception, apply default linear placement, flag for master data update

## Success Criteria
- on-shelf_availability >= 95%
- planogram_compliance_rate == 100%
- price_accuracy == 100%
- promotional_compliance == 100%

## Compliance Requirements
- food safety FIFO
- pricing accuracy regulations
- promotional compliance
- GDPR if loyalty data