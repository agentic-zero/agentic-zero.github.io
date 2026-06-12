# Integration Guide â€” nist_measure_risk_analyzer
**Process:** MEASURE — AI Risk Analysis and Metrics
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp nist_measure_risk_analyzer.py ./agents/
```

## Basic Usage
```python
from agents.nist_measure_risk_analyzer import NistMeasureRiskAnalyzerAgent

agent = NistMeasureRiskAnalyzerAgent()
result = agent.execute({
    "ai_system_outputs": your_ai_system_outputs_data,
    "test_datasets": your_test_datasets_data,
    "performance_benchmarks": your_performance_benchmarks_data,
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
- json_csv_ingestion
- metric_calculation_engine
- report_generator

## Escalation
The agent automatically escalates to human when:
- automation_potential < 0.5 require human review
- incomplete inputs or metric_reliability < 0.9 produce invalid scores