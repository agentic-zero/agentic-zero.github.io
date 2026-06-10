# Integration Guide — iot_event_management_agent
**Process:** IoT Event Management & Response
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp iot_event_management_agent.py ./agents/
```

## Basic Usage
```python
from agents.iot_event_management_agent import IotEventManagementAgentAgent

agent = IotEventManagementAgentAgent()
result = agent.execute({
    "iot_sensor_events": your_iot_sensor_events_data,
    "business_rules": your_business_rules_data,
    "threshold_definitions": your_threshold_definitions_data,
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
- IoTPlatform_MQTT_OPCUA
- AIEngine
- BusinessRuleStore
- ActionExecutor
- NotificationService

## Escalation
The agent automatically escalates to human when:
- CriticalEvent == true
- AutoResponseAvailable == false or ActionSuccessful == false after retry
- Sensor timeout > 30s
- HumanRequired == true or compliance violation detected