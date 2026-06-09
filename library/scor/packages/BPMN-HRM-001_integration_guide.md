# Integration Guide — production_scheduling_hybrid_agent
**Process:** Production Scheduling
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp production_scheduling_hybrid_agent.py ./agents/
```

## Basic Usage
```python
from agents.production_scheduling_hybrid_agent import ProductionSchedulingHybridAgentAgent

agent = ProductionSchedulingHybridAgentAgent()
result = agent.execute({
    "production_orders": your_production_orders_data,
    "bom": your_bom_data,
    "routing": your_routing_data,
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
- SAP_PP_API
- ERP_BOM_routing
- Quality_System_API
- Capacity_Planning_Tool

## Escalation
The agent automatically escalates to human when:
- CapacityAvailable false after 2 attempts
- ReworkRequired >2 times
- Material staging timeout >4 hours