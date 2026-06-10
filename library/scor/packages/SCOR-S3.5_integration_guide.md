# Integration Guide â€” supplier_milestone_payment_authorizer
**Process:** Authorize Supplier Payment (ETO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp supplier_milestone_payment_authorizer.py ./agents/
```

## Basic Usage
```python
from agents.supplier_milestone_payment_authorizer import SupplierMilestonePaymentAuthorizerAgent

agent = SupplierMilestonePaymentAuthorizerAgent()
result = agent.execute({
    "milestone_completions": your_milestone_completions_data,
    "engineering_acceptance_reports": your_engineering_acceptance_reports_data,
    "supplier_invoices": your_supplier_invoices_data,
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
- financial_database_api
- invoice_system
- engineering_report_store
- compliance_engine

## Escalation
The agent automatically escalates to human when:
- partial milestone completion
- missing EngineeringAcceptanceReport after 24h
- milestone_completion_date exceeds due_date
- budget check failure