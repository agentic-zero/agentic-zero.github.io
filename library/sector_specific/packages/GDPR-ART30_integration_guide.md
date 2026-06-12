# Integration Guide â€” gdpr_ropa_maintenance_agent
**Process:** Records of Processing Activities (ROPA)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp gdpr_ropa_maintenance_agent.py ./agents/
```

## Basic Usage
```python
from agents.gdpr_ropa_maintenance_agent import GdprRopaMaintenanceAgentAgent

agent = GdprRopaMaintenanceAgentAgent()
result = agent.execute({
    "processing_activities": your_processing_activities_data,
    "data_categories": your_data_categories_data,
    "purposes": your_purposes_data,
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
- ROPA_database_API
- schema_validator
- notification_service
- DPIA_risk_checker

## Escalation
The agent automatically escalates to human when:
- KPI remains <1.0 after automated update
- stale update >90 days
- audit notification with incomplete ROPA