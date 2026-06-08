# Integration Guide — build_loads_optimizer
**Process:** Build Loads (MTO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp build_loads_optimizer.py ./agents/
```

## Basic Usage
```python
from agents.build_loads_optimizer import BuildLoadsOptimizerAgent

agent = BuildLoadsOptimizerAgent()
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
- PIM_product_api
- carrier_master_api
- compliance_db
- route_planning_system

## Escalation
The agent automatically escalates to human when:
- Missing product dimensions or GDPR data
- No carrier meets constraints (trigger SCOR-D2.6)
- Optimization solver timeout