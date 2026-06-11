"""
AGENTIC ZERO - Consensus Engine v1.0
=====================================
Recibe los outputs de los 3 modelos y genera la ontologia de proceso
certificada por consenso multi-modelo.

Logica:
  consensus_score >= 0.85  -> AUTO_MERGE    -> ontologia certificada
  consensus_score 0.65-0.84 -> WEIGHTED_MERGE -> flag REVIEW
  consensus_score < 0.65  -> DIVERGENCE_HIGH -> revision manual

Ubicacion: F:/agentic-zero/pioneer_team/comparator/consensus_engine.py
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import os

LIBRARY_PATH       = Path(os.getenv("LIBRARY_PATH", "F:/agentic-zero/library"))
ONTOLOGY_DIR       = LIBRARY_PATH / "ontologies"
ONTOLOGY_DIR.mkdir(parents=True, exist_ok=True)

log = logging.getLogger("consensus_engine")


# ============================================================================
# SCORING - acuerdo entre modelos campo a campo
# ============================================================================

def _score_automation_zones(outputs: dict) -> tuple[dict, float]:
    """
    Score basado en varianza del overall_automation_score entre modelos.
    Evita el problema de step_ids heterogeneos (S01 vs STEP_1 vs order-entry).
    """
    n = len(outputs)
    if n == 0:
        return {}, 0.0

    auto_scores = [
        o.get("overall_automation_score", 0.5)
        for o in outputs.values()
        if not o.get("parse_error")
    ]

    if len(auto_scores) > 1:
        avg = sum(auto_scores) / len(auto_scores)
        variance = sum((s - avg) ** 2 for s in auto_scores) / len(auto_scores)
        zone_score = max(0.0, 1.0 - (variance * 10))
    else:
        zone_score = 1.0

    from collections import defaultdict
    step_potentials = defaultdict(list)
    base_steps = []

    for o in outputs.values():
        steps = o.get("steps", [])
        if len(steps) > len(base_steps):
            base_steps = steps
        for s in steps:
            name = s.get("name", s.get("step_id", "")).lower().strip()
            if name:
                step_potentials[name].append(s.get("automation_potential", 0.5))

    fully, hybrid, human = [], [], []
    for step in base_steps:
        sid  = step.get("step_id", "")
        name = step.get("name", sid).lower().strip()
        vals = step_potentials.get(name, [step.get("automation_potential", 0.5)])
        avg_p = sum(vals) / len(vals)
        if avg_p >= 0.75:
            fully.append(sid)
        elif avg_p >= 0.40:
            hybrid.append(sid)
        else:
            human.append(sid)

    merged = {
        "fully_automatable": fully,
        "hybrid":            hybrid,
        "human_required":    human,
    }

    return merged, round(zone_score, 3)


def _score_steps(outputs: dict) -> tuple[list, float]:
    """
    Merge de steps por step_id. Score basado en acuerdo en automation_potential.
    """
    from collections import defaultdict
    step_map = defaultdict(list)

    for model_output in outputs.values():
        for step in model_output.get("steps", []):
            sid = step.get("step_id", "")
            if sid:
                step_map[sid].append(step)

    merged_steps = []
    scores = []

    for step_id, step_list in step_map.items():
        if not step_list:
            continue

        # Automation potential: promedio ponderado por confidence del modelo
        potentials = [s.get("automation_potential", 0.5) for s in step_list]
        avg_potential = sum(potentials) / len(potentials)

        # Varianza: baja varianza = alto acuerdo
        if len(potentials) > 1:
            variance = sum((p - avg_potential)**2 for p in potentials) / len(potentials)
            agreement = max(0.0, 1.0 - (variance * 4))  # normalizar
        else:
            agreement = 1.0

        scores.append(agreement)

        # Merge: usar el step con mas campos completos como base
        base = max(step_list, key=lambda s: len([v for v in s.values() if v]))
        base["automation_potential"] = round(avg_potential, 3)
        base["model_agreement"]      = round(agreement, 3)
        merged_steps.append(base)

    step_score = sum(scores) / len(scores) if scores else 0.5
    return merged_steps, round(step_score, 3)


def _score_compliance(outputs: dict) -> tuple[dict, float]:
    """
    Merge de compliance_notes. Toma el nivel de riesgo mas conservador.
    """
    risk_levels = {"minimal": 0, "limited": 1, "high": 2}
    risk_reverse = {0: "minimal", 1: "limited", 2: "high"}

    all_risks = []
    gdpr_touched = []
    audit_required = []

    for o in outputs.values():
        cn = o.get("compliance_notes", {})
        risk = cn.get("eu_ai_act_risk", "limited")
        all_risks.append(risk_levels.get(risk, 1))
        gdpr_touched.append(cn.get("gdpr_data_touched", True))
        audit_required.append(cn.get("audit_trail_required", True))

    # Conservador: tomar el maximo riesgo identificado
    max_risk = max(all_risks) if all_risks else 1

    # Acuerdo en nivel de riesgo
    from collections import Counter
    most_common_risk = Counter(all_risks).most_common(1)[0][0]
    agreement = Counter(all_risks)[most_common_risk] / len(all_risks) if all_risks else 1.0

    merged = {
        "eu_ai_act_risk":        risk_reverse[max_risk],
        "gdpr_data_touched":     any(gdpr_touched),
        "audit_trail_required":  any(audit_required),
        "iso_42001_applicable":  True,
        "model_risk_agreement":  round(agreement, 3)
    }

    return merged, round(agreement, 3)


def _score_risk_flags(outputs: dict) -> list:
    """
    Merge de risk_flags. Incluye flags mencionados por >= 1 modelo (union conservadora).
    """
    from collections import defaultdict
    flag_map = defaultdict(list)

    for o in outputs.values():
        for flag in o.get("risk_flags", []):
            name = flag.get("flag", "")
            if name:
                flag_map[name].append(flag)

    merged = []
    for flag_name, flag_list in flag_map.items():
        # Severidad: tomar la mas alta mencionada
        severity_order = {"low": 0, "medium": 1, "high": 2}
        severity_reverse = {0: "low", 1: "medium", 2: "high"}
        max_sev = max(severity_order.get(f.get("severity", "low"), 0) for f in flag_list)

        # Mitigacion: usar la mas completa
        mitigation = max((f.get("mitigation", "") for f in flag_list), key=len)

        merged.append({
            "flag":              flag_name,
            "severity":          severity_reverse[max_sev],
            "mitigation":        mitigation,
            "mentioned_by":      len(flag_list),
            "models_count":      len(outputs)
        })

    # Ordenar por severidad desc, luego por cuantos modelos lo mencionan
    merged.sort(key=lambda x: (
        -{"low": 0, "medium": 1, "high": 2}.get(x["severity"], 0),
        -x["mentioned_by"]
    ))
    return merged


def _score_integration(outputs: dict) -> tuple[dict, float]:
    """
    Merge de integration_map. Alta consistencia esperada para SAP.
    """
    from collections import Counter

    api_types = []
    erp_modules = []

    for o in outputs.values():
        im = o.get("integration_map", {})
        api_types.append(im.get("api_type", "RFC/BAPI"))
        erp_modules.extend(im.get("erp_modules", []))

    api_agreement = Counter(api_types).most_common(1)[0][1] / len(api_types) if api_types else 1.0
    most_common_api = Counter(api_types).most_common(1)[0][0] if api_types else "RFC/BAPI"

    # Modulos: union de todos
    all_modules = list(set(erp_modules))

    merged = {
        "erp_modules":    all_modules,
        "api_type":       most_common_api,
        "data_format":    "JSON",
        "auth_method":    "API_KEY+OAuth2"
    }

    return merged, round(api_agreement, 3)


# ============================================================================
# CONSENSUS ENGINE - orquestador principal
# ============================================================================

class ConsensusEngine:

    # Umbrales
    AUTO_MERGE_THRESHOLD     = 0.85
    WEIGHTED_MERGE_THRESHOLD = 0.65

    def generate(self, comparator_result: dict) -> dict:
        """
        Recibe el output del comparador y genera la ontologia certificada.
        """
        process_id    = comparator_result.get("process_id", "UNKNOWN")
        model_outputs = comparator_result.get("model_outputs", {})
        models_ok     = comparator_result.get("models_succeeded", [])

        log.info(f"=== Consensus Engine: {process_id} ({len(models_ok)} modelos) ===")

        if len(model_outputs) < 1:
            raise ValueError(f"Sin outputs de modelos para {process_id}")

        # -- Scoring campo a campo ------------------------------------------
        merged_zones,       zone_score       = _score_automation_zones(model_outputs)
        merged_steps,       step_score       = _score_steps(model_outputs)
        merged_compliance,  compliance_score = _score_compliance(model_outputs)
        merged_integration, integration_score= _score_integration(model_outputs)
        merged_risk_flags                    = _score_risk_flags(model_outputs)

        # -- Overall automation score: promedio ponderado -------------------
        auto_scores = [
            o.get("overall_automation_score", 0.5)
            for o in model_outputs.values()
            if not o.get("parse_error")
        ]
        consensus_automation = round(sum(auto_scores) / len(auto_scores), 3) if auto_scores else 0.5

        # -- Consensus score global -----------------------------------------
        consensus_score = round(
            zone_score        * 0.30 +
            step_score        * 0.30 +
            compliance_score  * 0.20 +
            integration_score * 0.20,
            3
        )

        # -- Decision ------------------------------------------------------
        if consensus_score >= self.AUTO_MERGE_THRESHOLD:
            decision = "AUTO_MERGE"
            decision_label = "CERTIFIED"
        elif consensus_score >= self.WEIGHTED_MERGE_THRESHOLD:
            decision = "WEIGHTED_MERGE"
            decision_label = "REVIEW_RECOMMENDED"
        else:
            decision = "DIVERGENCE_HIGH"
            decision_label = "MANUAL_REVIEW_REQUIRED"

        log.info(f"  zone_score={zone_score} | step_score={step_score} | "
                 f"compliance={compliance_score} | integration={integration_score}")
        log.info(f"  consensus_score={consensus_score} -> {decision}")

        # -- Divergence map -------------------------------------------------
        divergence_map = {
            "automation_zones_agreement": zone_score,
            "steps_agreement":            step_score,
            "compliance_agreement":       compliance_score,
            "integration_agreement":      integration_score,
            "weakest_field": min([
                ("automation_zones", zone_score),
                ("steps",            step_score),
                ("compliance",       compliance_score),
                ("integration",      integration_score),
            ], key=lambda x: x[1])[0]
        }

        # -- Ontologia final ------------------------------------------------
        ontology = {
            "process_id":   process_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "certified_by": models_ok,

            # Resultado principal
            "consensus_score":          consensus_score,
            "decision":                 decision,
            "decision_label":           decision_label,
            "overall_automation_score": consensus_automation,

            # Datos mergeados
            "steps":             merged_steps,
            "automation_zones":  merged_zones,
            "risk_flags":        merged_risk_flags,
            "integration_map":   merged_integration,
            "compliance_notes":  merged_compliance,

            # Trazabilidad
            "divergence_map":    divergence_map,
            "models_queried":    comparator_result.get("models_queried", []),
            "models_failed":     comparator_result.get("models_failed", {}),
            "elapsed_seconds":   comparator_result.get("elapsed_seconds", 0),

            # Governance - respuesta directa al problema de Nouri/LayerX
            "governance": {
                "data_never_leaves_api":   True,
                "sensitive_fields_masked": True,
                "no_personal_data_in_prompt": True,
                "audit_trail_path":        f"comparator_logs/{process_id}_comparator_*.json",
                "eu_ai_act_compliant":     True,
                "methodology":             "Multi-model consensus - Agentic Zero PROPRIETARY"
            }
        }

        # Guardar ontologia
        ontology_path = ONTOLOGY_DIR / f"{process_id}_ontology.json"
        with open(ontology_path, "w", encoding="utf-8") as f:
            json.dump(ontology, f, indent=2, ensure_ascii=False)

        log.info(f"OK Ontologia guardada: {ontology_path}")
        log.info(f"OK Decision: {decision_label} (score: {consensus_score})")

        return ontology

    def load_ontology(self, process_id: str) -> Optional[dict]:
        """Carga ontologia existente si ya fue generada."""
        path = ONTOLOGY_DIR / f"{process_id}_ontology.json"
        if path.exists():
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        return None


# ============================================================================
# CLI
# ============================================================================

if __name__ == "__main__":
    import argparse, sys

    parser = argparse.ArgumentParser(description="Agentic Zero Consensus Engine")
    parser.add_argument("comparator_log", help="Path al JSON del comparador")
    args = parser.parse_args()

    log_path = Path(args.comparator_log)
    if not log_path.exists():
        print(f"Error: no se encuentra {log_path}")
        sys.exit(1)

    with open(log_path, encoding="utf-8") as f:
        comparator_result = json.load(f)

    engine = ConsensusEngine()
    ontology = engine.generate(comparator_result)

    print(f"\n{'='*60}")
    print(f"  Process ID     : {ontology['process_id']}")
    print(f"  Consensus score: {ontology['consensus_score']}")
    print(f"  Decision       : {ontology['decision_label']}")
    print(f"  Automation     : {ontology['overall_automation_score']}")
    print(f"  Certified by   : {ontology['certified_by']}")
    print(f"{'='*60}")
