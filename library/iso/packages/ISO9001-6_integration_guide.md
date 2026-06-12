# Integration Guide â€” risk_opportunity_planner
**Process:** Planning — Risk and Opportunity Management
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp risk_opportunity_planner.py ./agents/
```

## Basic Usage
```python
from agents.risk_opportunity_planner import RiskOpportunityPlannerAgent

agent = RiskOpportunityPlannerAgent()
result = agent.execute({
    "context_analysis": your_context_analysis_data,
    "stakeholder_needs": your_stakeholder_needs_data,
    "quality_policy": your_quality_policy_data,
})
print(result['outputs'])
```

## Supported Systems
- SAP ECC
- SAP S/4HANA
- SAP EWM
- Oracle ERP Cloud
- Oracle JDE

## Tools Required
- RiskRegister_API
- PerformanceData_store
- ContextAnalysis_engine
- KPI_tracker
- notification_service

## Escalation
The agent automatically escalates to human when:
- missing owner on Risk
- defense sector without compliance_flags
- objective_achievement_rate <0.8 after revision attempt
- stale PerformanceData > review period