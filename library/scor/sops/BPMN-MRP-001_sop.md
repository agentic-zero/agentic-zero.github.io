# SOP — Material Requirements Planning
**Process ID:** BPMN-MRP-001
**Framework:**  | **Domain:** BPMN
**Generated:** 2026-06-08

## Purpose
MRP process from demand input to production order release including BOM explosion, capacity check, material availability and work order generation

## Triggers
- Demand Signal Received start event from sales_orders or demand_forecast

## Inputs Required
- demand forecast
- sales orders
- BOM
- inventory levels
- capacity data
- lead times

## Process Steps
1. IF MaterialAvailable == false THEN generate PurchaseRequisition
2. IF CapacityAvailable == false THEN raise Exception
3. IF Exception == true THEN route to Management lane for approval
4. IF ApprovePlan == true THEN convert PlannedOrder to ProductionOrder

## Expected Outputs
- production orders
- purchase requisitions
- capacity plan
- material shortage alerts

## Business Rules
- NetRequirement = GrossRequirement - Inventory - ScheduledReceipts
- Capacity check must complete before GeneratePlannedOrders
- ProductionOrder release requires ApprovePlan == true
- All pharma sector runs must set compliance_flags = GxP

## Exception Handling
- Material shortage triggers MaterialShortageAlert and Procurement lane
- Capacity overload routes to Exception gateway and Management lane review
- ApprovePlan == false cancels PlannedOrder and logs exception_rate KPI

## Success Criteria
- Production Orders Released end event reached
- planning_accuracy >= 0.95
- material_availability_rate >= 0.98
- exception_rate <= 0.05

## Compliance Requirements
- GxP if pharma
- production scheduling compliance
- GDPR if personal data