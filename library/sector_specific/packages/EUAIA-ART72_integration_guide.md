# Integration Guide â€” post_market_monitoring_agent
**Process:** Post-Market Monitoring
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp post_market_monitoring_agent.py ./agents/
```

## Basic Usage
```python
from agents.post_market_monitoring_agent import PostMarketMonitoringAgentAgent

agent = PostMarketMonitoringAgentAgent()
result = agent.execute({
    "deployment_performance_data": your_deployment_performance_data_data,
    "user_feedback": your_user_feedback_data,
    "incident_reports": your_incident_reports_data,
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
- runtime_log_ingestion_api
- incident_database
- national_authority_notification_service
- user_feedback_api
- metric_computation_engine

## Escalation
The agent automatically escalates to human when:
- corrective_action_effectiveness < 0.8 escalate to EUAIA-ART9
- reporting_timeliness breach or missed serious incident notify human operator
- defense sector route via SCOR-DIG10 instead of direct authority