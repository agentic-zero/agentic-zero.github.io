# Integration Guide — controlled_item_serialization_agent
**Process:** Controlled Item & Serialization Management
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp controlled_item_serialization_agent.py ./agents/
```

## Basic Usage
```python
from agents.controlled_item_serialization_agent import ControlledItemSerializationAgentAgent

agent = ControlledItemSerializationAgentAgent()
result = agent.execute({
    "item_specifications": your_item_specifications_data,
    "serial_numbers": your_serial_numbers_data,
    "classification_data": your_classification_data_data,
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
- serial_registry_api
- custody_record_db
- regulatory_reporting_system
- classification_validator
- audit_logger

## Escalation
The agent automatically escalates to human when:
- Transfer not authorized
- Serial number collision detected
- Missing classification data
- Report SLA breach