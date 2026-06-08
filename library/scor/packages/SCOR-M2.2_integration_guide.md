# Integration Guide — mto_material_issue_agent
**Process:** Issue Sourced/In-Process Product (MTO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp mto_material_issue_agent.py ./agents/
```

## Basic Usage
```python
from agents.mto_material_issue_agent import MtoMaterialIssueAgentAgent

agent = MtoMaterialIssueAgentAgent()
result = agent.execute({
    "production_schedule": your_production_schedule_data,
    "material_pick_lists": your_material_pick_lists_data,
    "wip_inventory": your_wip_inventory_data,
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
- Scan_Verification_System
- GxP_Batch_Recorder

## Escalation
The agent automatically escalates to human when:
- kitting_accuracy <99.5%
- missing pick-list items
- unresolved WIP discrepancy
- GxP batch traceability failure