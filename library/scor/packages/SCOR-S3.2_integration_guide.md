# Integration Guide — eto_receiving_inspection_agent
**Process:** Receive Engineer-to-Order Product
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp eto_receiving_inspection_agent.py ./agents/
```

## Basic Usage
```python
from agents.eto_receiving_inspection_agent import EtoReceivingInspectionAgentAgent

agent = EtoReceivingInspectionAgentAgent()
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
- document_parser
- certificate_verifier_api
- inventory_management_system
- project_bom_updater
- export_control_checker

## Escalation
The agent automatically escalates to human when:
- missing certificates after 4 hours
- documentation mismatch or export control violation
- first-pass inspection failure requiring rework/rejection