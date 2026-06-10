# Integration Guide — npi_stage_gate_orchestrator
**Process:** New Product Introduction (NPI)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp npi_stage_gate_orchestrator.py ./agents/
```

## Basic Usage
```python
from agents.npi_stage_gate_orchestrator import NpiStageGateOrchestratorAgent

agent = NpiStageGateOrchestratorAgent()
result = agent.execute({
    "product_concept": your_product_concept_data,
    "market_requirements": your_market_requirements_data,
    "regulatory_guidelines": your_regulatory_guidelines_data,
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
- SAP_PLM_API
- Windchill_integration
- regulatory_database_query
- event_listener

## Escalation
The agent automatically escalates to human when:
- Product_Cancelled after 3 consecutive Stage_Gate rejections
- Regulatory rejection in pharma/food sector
- Missing ERP log or GDPR/IP violation detected