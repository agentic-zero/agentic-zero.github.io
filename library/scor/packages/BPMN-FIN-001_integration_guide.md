# Integration Guide â€” invoice_to_cash_automation_agent
**Process:** Invoice-to-Cash (Accounts Receivable)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp invoice_to_cash_automation_agent.py ./agents/
```

## Basic Usage
```python
from agents.invoice_to_cash_automation_agent import InvoiceToCashAutomationAgentAgent

agent = InvoiceToCashAutomationAgentAgent()
result = agent.execute({
    "invoices": your_invoices_data,
    "payment_terms": your_payment_terms_data,
    "customer_data": your_customer_data_data,
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
- ERP_invoice_api
- bank_payment_feed
- customer_data_store
- dunning_messaging_service

## Escalation
The agent automatically escalates to human when:
- Dispute amount >5000 requires management approval
- Payment unapplied after 3 days triggers manual reconcile
- Escalated dunning notifies sales for lane customers