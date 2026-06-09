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
- inventory_management_api
- production_order_system
- staging_location_manager
- transfer_equipment_interface
- audit_logger

## Escalation
The agent automatically escalates to human when:
- Missing VerificationApproval
- StagingLocation unavailable after reroute attempt
- transfer accuracy < 99.5%
- WIP update cycle time breach