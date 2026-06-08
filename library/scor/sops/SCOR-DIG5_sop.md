# SOP — Manage Digital Supply Chain Visibility
**Process ID:** SCOR-DIG5
**Framework:** SCOR-Digital | **Domain:** Digital Enable
**Generated:** 2026-06-08

## Purpose
Process of achieving and maintaining real-time end-to-end visibility across the supply chain network including inventory positions, order status, shipment tracking and supplier operational status

## Triggers
- New ERP/WMS/TMS record received
- Supplier feed or carrier_API push event
- IoT stream update exceeding configured threshold

## Inputs Required
- ERP data
- WMS data
- TMS data
- supplier feeds
- carrier APIs
- IoT streams

## Process Steps
1. IF data_freshness_minutes > 15 THEN trigger RealTimeAlert with severity=high
2. IF exception_detection_rate < 0.92 THEN generate ExceptionReport and notify related_processes
3. IF ETA_prediction_accuracy < 0.85 THEN recalculate using carrier_API + IoT_stream

## Expected Outputs
- visibility dashboard
- real-time alerts
- exception reports
- predicted ETAs
- inventory snapshots

## Business Rules
- All location and tracking data must satisfy GDPR compliance before storage in VisibilityDashboard
- Pharma sector requires serialization check on every InventorySnapshot
- Data freshness must be <=5 minutes for manufacturing and automotive sectors

## Exception Handling
- Missing carrier_API response: use last known TMS data and flag PredictedETA as degraded
- IoT stream dropout: switch to WMS/ERP fallback and reduce visibility_coverage_rate KPI

## Success Criteria
- visibility_coverage_rate >= 0.95
- data_freshness <= 5 minutes
- exception_detection_rate >= 0.92
- ETA_prediction_accuracy >= 0.90

## Compliance Requirements
- GDPR location and tracking data
- customs data regulations
- food traceability regulations
- pharma serialization requirements