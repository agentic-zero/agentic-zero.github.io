# Integration Guide — mto_produce_test_agent
**Process:** Produce and Test (MTO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp mto_produce_test_agent.py ./agents/
```

## Basic Usage
```python
from agents.mto_produce_test_agent import MtoProduceTestAgentAgent

agent = MtoProduceTestAgentAgent()
result = agent.execute({
    "work_orders": your_work_orders_data,
    "production_routings": your_production_routings_data,
    "quality_plans": your_quality_plans_data,
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
- ERP_work_order_api
- MES_routing_execution
- test_equipment_interface
- quality_record_system

## Escalation
The agent automatically escalates to human when:
- first_pass_yield < 0.95 or test_pass_rate < 1.0 requiring root cause or rework
- missing calibration or compliance record blocks execution
- customer spec change or equipment downtime