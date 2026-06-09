# Integration Guide — defective_return_receipt_scheduler
**Process:** Schedule Defective Product Return Receipt
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp defective_return_receipt_scheduler.py ./agents/
```

## Basic Usage
```python
from agents.defective_return_receipt_scheduler import DefectiveReturnReceiptSchedulerAgent

agent = DefectiveReturnReceiptSchedulerAgent()
result = agent.execute({
    "rma_authorization": your_rma_authorization_data,
    "customer_shipment_notice": your_customer_shipment_notice_data,
    "warehouse_capacity": your_warehouse_capacity_data,
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
- RMA_validation_API
- Warehouse_capacity_API
- Scheduling_engine
- Compliance_checker

## Escalation
The agent automatically escalates to human when:
- Missing or invalid RMA
- Insufficient resources after reallocation
- Cold chain or GxP violation risk