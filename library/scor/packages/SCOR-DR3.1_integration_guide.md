# Integration Guide — excess_return_authorizer
**Process:** Authorize Excess Product Return
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp excess_return_authorizer.py ./agents/
```

## Basic Usage
```python
from agents.excess_return_authorizer import ExcessReturnAuthorizerAgent

agent = ExcessReturnAuthorizerAgent()
result = agent.execute({
    "excess_return_request": your_excess_return_request_data,
    "inventory_data": your_inventory_data_data,
    "customer_purchase_history": your_customer_purchase_history_data,
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
- customer_system_api
- erp_inventory_query
- policy_store_access
- compliance_logger

## Escalation
The agent automatically escalates to human when:
- pharma expiry compliance failure
- GDPR consent missing
- ReturnPolicy violation without negotiable quantity
- process timeout from missing data