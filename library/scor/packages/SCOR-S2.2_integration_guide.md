# Integration Guide — mto_receiving_agent
**Process:** Receive Product (MTO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp mto_receiving_agent.py ./agents/
```

## Basic Usage
```python
from agents.mto_receiving_agent import MtoReceivingAgentAgent

agent = MtoReceivingAgentAgent()
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
- erp_api
- qms_api
- wms_api
- aps_api

## Escalation
The agent automatically escalates to human when:
- unresolved quantity/spec mismatch
- dock capacity breach requiring manual reschedule
- failed inspection needing procurement disposition