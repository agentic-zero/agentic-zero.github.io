# Integration Guide — supplier_payment_authorizer
**Process:** Authorize Supplier Payment (MTO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp supplier_payment_authorizer.py ./agents/
```

## Basic Usage
```python
from agents.supplier_payment_authorizer import SupplierPaymentAuthorizerAgent

agent = SupplierPaymentAuthorizerAgent()
result = agent.execute({
    "supplier_invoices": your_supplier_invoices_data,
    "goods_receipts": your_goods_receipts_data,
    "purchase_orders": your_purchase_orders_data,
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
- ERP_api
- WMS_api
- QMS_api
- email_workflow_tool
- Supplier_master_api

## Escalation
The agent automatically escalates to human when:
- three-way mismatch exceeds 0.01 tolerance
- QualityVerificationResult.status == 'failed'
- missing data blocks authorization beyond SLA