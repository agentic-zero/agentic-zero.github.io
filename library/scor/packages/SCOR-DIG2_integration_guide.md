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
- stream_ingestion_api
- anomaly_detection_engine
- encryption_module
- compliance_validator

## Escalation
The agent automatically escalates to human when:
- data_gap exceeds 5 minutes or uptime below 0.99
- pharma location_data absent
- unresolvable compliance or encryption failure