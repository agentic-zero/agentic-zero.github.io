# SOP — Schedule Defective Product Return Receipt
**Process ID:** SCOR-DR1.2
**Framework:** SCOR | **Domain:** Return
**Generated:** 2026-06-08

## Purpose
Process of scheduling and coordinating the receipt of defective product returns from customers including dock scheduling and inspection resource allocation

## Triggers
- Receipt of valid RMA_Authorization combined with Customer_Shipment_Notice

## Inputs Required
- RMA authorization
- customer shipment notice
- warehouse capacity
- inspection resources

## Process Steps
1. IF sector == 'pharma' THEN enforce GxP compliance on Inspection_Plan
2. IF product.requires_cold_chain THEN allocate temperature-controlled dock and resources
3. IF Warehouse_Capacity.available < required_space THEN reject or reschedule appointment

## Expected Outputs
- receipt schedule
- dock appointment
- inspection plan

## Business Rules
- RMA_Authorization must be valid and non-expired before scheduling
- Dock_Appointment must not exceed warehouse operating hours
- Inspection_Plan must allocate resources with efficiency >= KPI target
- All compliance_flags must be checked before confirming schedule

## Exception Handling
- Missing RMA_Authorization: halt process and request authorization from customer
- Insufficient Inspection_Resources: notify related_process SCOR-DR1.3 for resource reallocation
- Cold chain violation risk: flag and route to specialized handling or reject shipment

## Success Criteria
- Receipt_Schedule created with scheduling accuracy >= 95%
- Dock_Appointment confirmed with utilization >= 80%
- Inspection_Plan generated meeting resource efficiency KPI

## Compliance Requirements
- GxP if pharma
- cold chain if required
- health and safety regulations