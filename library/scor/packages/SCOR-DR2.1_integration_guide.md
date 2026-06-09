# Integration Guide — mro_return_authorization_agent
**Process:** Authorize MRO Product Return
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp mro_return_authorization_agent.py ./agents/
```

## Basic Usage
```python
from agents.mro_return_authorization_agent import MroReturnAuthorizationAgentAgent

agent = MroReturnAuthorizationAgentAgent()
result = agent.execute({
    "mro_return_request": your_mro_return_request_data,
    "purchase_history": your_purchase_history_data,
    "product_condition_assessment": your_product_condition_assessment_data,
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
- erp_api
- policy_engine
- product_assessment_api
- compliance_checker

## Escalation
The agent automatically escalates to human when:
- hazardous MRO requiring environmental_officer review
- GDPR personal_data without consent
- missing purchase_history after 24h auto-request