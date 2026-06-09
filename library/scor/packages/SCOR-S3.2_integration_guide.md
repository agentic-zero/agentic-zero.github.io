# Integration Guide — eto_receiving_automation_agent
**Process:** Receive Engineer-to-Order Product
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp eto_receiving_automation_agent.py ./agents/
```

## Basic Usage
```python
from agents.eto_receiving_automation_agent import EtoReceivingAutomationAgentAgent

agent = EtoReceivingAutomationAgentAgent()
result = agent.execute({
    "eto_delivery": your_eto_delivery_data,
    "engineering_drawings": your_engineering_drawings_data,
    "test_reports": your_test_reports_data,
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
- ASN_notification_listener
- certificate_verification_api
- erp_inventory_system
- non_conformance_workflow_api
- kpi_logger

## Escalation
The agent automatically escalates to human when:
- Missing certificates: notify engineering within 4 hours and hold in quarantine
- Inspection failure: create NCR and escalate to SCOR-S3.3
- KPI threshold breach or compliance flag