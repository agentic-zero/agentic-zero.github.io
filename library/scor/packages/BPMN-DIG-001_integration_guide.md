# Integration Guide — demand_sensing_forecast_agent
**Process:** AI-Powered Demand Sensing & Forecasting
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp demand_sensing_forecast_agent.py ./agents/
```

## Basic Usage
```python
from agents.demand_sensing_forecast_agent import DemandSensingForecastAgentAgent

agent = DemandSensingForecastAgentAgent()
result = agent.execute({
    "pos_data": your_pos_data_data,
    "orders": your_orders_data,
    "market_signals": your_market_signals_data,
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
- data_ingestion_api
- ml_inference_engine
- consensus_workflow_notifier
- planning_system_publisher
- audit_logger

## Escalation
The agent automatically escalates to human when:
- ModelConfidence < 0.7
- DataQualityOK false after 3 retries
- ConsensusReview timeout > 72 hours
- human review required under GDPR Art.22