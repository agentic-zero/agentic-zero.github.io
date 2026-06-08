# Integration Guide — mro_product_return_agent
**Process:** Return MRO Product to Supplier
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp mro_product_return_agent.py ./agents/
```

## Basic Usage
```python
from agents.mro_product_return_agent import MroProductReturnAgentAgent

agent = MroProductReturnAgentAgent()
result = agent.execute({
    "mro_shipment_schedule": your_mro_shipment_schedule_data,
    "return_authorization": your_return_authorization_data,
    "packaging": your_packaging_data,
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
- supplier_api
- packaging_provider_api
- carrier_api
- gdpr_compliance_tool

## Escalation
The agent automatically escalates to human when:
- if return authorization is denied
- if shipment is lost or damaged
- if credit confirmation is disputed