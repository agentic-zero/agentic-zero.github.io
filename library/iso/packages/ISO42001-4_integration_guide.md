# Integration Guide â€” iso42001_4_context_agent
**Process:** AI Context — Organization and Interested Parties
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp iso42001_4_context_agent.py ./agents/
```

## Basic Usage
```python
from agents.iso42001_4_context_agent import Iso420014ContextAgentAgent

agent = Iso420014ContextAgentAgent()
result = agent.execute({
    "ai_use_case_inventory": your_ai_use_case_inventory_data,
    "regulatory_requirements": your_regulatory_requirements_data,
    "stakeholder_ai_expectations": your_stakeholder_ai_expectations_data,
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
- AIUseCaseInventory_API
- RegulatoryRequirement_DB
- StakeholderExpectation_Parser
- ComplianceFlag_Evaluator

## Escalation
The agent automatically escalates to human when:
- automation_potential < 0.5 requires manual stakeholder validation
- missing inputs or unmapped regulatory requirements