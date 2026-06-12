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
- runtime_log_analyzer
- incident_reporting_api
- national_authority_notification_service
- performance_metric_calculator

## Escalation
The agent automatically escalates to human when:
- national_authority unreachable after 5 retry days
- corrective_action_effectiveness below 0.8 after two attempts
- monitoring_coverage remains below 0.95 after source expansion