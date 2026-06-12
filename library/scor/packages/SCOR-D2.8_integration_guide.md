# Integration Guide â€” finished_goods_receipt_agent
**Process:** Receive Product from Source or Make (MTO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp finished_goods_receipt_agent.py ./agents/
```

## Basic Usage
```python
from agents.finished_goods_receipt_agent import FinishedGoodsReceiptAgentAgent

agent = FinishedGoodsReceiptAgentAgent()
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
- ERP_api
- WMS_integration
- quality_control_system
- packaging_inspection_module

## Escalation
The agent automatically escalates to human when:
- Missing QualityRelease route to exception queue and notify SCOR-M2.5
- Failed quality check reject goods and trigger return/rework
- InventoryAccuracy below threshold trigger cycle count