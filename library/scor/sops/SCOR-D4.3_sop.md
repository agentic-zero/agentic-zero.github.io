# SOP — Pick Product in Store
**Process ID:** SCOR-D4.3
**Framework:** SCOR | **Domain:** Deliver
**Generated:** 2026-06-08

## Purpose
Process of picking products for store replenishment, click-and-collect or e-commerce fulfillment from retail backroom or floor inventory

## Triggers
- new ReplenishmentSignal received
- new CustomerOrder received

## Inputs Required
- replenishment signals
- customer orders
- store inventory
- picking equipment
- planogram data

## Process Steps
1. IF product location in PlanogramData is backroom THEN select backroom pick path
2. IF CustomerOrder.channel is click-and-collect THEN set priority flag and target completion under 2 hours
3. IF StoreInventory.quantity < order_quantity THEN check substitution rules or flag exception

## Expected Outputs
- picked products
- inventory depletion records
- pick accuracy data
- fulfillment confirmation

## Business Rules
- food_safety_handling: true for all food sector SKUs before pick
- log_pick_accuracy: record correct vs incorrect picks after every task
- GDPR_compliance: anonymize customer_order_data after FulfillmentConfirmation

## Exception Handling
- out_of_stock: log exception, trigger substitution workflow or notify customer, update InventoryDepletionRecord with zero quantity

## Success Criteria
- pick_accuracy >= 0.99
- pick_cycle_time <= target_minutes
- FulfillmentConfirmation generated with no open exceptions
- InventoryDepletionRecord updated in real time

## Compliance Requirements
- food safety handling
- GDPR customer order data
- health and safety