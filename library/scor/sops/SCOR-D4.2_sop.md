# SOP — Receive Product at Store
**Process ID:** SCOR-D4.2
**Framework:** SCOR | **Domain:** Deliver
**Generated:** 2026-06-08

## Purpose
Process of receiving products at retail stores including delivery verification, quantity check, quality inspection and inventory system update

## Triggers
- delivery truck arrival logged by dock sensor
- delivery_schedule time reached with status=pending

## Inputs Required
- delivery schedule
- purchase orders
- delivered products
- receiving equipment
- store inventory system

## Process Steps
1. IF delivered quantity matches PurchaseOrder THEN proceed to quality inspection ELSE create DiscrepancyReport
2. IF quality inspection passes THEN update inventory ELSE reject DeliveredProduct and log exception
3. IF cold chain compliance verified THEN accept ELSE reject and notify supplier

## Expected Outputs
- received products
- inventory update
- discrepancy reports
- supplier delivery performance data

## Business Rules
- receiving_accuracy must be >= 99% for every delivery
- all food products require temperature check before inventory update
- GDPR store data requires anonymization of any customer-linked receiving records
- cold chain compliance must be logged with timestamp and equipment ID

## Exception Handling
- quantity mismatch > 5%: auto-create DiscrepancyReport and hold products for 24h pending supplier confirmation
- failed quality inspection: reject batch, update SupplierDeliveryPerformanceData with failure flag, notify procurement

## Success Criteria
- inventory_update committed with zero discrepancies
- receiving_cycle_time <= target KPI
- SupplierDeliveryPerformanceData score updated >= threshold

## Compliance Requirements
- food safety receiving
- GDPR store data
- cold chain compliance
- retail compliance