# Integration Guide — export_control_clearance_agent
**Process:** Export Control Clearance
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp export_control_clearance_agent.py ./agents/
```

## Basic Usage
```python
from agents.export_control_clearance_agent import ExportControlClearanceAgentAgent

agent = ExportControlClearanceAgentAgent()
result = agent.execute({
    "product_eccn_classification": your_product_eccn_classification_data,
    "customer_data": your_customer_data_data,
    "country_data": your_country_data_data,
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
- ERP order event listener
- DeniedPartyList API
- ECCN classification database
- License application portal
- AES filing service
- OFAC/ITAR screening engine

## Escalation
The agent automatically escalates to human when:
- Party matches DeniedPartyList
- License application rejected
- Missing ECCN classification after timeout
- License validity window expires