# Integration Guide — iot_sensor_stream_manager
**Process:** Manage IoT and Sensor Data Streams
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp iot_sensor_stream_manager.py ./agents/
```

## Basic Usage
```python
from agents.iot_sensor_stream_manager import IotSensorStreamManagerAgent

agent = IotSensorStreamManagerAgent()
result = agent.execute({
    "sensor_readings": your_sensor_readings_data,
    "device_telemetry": your_device_telemetry_data,
    "environmental_data": your_environmental_data_data,
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
- MQTT_client
- TLS_1.3_module
- data_anonymizer
- anomaly_detection_engine
- failover_controller

## Escalation
The agent automatically escalates to human when:
- sensor_offline_exceeding_5min
- data_quality_rate_below_0.95_after_quarantine
- persistent_false_anomaly_alerts