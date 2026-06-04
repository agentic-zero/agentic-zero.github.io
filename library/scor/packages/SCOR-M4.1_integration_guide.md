# Integration Guide — product_test_and_inspect_agent
**Process:** Test and Inspect Products
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp product_test_and_inspect_agent.py ./agents/
```

## Basic Usage
```python
from agents.product_test_and_inspect_agent import ProductTestAndInspectAgentAgent

agent = ProductTestAndInspectAgentAgent()
result = agent.execute({
    "confirmed_production": your_confirmed_production_data,
    "quality_standards": your_quality_standards_data,
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
- testing_system_api
- quality_standards_database
- report_generation_tool

## Escalation
The agent automatically escalates to human when:
- defect rate exceeds threshold
- test coverage is below threshold
- quality report generation fails