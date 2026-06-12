# Integration Guide â€” eu_ai_act_art10_data_governor
**Process:** Data Governance for High-Risk AI
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp eu_ai_act_art10_data_governor.py ./agents/
```

## Basic Usage
```python
from agents.eu_ai_act_art10_data_governor import EuAiActArt10DataGovernorAgent

agent = EuAiActArt10DataGovernorAgent()
result = agent.execute({
    "training_datasets": your_training_datasets_data,
    "validation_datasets": your_validation_datasets_data,
    "test_datasets": your_test_datasets_data,
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
- dataset_ingestion_scanner
- bias_metric_calculator
- data_lineage_tracker
- quality_report_generator

## Escalation
The agent automatically escalates to human when:
- missing data_provenance fields
- bias_metric > 0.1 after mitigation
- representativeness_score < 0.85
- classified defense data exception invoked