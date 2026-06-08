# Integration Guide — produce_and_test_agent
**Process:** Produce and Test (MTO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp produce_and_test_agent.py ./agents/
```

## Basic Usage
```python
from agents.produce_and_test_agent import ProduceAndTestAgentAgent

agent = ProduceAndTestAgentAgent()
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
- ERP_workorder_api
- MES_routing_execution
- QMS_quality_plan
- test_equipment_interface
- compliance_logger

## Escalation
The agent automatically escalates to human when:
- equipment failure or missing quality plan
- test pass rate < 95% after root-cause attempt
- non-conforming result requiring deviation record