# Integration Guide — excess_product_return_agent
**Process:** Return Excess Product to Supplier
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp excess_product_return_agent.py ./agents/
```

## Basic Usage
```python
from agents.excess_product_return_agent import ExcessProductReturnAgentAgent

agent = ExcessProductReturnAgentAgent()
result = agent.execute({
    "return_shipment_schedule": your_return_shipment_schedule_data,
    "return_authorization": your_return_authorization_data,
    "product_preparation": your_product_preparation_data,
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
- supplier_erp_api
- planning_system
- carrier_api
- finance_system
- document_repository

## Escalation
The agent automatically escalates to human when:
- product expired beyond policy
- ProofOfDelivery missing after 48h
- shipment rejected due to inaccurate contents or missing compliance_flags