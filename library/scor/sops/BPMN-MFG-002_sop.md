# SOP — Maintenance Work Order Management (MRO)
**Process ID:** BPMN-MFG-002
**Framework:**  | **Domain:** BPMN
**Generated:** 2026-06-09

## Purpose
Maintenance work order process from breakdown or planned maintenance trigger to equipment return to service including diagnosis, parts procurement, execution and history update

## Triggers
- Breakdown alert received from sensor/operator
- PM schedule event fired from CMMS calendar

## Inputs Required
- breakdown alert
- PM schedule
- equipment history
- spare parts inventory
- maintenance procedures

## Process Steps
1. IF Emergency? THEN set priority=1 and skip queue ELSE normal scheduling
2. IF Parts Available? THEN proceed to ScheduleMaintenance ELSE create ProcurementRequest
3. IF Repair Feasible? THEN ExecuteMaintenance ELSE set end_event=EquipmentDecommissioned
4. IF Test Passed? THEN UpdateEquipmentHistory and CloseWorkOrder ELSE loop to DiagnoseFault

## Expected Outputs
- completed work order
- equipment history update
- parts consumption
- OEE data

## Business Rules
- WorkOrder.status must transition only through valid states: Created->Diagnosed->Scheduled->Executed->Verified->Closed
- Every WorkOrder must reference equipment_id and at least one task from the predefined task list
- Update EquipmentHistory before allowing CloseWorkOrder
- Sector=pharma requires GxP qualification flag on WorkOrder

## Exception Handling
- Repair not feasible: transition directly to EquipmentDecommissioned and archive WorkOrder
- Parts unavailable after 3 procurement attempts: escalate to engineering review and update MTTR KPI

## Success Criteria
- end_event=EquipmentReturnedToService
- WorkOrder.status=Closed
- EquipmentHistory record created with OEE delta
- All KPIs (MTTR, MTBF, PM compliance) updated

## Compliance Requirements
- GxP equipment qualification if pharma
- safety regulations
- GDPR if personal data
- ATEX if applicable