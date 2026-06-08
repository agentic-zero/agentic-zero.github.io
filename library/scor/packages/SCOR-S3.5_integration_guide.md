# Integration Guide — milestone_payment_authorizer
**Process:** Authorize Supplier Payment (ETO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp milestone_payment_authorizer.py ./agents/
```

## Basic Usage
```python
from agents.milestone_payment_authorizer import MilestonePaymentAuthorizerAgent

agent = MilestonePaymentAuthorizerAgent()
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
- ERP_invoice_api
- engineering_acceptance_db
- contract_terms_store
- financial_update_service
- compliance_checker

## Escalation
The agent automatically escalates to human when:
- missing EngineeringAcceptanceReport
- invoice mismatch > 2%
- contract compliance rate < 95%
- government_contracting compliance_flags detected