# Integration Guide — eto_order_validation_agent
**Process:** Receive, Configure, Enter and Validate ETO Order
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp eto_order_validation_agent.py ./agents/
```

## Basic Usage
```python
from agents.eto_order_validation_agent import EtoOrderValidationAgentAgent

agent = EtoOrderValidationAgentAgent()
result = agent.execute({
    "customer_technical_requirements": your_customer_technical_requirements_data,
    "sow": your_sow_data,
    "feasibility_data": your_feasibility_data_data,
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
- Engineering_DB
- Risk_Engine
- ERP
- Compliance_Service

## Escalation
The agent automatically escalates to human when:
- Missing engineering_capacity data after 24h auto-query
- Non-compliant export_control detected
- requirement_capture_accuracy <0.95
- feasibility_score <0.7 or risk_level >medium