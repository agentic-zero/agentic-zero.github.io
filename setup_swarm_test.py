import json
import os

os.makedirs("events_test1", exist_ok=True)
os.makedirs("events_test2", exist_ok=True)
os.makedirs("events_test3", exist_ok=True)
os.makedirs("events_test4", exist_ok=True)

# Caso 1: sin conflicto (dentro de tolerancia)
events1 = [
    {"event_id":"E1","timestamp":"2026-06-25T10:00:00Z","event_type":"demand_planning_updated","source":"demand_planning_agent","payload":{"organism":"Demand Planning Organism","scenario_id":"SC-001","confidence_score":0.92,"risk_score":0.30}},
    {"event_id":"E2","timestamp":"2026-06-25T10:00:05Z","event_type":"supply_planning_updated","source":"supply_planning_agent","payload":{"organism":"Supply Planning Organism","scenario_id":"SC-001","confidence_score":0.88,"risk_score":0.45}},
]
with open("events_test1/swarm_events.jsonl","w") as f:
    for e in events1: f.write(json.dumps(e)+"\n")

# Caso 2: conflicto por baja confianza -> ESCALATED
events2 = [
    {"event_id":"E3","timestamp":"2026-06-25T10:00:00Z","event_type":"demand_planning_updated","source":"demand_planning_agent","payload":{"organism":"Demand Planning Organism","scenario_id":"SC-002","confidence_score":0.91,"risk_score":0.20}},
    {"event_id":"E4","timestamp":"2026-06-25T10:00:05Z","event_type":"supply_planning_updated","source":"supply_planning_agent","payload":{"organism":"Supply Planning Organism","scenario_id":"SC-002","confidence_score":0.55,"risk_score":0.85}},
]
with open("events_test2/swarm_events.jsonl","w") as f:
    for e in events2: f.write(json.dumps(e)+"\n")

# Caso 3: impacto financiero critico -> ESCALATED siempre
events3 = [
    {"event_id":"E5","timestamp":"2026-06-25T10:00:00Z","event_type":"demand_planning_updated","source":"demand_planning_agent","payload":{"organism":"Demand Planning Organism","scenario_id":"SC-003","confidence_score":0.95,"risk_score":0.40,"financial_impact":0.80}},
    {"event_id":"E6","timestamp":"2026-06-25T10:00:05Z","event_type":"supply_planning_updated","source":"supply_planning_agent","payload":{"organism":"Supply Planning Organism","scenario_id":"SC-003","confidence_score":0.93,"risk_score":0.55,"financial_impact":0.20}},
]
with open("events_test3/swarm_events.jsonl","w") as f:
    for e in events3: f.write(json.dumps(e)+"\n")

# Caso 4: desacuerdo moderado, ambos confiados -> RESOLVED_AUTO
events4 = [
    {"event_id":"E7","timestamp":"2026-06-25T10:00:00Z","event_type":"demand_planning_updated","source":"demand_planning_agent","payload":{"organism":"Demand Planning Organism","scenario_id":"SC-004","confidence_score":0.93,"risk_score":0.20}},
    {"event_id":"E8","timestamp":"2026-06-25T10:00:05Z","event_type":"supply_planning_updated","source":"supply_planning_agent","payload":{"organism":"Supply Planning Organism","scenario_id":"SC-004","confidence_score":0.90,"risk_score":0.55}},
]
with open("events_test4/swarm_events.jsonl","w") as f:
    for e in events4: f.write(json.dumps(e)+"\n")

print("4 escenarios de prueba creados")
