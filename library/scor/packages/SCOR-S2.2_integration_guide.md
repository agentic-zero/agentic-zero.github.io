# Integration Guide — mto_product_receiving_agent
**Process:** Receive Product (MTO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp mto_product_receiving_agent.py ./agents/
```

## Basic Usage
```python
from agents.mto_product_receiving_agent import MtoProductReceivingAgentAgent

agent = MtoProductReceivingAgentAgent()
result = agent.execute({
    "delivery_schedule": your_delivery_schedule_data,
    "purchase_orders": your_purchase_orders_data,
    "quality_specifications": your_quality_specifications_data,
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
- ERP_system
- WMS
- Quality_management_system
- RFID_dock_scanner
- ASN_interface

## Escalation
The agent automatically escalates to human when:
- rejection_rate exceeds threshold requiring supplier notification
- dock capacity overload triggering reschedule
- missing compliance docs causing process hold