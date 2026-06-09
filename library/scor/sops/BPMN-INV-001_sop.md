# SOP — Inventory Management & Replenishment
**Process ID:** BPMN-INV-001
**Framework:**  | **Domain:** BPMN
**Generated:** 2026-06-09

## Purpose
Inventory replenishment process from stock monitoring to purchase order creation including reorder point calculation, safety stock management and ABC classification

## Triggers
- scheduled InventoryMonitorTrigger every 24 hours
- real-time stock update event when quantity changes > 5%

## Inputs Required
- inventory levels
- demand forecast
- lead times
- safety stock parameters
- supplier data

## Process Steps
1. IF current_stock < reorder_point THEN CalculateOrderQuantity ELSE NoActionRequired
2. IF current_stock < safety_stock THEN ExpediteIfCritical
3. IF preferred_supplier_available == true THEN CreatePurchaseOrder ELSE SelectAlternativeSupplier
4. IF order_value > approval_threshold THEN ApproveOrder gateway ELSE auto-approve

## Expected Outputs
- replenishment orders
- stock alerts
- inventory reports
- reorder recommendations

## Business Rules
- ReorderPoint = (average_daily_demand * lead_time_days) + safety_stock
- SafetyStock = z_score * demand_std_dev * sqrt(lead_time_days)
- OrderQuantity = max(0, reorder_point - current_stock + demand_forecast_next_period)
- ABCClassification must be recalculated quarterly based on annual consumption value

## Exception Handling
- CriticalStock exception: bypass normal approval and trigger expedited PO within 4 hours
- NoPreferredSupplier: fallback to secondary supplier list and log supplier risk flag
- Approval rejection: return to CalculateOrderQuantity with 10% quantity reduction option

## Success Criteria
- ReplenishmentOrderPlaced with PO number generated
- stock_level restored above reorder_point within lead_time
- inventory_turnover >= target_kpi and stockout_rate == 0 for affected SKUs

## Compliance Requirements
- expiry management if pharma/food
- GDPR if personal data
- financial reporting