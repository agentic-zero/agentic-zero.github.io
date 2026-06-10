# Integration Guide — shop_floor_execution_controller
**Process:** Shop Floor Control & Execution
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp shop_floor_execution_controller.py ./agents/
```

## Basic Usage
```python
from agents.shop_floor_execution_controller import ShopFloorExecutionControllerAgent

agent = ShopFloorExecutionControllerAgent()
result = agent.execute({
    "work_orders": your_work_orders_data,
    "routings": your_routings_data,
    "work_center_capacity": your_work_center_capacity_data,
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
- MES_API
- ERP_workorder_dispatch
- Quality_Inspection_System
- OEE_Calculator

## Escalation
The agent automatically escalates to human when:
- materials unavailable or machine fault
- max rework attempts exceeded
- schedule adherence projected below 70%