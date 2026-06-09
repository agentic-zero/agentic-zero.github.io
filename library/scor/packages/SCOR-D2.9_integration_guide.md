# Integration Guide — mto_pick_execution_agent
**Process:** Pick Product (MTO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp mto_pick_execution_agent.py ./agents/
```

## Basic Usage
```python
from agents.mto_pick_execution_agent import MtoPickExecutionAgentAgent

agent = MtoPickExecutionAgentAgent()
result = agent.execute({
    "pick_lists": your_pick_lists_data,
    "staging_locations": your_staging_locations_data,
    "order_documentation": your_order_documentation_data,
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
- WMS_API
- ScanSystem_interface
- InventoryManagementSystem
- PickList_trigger_listener

## Escalation
The agent automatically escalates to human when:
- Item not found at StagingLocation
- Quantity mismatch after scan
- Pick cycle time exceeds KPI threshold