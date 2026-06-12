# Integration Guide â€” mto_product_pick_agent
**Process:** Pick Product (MTO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp mto_product_pick_agent.py ./agents/
```

## Basic Usage
```python
from agents.mto_product_pick_agent import MtoProductPickAgentAgent

agent = MtoProductPickAgentAgent()
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
- ScanSystem_API
- WMS_interface
- ERP_PickList_connector
- PackStagingLocation_API

## Escalation
The agent automatically escalates to human when:
- Item not found at StagingLocation
- Scan mismatch or inventory discrepancy
- Inventory update exceeds 30s
- Pick accuracy fails OrderDocumentation validation