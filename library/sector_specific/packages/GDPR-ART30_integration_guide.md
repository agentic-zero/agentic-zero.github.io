# Integration Guide â€” gdpr_ropa_automation_agent
**Process:** Records of Processing Activities (ROPA)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp gdpr_ropa_automation_agent.py ./agents/
```

## Basic Usage
```python
from agents.gdpr_ropa_automation_agent import GdprRopaAutomationAgentAgent

agent = GdprRopaAutomationAgentAgent()
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
- data_inventory_api
- document_management_system
- notification_service
- compliance_export_generator

## Escalation
The agent automatically escalates to human when:
- high_risk_processing_without_documentation
- update_deadline_exceeded_30_days
- dpa_audit_notification_received