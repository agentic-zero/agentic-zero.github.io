# SOP — Schedule Defective Product Return Receipt
**Process ID:** SCOR-DR1.2
**Framework:** SCOR | **Domain:** Return
**Generated:** 2026-06-07

## Purpose
Process of scheduling and coordinating the receipt of defective product returns from customers including dock scheduling and inspection resource allocation

## Triggers
- Valid RMA_Authorization received AND Customer_Shipment_Notice received

## Inputs Required
- RMA authorization
- customer shipment notice
- warehouse capacity
- inspection resources

## Process Steps
1. IF sector == 'pharma' THEN enforce GxP compliance check before scheduling
2. IF product.requires_cold_chain == true THEN allocate temperature-controlled dock and inspection resources
3. IF warehouse_capacity.available < required_space THEN reject or reschedule appointment

## Expected Outputs
- receipt schedule
- dock appointment
- inspection plan

## Business Rules
- Dock_Appointment must not exceed 85% daily utilization
- Inspection_Plan must assign at least one qualified inspector per return batch
- Receipt_Schedule must be generated within 4 hours of valid RMA + shipment notice receipt

## Exception Handling
- Invalid RMA: reject scheduling and send rejection notification to customer within 1 hour
- Insufficient capacity: auto-escalate to warehouse manager and propose next available slot
- Missing compliance data: hold scheduling until GxP or cold-chain verification is provided

## Success Criteria
- Receipt_Schedule status == 'confirmed' AND Dock_Appointment assigned AND Inspection_Plan resources allocated
- All compliance_flags satisfied for sector

## Compliance Requirements
- GxP if pharma
- cold chain if required
- health and safety regulations