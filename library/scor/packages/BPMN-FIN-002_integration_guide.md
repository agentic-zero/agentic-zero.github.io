# Integration Guide — accounts_payable_automation_agent
**Process:** Accounts Payable Automation
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp accounts_payable_automation_agent.py ./agents/
```

## Basic Usage
```python
from agents.accounts_payable_automation_agent import AccountsPayableAutomationAgentAgent

agent = AccountsPayableAutomationAgentAgent()
result = agent.execute({
    "supplier_invoices": your_supplier_invoices_data,
    "purchase_orders": your_purchase_orders_data,
    "goods_receipts": your_goods_receipts_data,
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
- OCR_engine
- ERP_API
- BankSystem_API
- Approval_workflow_tool

## Escalation
The agent automatically escalates to human when:
- Duplicate detected
- 3-way match failure unresolved >24h
- Tolerance breach requiring approver
- Payment blocked by compliance flag