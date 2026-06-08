# Integration Guide — excess_product_return_authorization_agent
**Process:** Request Excess Product Return Authorization
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp excess_product_return_authorization_agent.py ./agents/
```

## Basic Usage
```python
from agents.excess_product_return_authorization_agent import ExcessProductReturnAuthorizationAgentAgent

agent = ExcessProductReturnAuthorizationAgentAgent()
result = agent.execute({
    "disposition_decision": your_disposition_decision_data,
    "excess_inventory_data": your_excess_inventory_data_data,
    "supplier_terms": your_supplier_terms_data,
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
- inventory_management_system_api
- supplier_contract_database
- business_rules_engine

## Escalation
The agent automatically escalates to human when:
- if supplier does not respond to excess return authorization request within 3 days
- if credit terms are not acceptable after 2 renegotiation attempts