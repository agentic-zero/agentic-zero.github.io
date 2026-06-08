# SOP — Manage Supply Chain Assets
**Process ID:** SCOR-E5
**Framework:** SCOR | **Domain:** Enable
**Generated:** 2026-06-07

## Purpose
Process of managing physical and digital assets across the supply chain including equipment, facilities, technology infrastructure and IoT devices that support autonomous operations

## Triggers
- Scheduled daily/weekly asset review cron job
- Real-time threshold breach on AssetPerformanceData stream
- New CapitalPlan or TechnologyRoadmap version published

## Inputs Required
- asset registry
- maintenance schedules
- asset performance data
- capital plans
- technology roadmap

## Process Steps
1. IF assetUptime < 0.95 THEN generate MaintenancePlan
2. IF maintenanceComplianceRate < 0.98 THEN escalate to compliance audit
3. IF returnOnAssets < target THEN produce InvestmentRecommendation

## Expected Outputs
- asset utilization reports
- maintenance plans
- lifecycle assessments
- investment recommendations
- asset performance dashboards

## Business Rules
- All assets must comply with ISO 55001 registry requirements
- MaintenanceSchedule must be executed within SLA window defined in maintenance schedules
- Environmental compliance checks required before LifecycleAssessment approval

## Exception Handling
- IoT device offline: switch to last-known AssetPerformanceData and flag for manual inspection within 24h
- CapitalPlan budget exceeded: defer non-critical InvestmentRecommendation and log exception

## Success Criteria
- asset_utilization_rate >= target AND maintenance_compliance_rate >= 0.98 AND asset_uptime >= 0.95
- All outputs (reports, plans, dashboards) generated and stored within SLA

## Compliance Requirements
- ISO 55001 asset management
- EU AI Act infrastructure
- environmental compliance
- safety regulations