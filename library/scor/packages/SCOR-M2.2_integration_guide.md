# Integration Guide — mto_material_issue_controller
**Process:** Issue Sourced/In-Process Product (MTO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp mto_material_issue_controller.py ./agents/
```

## Basic Usage
```python
from agents.mto_material_issue_controller import MtoMaterialIssueControllerAgent

agent = MtoMaterialIssueControllerAgent()
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
- ERP_workorder_api
- WMS_picklist_api
- inventory_system_lot_lookup
- shop_floor_terminal_interface
- barcode_scanner_validation

## Escalation
The agent automatically escalates to human when:
- missing lot number detected
- negative WIP balance found
- kitting accuracy below 99% after recount
- WorkOrder status not released