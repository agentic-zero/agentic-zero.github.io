# Integration Guide — mto_transfer_orchestrator
**Process:** Transfer Product (MTO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp mto_transfer_orchestrator.py ./agents/
```

## Basic Usage
```python
from agents.mto_transfer_orchestrator import MtoTransferOrchestratorAgent

agent = MtoTransferOrchestratorAgent()
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
- verification_system_api
- erp_production_order_api
- wms_staging_api
- equipment_sensor_feed
- inventory_db_writer
- auth_service

## Escalation
The agent automatically escalates to human when:
- equipment unavailable beyond SLA timer
- quantity mismatch > 0 or unlogged lot_ids
- missing chain_of_custody or compliance_flags