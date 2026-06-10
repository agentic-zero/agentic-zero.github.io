# Integration Guide â€” mto_transfer_agent
**Process:** Transfer Product (MTO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp mto_transfer_agent.py ./agents/
```

## Basic Usage
```python
from agents.mto_transfer_agent import MtoTransferAgentAgent

agent = MtoTransferAgentAgent()
result = agent.execute({
    "verification_approval": your_verification_approval_data,
    "production_orders": your_production_orders_data,
    "staging_locations": your_staging_locations_data,
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
- WMS_API
- Verification_System
- Transfer_Sensor_Stream
- ChainOfCustody_Logger

## Escalation
The agent automatically escalates to human when:
- transfer_accuracy < 99 percent
- missing chain_of_custody in pharma/defense
- WIP update exceeds 5 minutes
- GxP signature absent when required