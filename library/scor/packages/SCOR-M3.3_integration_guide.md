# Integration Guide — eto_produce_and_test_agent
**Process:** Produce and Test (ETO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp eto_produce_and_test_agent.py ./agents/
```

## Basic Usage
```python
from agents.eto_produce_and_test_agent import EtoProduceAndTestAgentAgent

agent = EtoProduceAndTestAgentAgent()
result = agent.execute({
    "work_packages": your_work_packages_data,
    "engineering_drawings": your_engineering_drawings_data,
    "test_procedures": your_test_procedures_data,
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
- ERP_API
- PDM_API
- TestEquipment_Interface
- QA_System
- VideoValidation_Tool

## Escalation
The agent automatically escalates to human when:
- Missing test equipment: escalate to procurement with 4-hour SLA
- Customer witness unavailable: substitute video validation plus remote sign-off
- Integration or witness test failure requiring SCOR-M3.4 disposition