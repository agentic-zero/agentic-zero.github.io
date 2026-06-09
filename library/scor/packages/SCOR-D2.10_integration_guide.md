# Integration Guide — mto_packing_agent
**Process:** Pack Product (MTO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp mto_packing_agent.py ./agents/
```

## Basic Usage
```python
from agents.mto_packing_agent import MtoPackingAgentAgent

agent = MtoPackingAgentAgent()
result = agent.execute({
    "picked_products": your_picked_products_data,
    "packing_specifications": your_packing_specifications_data,
    "labels": your_labels_data,
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
- barcode_scanner
- wms_api
- erp_system
- compliance_database
- label_printer
- staging_queue_listener

## Escalation
The agent automatically escalates to human when:
- quantity mismatch or damaged item triggers inventory reconciliation/quarantine
- cycle_time exceeds threshold notifies supervisor
- missing label data escalates to order management