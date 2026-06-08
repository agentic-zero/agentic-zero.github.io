# SOP — Manage Digital Supply Chain Visibility
**Process ID:** SCOR-DIG5
**Framework:** SCOR-Digital | **Domain:** Digital Enable
**Generated:** 2026-06-07

## Purpose
Process of achieving and maintaining real-time end-to-end visibility across the supply chain network including inventory positions, order status, shipment tracking and supplier operational status

## Triggers
- New data received from any DataSource via webhook or polling
- Scheduled refresh every 60 seconds
- Manual trigger via VisibilityDashboard user action

## Inputs Required
- ERP data
- WMS data
- TMS data
- supplier feeds
- carrier APIs
- IoT streams

## Process Steps
1. IF data freshness > 5 minutes THEN trigger RealTimeAlert
2. IF exception detection rate < 95% THEN escalate ExceptionReport
3. IF ETA prediction accuracy < 85% THEN retrain prediction model

## Expected Outputs
- visibility dashboard
- real-time alerts
- exception reports
- predicted ETAs
- inventory snapshots

## Business Rules
- rule1: All location and tracking data must be anonymized per GDPR before storage
- rule2: Pharma serialization data must be validated against regulatory format before ingestion
- rule3: Visibility coverage rate must be calculated every 60 seconds across all DataSources
- rule4: Carrier API data must include timestamp and source identifier

## Exception Handling
- Missing supplier feed: log error, use last known value, and raise RealTimeAlert after 15 minutes
- TMS data latency > 10 minutes: mark affected shipments as stale in VisibilityDashboard and exclude from ETAPrediction
- IoT stream dropout: switch to carrier API backup and record in ExceptionReport

## Success Criteria
- visibility coverage rate >= 98%
- data freshness <= 2 minutes
- exception detection rate >= 95%
- ETA prediction accuracy >= 90%

## Compliance Requirements
- GDPR location and tracking data
- customs data regulations
- food traceability regulations
- pharma serialization requirements