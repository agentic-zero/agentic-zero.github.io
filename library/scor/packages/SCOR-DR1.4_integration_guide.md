# Integration Guide — defective_product_transfer_agent
**Process:** Transfer Defective Product Return
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp defective_product_transfer_agent.py ./agents/
```

## Basic Usage
```python
from agents.defective_product_transfer_agent import DefectiveProductTransferAgentAgent

agent = DefectiveProductTransferAgentAgent()
result = agent.execute({
    "inspection_report": your_inspection_report_data,
    "disposition_decision": your_disposition_decision_data,
    "warehouse_locations": your_warehouse_locations_data,
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
- warehouse_management_api
- transfer_resource_scheduler
- compliance_validator
- kpi_monitor

## Escalation
The agent automatically escalates to human when:
- Missing disposition decision triggers SCOR-DR1.3
- Hazardous material detected
- Transfer accuracy < 99% or cycle_time exceeded