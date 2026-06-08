# SOP — Manage IoT and Sensor Data Streams
**Process ID:** SCOR-DIG2
**Framework:** SCOR-Digital | **Domain:** Digital Enable
**Generated:** 2026-06-08

## Purpose
Process of managing end-to-end IoT infrastructure including sensor deployment, data ingestion, stream processing and real-time event management to feed autonomous supply chain agents

## Triggers
- Continuous arrival of sensor_readings or device_telemetry on ingestion topic

## Inputs Required
- sensor readings
- device telemetry
- environmental data
- location data
- equipment signals

## Process Steps
1. IF data_latency_ms > 100 THEN emit AnomalyAlert
2. IF sensor_uptime_pct < 99.0 THEN create SensorPerformanceReport with maintenance flag
3. IF data_quality_rate < 0.95 THEN quarantine DataStream and log exception

## Expected Outputs
- clean data streams
- real-time event triggers
- anomaly alerts
- sensor performance reports
- data quality metrics

## Business Rules
- All sensor_readings must be timestamped with UTC and device_id
- GDPR IoT data collection consent flag required before ingestion
- EU AI Act Art.10 data quality checks must run on every batch
- cybersecurity IoT standards encryption required for device_telemetry

## Exception Handling
- Missing device_telemetry: substitute last valid reading for max 300 seconds then raise AnomalyAlert
- Location data absent in pharma sector: block EventTrigger and log compliance violation

## Success Criteria
- sensor_uptime >= 0.99
- data_latency_ms <= 100
- data_quality_rate >= 0.95
- event_detection_accuracy >= 0.95

## Compliance Requirements
- GDPR IoT data collection
- EU AI Act data quality Art.10
- cybersecurity IoT standards
- industry-specific sensor regulations