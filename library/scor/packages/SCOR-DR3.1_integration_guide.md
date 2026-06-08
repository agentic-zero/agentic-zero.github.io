# Integration Guide — excess_return_authorization_agent
**Process:** Authorize Excess Product Return
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp excess_return_authorization_agent.py ./agents/
```

## Basic Usage
```python
from agents.excess_return_authorization_agent import ExcessReturnAuthorizationAgentAgent

agent = ExcessReturnAuthorizationAgentAgent()
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
- CRM_API
- WMS_API
- ERP_API
- Policy_Engine
- Forecasting_Service

## Escalation
The agent automatically escalates to human when:
- credit_terms negotiation timeout after 72 hours
- missing GDPR consent flag
- perishable expiry violation