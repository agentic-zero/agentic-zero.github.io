# Integration Guide — mto_receive_finished_goods_agent
**Process:** Receive Product from Source or Make (MTO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp mto_receive_finished_goods_agent.py ./agents/
```

## Basic Usage
```python
from agents.mto_receive_finished_goods_agent import MtoReceiveFinishedGoodsAgentAgent

agent = MtoReceiveFinishedGoodsAgentAgent()
result = agent.execute({
    "production_completion_notice": your_production_completion_notice_data,
    "quality_release": your_quality_release_data,
    "finished_goods": your_finished_goods_data,
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
- wms_api
- qa_system_connector
- manufacturing_notice_listener
- inventory_db_writer
- compliance_logger

## Escalation
The agent automatically escalates to human when:
- QualityRelease rejected or packaging failed
- Missing DeliveryDocumentation after SLA window
- System write failure on DeliverInventoryUpdate
- ReceiveAccuracy or InventoryAccuracy below target