# Integration Guide — defective_return_receipt_processor
**Process:** Receive Defective Product Return
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp defective_return_receipt_processor.py ./agents/
```

## Basic Usage
```python
from agents.defective_return_receipt_processor import DefectiveReturnReceiptProcessorAgent

agent = DefectiveReturnReceiptProcessorAgent()
result = agent.execute({
    "scheduled_return_shipment": your_scheduled_return_shipment_data,
    "rma_documentation": your_rma_documentation_data,
    "inspection_criteria": your_inspection_criteria_data,
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
- dock_scan_API
- RMA_lookup_service
- inventory_update_API
- inspection_criteria_engine
- exception_ticket_system

## Escalation
The agent automatically escalates to human when:
- serial mismatch or RMA invalid
- inspection cycle_time exceeds KPI
- GxP immutability violation detected