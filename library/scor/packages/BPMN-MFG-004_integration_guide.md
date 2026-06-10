# Integration Guide — rough_cut_capacity_agent
**Process:** Capacity Planning & Rough-Cut
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp rough_cut_capacity_agent.py ./agents/
```

## Basic Usage
```python
from agents.rough_cut_capacity_agent import RoughCutCapacityAgentAgent

agent = RoughCutCapacityAgentAgent()
result = agent.execute({
    "demand_plan": your_demand_plan_data,
    "routing_data": your_routing_data_data,
    "capacity_data": your_capacity_data_data,
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
- erp_integration
- sap_pp_connector
- finance_erp_api
- shift_pattern_analyzer

## Escalation
The agent automatically escalates to human when:
- GDPR flag triggered requiring anonymization
- No feasible option after all gateways
- Cycle time exceeds planning KPI or data quality failure