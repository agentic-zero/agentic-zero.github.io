# Integration Guide — mto_invoice_processor
**Process:** Invoice (MTO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp mto_invoice_processor.py ./agents/
```

## Basic Usage
```python
from agents.mto_invoice_processor import MtoInvoiceProcessorAgent

agent = MtoInvoiceProcessorAgent()
result = agent.execute({
    "delivery_confirmation": your_delivery_confirmation_data,
    "order_data": your_order_data_data,
    "pricing_data": your_pricing_data_data,
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
- ERP_API
- CRM_API
- PricingEngine
- TaxComplianceService
- DeliveryConfirmationListener

## Escalation
The agent automatically escalates to human when:
- invoice_accuracy_rate < 0.98
- payment_terms_conflict
- compliance_violation_detected