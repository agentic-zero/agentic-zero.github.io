# Integration Guide â€” eu_ai_act_art14_human_oversight_agent
**Process:** Human Oversight
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp eu_ai_act_art14_human_oversight_agent.py ./agents/
```

## Basic Usage
```python
from agents.eu_ai_act_art14_human_oversight_agent import EuAiActArt14HumanOversightAgentAgent

agent = EuAiActArt14HumanOversightAgentAgent()
result = agent.execute({
    "ai_system_outputs": your_ai_system_outputs_data,
    "oversight_protocols": your_oversight_protocols_data,
    "human_reviewer_assignments": your_human_reviewer_assignments_data,
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
- ai_output_inference_api
- hr_availability_system
- override_execution_api
- audit_logging_db

## Escalation
The agent automatically escalates to human when:
- AI_System_Output.confidence < Oversight_Protocol.threshold
- GDPR Art.22 automated decision detected
- no Human_Reviewer available within SLA