# Integration Guide â€” ppap_automation_agent
**Process:** Production Part Approval Process (PPAP)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp ppap_automation_agent.py ./agents/
```

## Basic Usage
```python
from agents.ppap_automation_agent import PpapAutomationAgentAgent

agent = PpapAutomationAgentAgent()
result = agent.execute({
    "engineering_drawings": your_engineering_drawings_data,
    "material_certifications": your_material_certifications_data,
    "dimensional_results": your_dimensional_results_data,
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
- pdf_step_parser
- cpk_ppk_calculator
- pdm_connector
- digital_signature_service
- customer_portal_api

## Escalation
The agent automatically escalates to human when:
- first-time approval failure with missing MaterialCertification or Cpk<1.33
- approval_cycle_time>30 days
- customer-specific vs AIAG requirement conflict