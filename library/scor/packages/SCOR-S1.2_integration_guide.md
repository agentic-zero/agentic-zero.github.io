# Integration Guide — authorize_and_pay_agent
**Process:** Authorize and Pay for Products and Services
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp authorize_and_pay_agent.py ./agents/
```

## Basic Usage
```python
from agents.authorize_and_pay_agent import AuthorizeAndPayAgentAgent

agent = AuthorizeAndPayAgentAgent()
result = agent.execute({
    "purchase_orders": your_purchase_orders_data,
    "supplier_invoices": your_supplier_invoices_data,
    "receipts": your_receipts_data,
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
- procurement_system_api
- financial_system_api
- logistics_system_api

## Escalation
The agent automatically escalates to human when:
- payment_failure
- discrepancy_investigation_unresolved
- compliance_issue_detected