# Integration Guide — credit_risk_management_agent
**Process:** Credit Management & Risk Assessment
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp credit_risk_management_agent.py ./agents/
```

## Basic Usage
```python
from agents.credit_risk_management_agent import CreditRiskManagementAgentAgent

agent = CreditRiskManagementAgentAgent()
result = agent.execute({
    "customer_financial_data": your_customer_financial_data_data,
    "credit_bureau_data": your_credit_bureau_data_data,
    "payment_history": your_payment_history_data,
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
- ERP_financial_statements
- DunBradstreet_credit_API
- SAP_FSCM
- AML_screening_tool

## Escalation
The agent automatically escalates to human when:
- AML flag or missing bureau data
- Risk score <550 or limit >50000 without dual sign-off
- Payment history >90 days old