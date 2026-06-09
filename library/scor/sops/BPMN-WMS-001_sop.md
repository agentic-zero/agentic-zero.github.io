# SOP — Warehouse Inbound Operations
**Process ID:** BPMN-WMS-001
**Framework:**  | **Domain:** BPMN
**Generated:** 2026-06-08

## Purpose
Warehouse inbound process from delivery appointment to putaway including receiving, inspection, labeling and inventory update

## Triggers
- DeliveryAppointmentConfirmed event received from supplier portal

## Inputs Required
- advance shipment notice
- purchase orders
- quality specs
- warehouse capacity
- dock schedule

## Process Steps
1. IF QualityOK == true THEN LabelProducts ELSE RejectShipment
2. IF QuantityMatch == true THEN QualityInspect ELSE RequestASNCorrection
3. IF Hazardous == true THEN AssignSpecialLocation ELSE AssignStandardLocation
4. IF TemperatureOK == true THEN Putaway ELSE HoldForTemperatureCorrection

## Expected Outputs
- received inventory
- quality report
- putaway confirmation
- inventory update

## Business Rules
- receiving_accuracy >= 0.99
- dock_to_stock_time <= 24 hours
- GxP compliance required when sector == pharma
- cold_chain_maintained == true when product.temperature_controlled == true
- GDPR redaction applied when shipment contains personal_data

## Exception Handling
- Quantity mismatch > 2 percent: create discrepancy report and hold goods in quarantine until PO amendment
- QualityInspectionResult == fail: route to return or rework lane and log rejection in quality_report
- Temperature breach: quarantine shipment and trigger compliance alert to SystemLane

## Success Criteria
- end_event == StockAvailable
- putaway_confirmation timestamp recorded
- inventory_update committed with quantity delta > 0
- kpi.receiving_accuracy >= 0.99 and kpi.dock_to_stock_time <= 24

## Compliance Requirements
- GxP if pharma
- cold chain
- GDPR if personal data
- food safety