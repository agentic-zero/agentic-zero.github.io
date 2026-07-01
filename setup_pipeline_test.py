import json, os, sys

CLIENT = "clients/distribuciones_norte/sop/essential_package"
TEST_DIR = "swarm_pipeline_test"

os.makedirs(f"{TEST_DIR}/00_enterprise_intent/level_2_siops", exist_ok=True)

coord = json.load(open(f"{CLIENT}/00_enterprise_intent/swarm_coordination_siop.json", encoding="utf-8"))

for i, org in enumerate(coord["organisms"]):
    with open(f"{TEST_DIR}/00_enterprise_intent/level_2_siops/{i:02d}_{org['agent_type']}.json", "w", encoding="utf-8") as f:
        json.dump(org, f, indent=2)

with open(f"{TEST_DIR}/00_enterprise_intent/swarm_coordination_siop.json", "w", encoding="utf-8") as f:
    json.dump(coord, f, indent=2)

with open(f"{TEST_DIR}/00_enterprise_intent/siop_decomposition.json", "w", encoding="utf-8") as f:
    json.dump({"parent_process": coord.get("parent_process", "Sales and Operations Planning S&OP")}, f, indent=2)

print(f"{len(coord['organisms'])} Level2SIOPs generados en {TEST_DIR}/ (carpeta de prueba, NO toca distribuciones_norte)")
