# Integration Guide — field_service_automation_agent
**Process:** After-Sales Service & Field Service
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp field_service_automation_agent.py ./agents/
```

## Basic Usage
```python
from agents.field_service_automation_agent import FieldServiceAutomationAgentAgent

agent = FieldServiceAutomationAgentAgent()
result = agent.execute({
    "service_request": your_service_request_data,
    "equipment_data": your_equipment_data_data,
    "service_history": your_service_history_data,
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
- CRM_API
- inventory_system
- scheduling_engine
- finance_billing_API
- GDPR_consent_logger
- asset_DB

## Escalation
The agent automatically escalates to human when:
- Parts unavailable after OrderParts
- CustomerSatisfied == false after TestVerify
- Equipment cannot be repaired
- SLA breach within 24h window