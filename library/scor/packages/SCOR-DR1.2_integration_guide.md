# Integration Guide — defective_product_return_scheduler
**Process:** Schedule Defective Product Return Receipt
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp defective_product_return_scheduler.py ./agents/
```

## Basic Usage
```python
from agents.defective_product_return_scheduler import DefectiveProductReturnSchedulerAgent

agent = DefectiveProductReturnSchedulerAgent()
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
- erp_rma_api
- warehouse_management_system
- compliance_engine
- scheduling_optimizer
- notification_service

## Escalation
The agent automatically escalates to human when:
- insufficient capacity after proposing next slot
- missing GxP or cold-chain data after hold
- unresolved resource conflict exceeding 90% utilization