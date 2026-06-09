# SOP — Capacity Planning & Rough-Cut
**Process ID:** BPMN-MFG-004
**Framework:**  | **Domain:** BPMN
**Generated:** 2026-06-09

## Purpose
Rough-cut capacity planning process from demand input to capacity commitment including resource loading, constraint identification and capacity adjustment decisions

## Triggers
- Demand Plan Available event published from demand planning system

## Inputs Required
- demand plan
- routing data
- capacity data
- shift patterns
- constraint data

## Process Steps
1. IF capacity_utilization >= 0.85 THEN CapacitySufficient=true ELSE CapacitySufficient=false
2. IF overtime_hours <= max_overtime_limit THEN OvertimeFeasible=true ELSE OvertimeFeasible=false
3. IF subcontract_cost <= internal_cost * 1.15 THEN SubcontractOption=true ELSE SubcontractOption=false
4. IF investment_roi_months <= 18 THEN InvestmentRequired=true ELSE InvestmentRequired=false

## Expected Outputs
- capacity plan
- bottleneck analysis
- investment recommendations
- production feasibility

## Business Rules
- capacity_utilization must be calculated as (total_load / available_capacity) per resource
- bottleneck_resolution_rate >= 0.9 required before CapacityPlanApproved
- plan_feasibility_rate must be validated against routing and shift data
- all compliance_flags (labor regulations, GDPR, financial reporting) must be checked before ApproveCapacityPlan
- automation_potential 0.75 requires human review on InvestmentRequired gateway

## Exception Handling
- If GDPR flag triggered by personal data in demand plan, route to Lane:Finance for anonymization before LoadDemandIntoCapacityModel
- If no feasible option after all gateways, escalate to Management with 48h SLA and mark process incomplete

## Success Criteria
- CapacityPlanApproved status set to true
- capacity_utilization between 0.75-0.95
- bottleneck_resolution_rate >= 0.9
- production_feasibility == true
- all KPIs logged with timestamp

## Compliance Requirements
- labor regulations
- GDPR if personal data
- financial reporting