# Integration Guide — load_plan_optimizer
**Process:** Build Loads (MTO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp load_plan_optimizer.py ./agents/
```

## Basic Usage
```python
from agents.load_plan_optimizer import LoadPlanOptimizerAgent

agent = LoadPlanOptimizerAgent()
result = agent.execute({
    "consolidated_orders": your_consolidated_orders_data,
    "product_dimensions_and_weights": your_product_dimensions_and_weights_data,
    "carrier_constraints": your_carrier_constraints_data,
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
- optimization_solver
- carrier_api
- compliance_db
- product_master

## Escalation
The agent automatically escalates to human when:
- optimization rate <70% after 3 iterations
- carrier-dg constraint conflict