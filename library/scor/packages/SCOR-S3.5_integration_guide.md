# Integration Guide — supplier_payment_authorization_agent
**Process:** Authorize Supplier Payment (ETO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp supplier_payment_authorization_agent.py ./agents/
```

## Basic Usage
```python
from agents.supplier_payment_authorization_agent import SupplierPaymentAuthorizationAgentAgent

agent = SupplierPaymentAuthorizationAgentAgent()
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
- engineering_system_api
- contract_management_system
- supplier_erp
- financial_reporting_api

## Escalation
The agent automatically escalates to human when:
- EngineeringAcceptanceReport rejected
- export_control_financial_flag active
- amount mismatch or budget shortfall
- compliance rate below 0.95