# Integration Guide — supply_chain_transportation_policy_agent
**Process:** Determine Supply Chain Transportation Policy
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp supply_chain_transportation_policy_agent.py ./agents/
```

## Basic Usage
```python
from agents.supply_chain_transportation_policy_agent import SupplyChainTransportationPolicyAgentAgent

agent = SupplyChainTransportationPolicyAgentAgent()
result = agent.execute({
    "demand_plan": your_demand_plan_data,
    "supply_chain_requirements": your_supply_chain_requirements_data,
    "transportation_data": your_transportation_data_data,
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
- transportation_management_system_api
- data_analytics_library
- compliance_validation_module

## Escalation
The agent automatically escalates to human when:
- transportation cost exceeds 10% of budget
- on-time delivery rate falls below 90%
- carrier selection does not meet supply chain requirements