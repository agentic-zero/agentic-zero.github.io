"""
AGENTIC ZERO - Comparator Pipeline v1.0
=========================================
Punto de entrada unico que orquesta:
  1. MultiModelComparator  -> 3 modelos en paralelo
  2. ConsensusEngine       -> ontologia certificada
  3. Integracion con Architect -> engancha en pipeline existente

Uso standalone:
  python comparator_pipeline.py BPMN-OTC-001 --sector distribution --erp "SAP ECC + HANA"

Uso desde Architect:
  from comparator_pipeline import run_comparator
  ontology = run_comparator(process_spec)

Ubicacion: F:/agentic-zero/pioneer_team/comparator/comparator_pipeline.py
"""

import json
import logging
import sys
from pathlib import Path
from datetime import datetime, timezone
import os

# Anadir path del proyecto al sys.path
ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from comparator import MultiModelComparator
from consensus_engine import ConsensusEngine

log = logging.getLogger("comparator_pipeline")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [PIPELINE] %(levelname)s %(message)s",
    datefmt="%H:%M:%S"
)

LIBRARY_PATH = Path(os.getenv("LIBRARY_PATH", "F:/agentic-zero/library"))


# ============================================================================
# FUNCION PRINCIPAL - usable desde Architect
# ============================================================================

def run_comparator(process_spec: dict, force: bool = False) -> dict:
    """
    Ejecuta el pipeline completo: comparador -> consensus -> ontologia.

    Args:
        process_spec: dict con process_id, name, framework, sector, erp, description
        force: si True, regenera aunque ya exista ontologia

    Returns:
        ontology dict con consensus_score, decision, steps mergeados, etc.
    """
    process_id = process_spec.get("process_id", "UNKNOWN")

    # -- Verificar si ya existe ontologia valida ---------------------------
    engine = ConsensusEngine()
    if not force:
        existing = engine.load_ontology(process_id)
        if existing:
            log.info(f"OK Ontologia existente cargada: {process_id} "
                     f"(score: {existing.get('consensus_score', 'N/A')})")
            return existing

    log.info(f"=== Comparator Pipeline: {process_id} ===")
    start = datetime.now(timezone.utc)

    # -- PASO 1: Comparador ------------------------------------------------
    log.info("PASO 1/2: Multi-Model Comparador...")
    comparator = MultiModelComparator()
    comparator_result = comparator.run_and_save(process_spec)

    models_ok = len(comparator_result.get("models_succeeded", []))
    if models_ok == 0:
        raise RuntimeError(f"Todos los modelos fallaron para {process_id}")

    log.info(f"  -> {models_ok} modelos completados en "
             f"{comparator_result.get('elapsed_seconds', 0)}s")

    # -- PASO 2: Consensus Engine ------------------------------------------
    log.info("PASO 2/2: Consensus Engine...")
    ontology = engine.generate(comparator_result)

    elapsed = round((datetime.now(timezone.utc) - start).total_seconds(), 2)

    # -- Resumen -----------------------------------------------------------
    decision = ontology.get("decision_label", "UNKNOWN")
    score    = ontology.get("consensus_score", 0)

    log.info(f"{'='*50}")
    log.info(f"  {process_id} - COMPLETADO en {elapsed}s")
    log.info(f"  Consensus score : {score}")
    log.info(f"  Decision        : {decision}")
    log.info(f"  Automation      : {ontology.get('overall_automation_score', 0)}")
    log.info(f"  Certified by    : {ontology.get('certified_by', [])}")
    log.info(f"{'='*50}")

    return ontology


def inject_ontology_into_package(process_id: str, ontology: dict) -> bool:
    """
    Inyecta la ontologia en el package existente del proceso.
    Llamado tras run_comparator para enriquecer el paquete de biblioteca.
    """
    package_path = LIBRARY_PATH / "scor" / "packages" / f"{process_id}_package.json"

    # Buscar tambien en bpmn y otros directorios
    if not package_path.exists():
        for subdir in ["bpmn", "frameworks", "sector_specific"]:
            alt = LIBRARY_PATH / subdir / "packages" / f"{process_id}_package.json"
            if alt.exists():
                package_path = alt
                break

    if not package_path.exists():
        log.warning(f"Package no encontrado para {process_id} - ontologia guardada independientemente")
        return False

    with open(package_path, encoding="utf-8") as f:
        package = json.load(f)

    # Anadir seccion multi_model_validation
    package["multi_model_validation"] = {
        "consensus_score":          ontology.get("consensus_score"),
        "decision":                 ontology.get("decision"),
        "decision_label":           ontology.get("decision_label"),
        "overall_automation_score": ontology.get("overall_automation_score"),
        "certified_by":             ontology.get("certified_by", []),
        "generated_at":             ontology.get("generated_at"),
        "divergence_map":           ontology.get("divergence_map", {}),
        "governance":               ontology.get("governance", {}),
        "ontology_path":            f"library/ontologies/{process_id}_ontology.json"
    }

    with open(package_path, "w", encoding="utf-8") as f:
        json.dump(package, f, indent=2, ensure_ascii=False)

    log.info(f"OK Ontologia inyectada en package: {package_path.name}")
    return True


# ============================================================================
# PATCH PARA ARCHITECT - funcion de enganche
# ============================================================================

ARCHITECT_HOOK = '''
# -- Multi-Model Comparador hook (anadir en architect.py) -----------------
# Insertar al final del metodo validate_process() o generate_variants(),
# ANTES de devolver el resultado al Builder.

def run_multi_model_validation(self, process_spec: dict) -> dict:
    """Enganche del comparador en el Architect."""
    try:
        from pioneer_team.comparator.comparator_pipeline import run_comparator, inject_ontology_into_package
        ontology = run_comparator(process_spec)
        inject_ontology_into_package(process_spec.get("process_id"), ontology)
        return ontology
    except Exception as e:
        import logging
        logging.getLogger("architect").warning(
            f"Multi-model comparador no disponible: {e} - continuando sin ontologia"
        )
        return {}
# -------------------------------------------------------------------------
'''


# ============================================================================
# CLI
# ============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Agentic Zero Comparator Pipeline - Multi-Model Ontology Generator"
    )
    parser.add_argument("process_id",  help="ID del proceso (ej. BPMN-OTC-001)")
    parser.add_argument("--name",        default="", help="Nombre descriptivo")
    parser.add_argument("--framework",   default="BPMN+SCOR")
    parser.add_argument("--sector",      default="distribution")
    parser.add_argument("--erp",         default="SAP ECC + HANA")
    parser.add_argument("--description", default="")
    parser.add_argument("--force",       action="store_true",
                        help="Regenerar aunque ya exista ontologia")
    parser.add_argument("--inject",      action="store_true",
                        help="Inyectar ontologia en el package de biblioteca")
    parser.add_argument("--show-hook",   action="store_true",
                        help="Mostrar codigo de enganche para architect.py")
    args = parser.parse_args()

    if args.show_hook:
        print(ARCHITECT_HOOK)
        sys.exit(0)

    spec = {
        "process_id":  args.process_id,
        "name":        args.name or args.process_id,
        "framework":   args.framework,
        "sector":      args.sector,
        "erp":         args.erp,
        "description": args.description,
    }

    ontology = run_comparator(spec, force=args.force)

    if args.inject:
        inject_ontology_into_package(args.process_id, ontology)

    # Output resumen
    print(f"\n{'='*60}")
    print(f"  Process         : {ontology['process_id']}")
    print(f"  Consensus score : {ontology['consensus_score']}")
    print(f"  Decision        : {ontology['decision_label']}")
    print(f"  Automation score: {ontology['overall_automation_score']}")
    print(f"  Certified by    : {', '.join(ontology.get('certified_by', []))}")
    print(f"  Risk flags      : {len(ontology.get('risk_flags', []))}")
    print(f"  Steps merged    : {len(ontology.get('steps', []))}")
    print(f"  Weakest field   : {ontology.get('divergence_map', {}).get('weakest_field', 'N/A')}")
    print(f"{'='*60}")

    if ontology.get("decision") == "DIVERGENCE_HIGH":
        print("\nWARN  DIVERGENCE_HIGH - revision manual recomendada antes de certificar")
    elif ontology.get("decision") == "WEIGHTED_MERGE":
        print("\nWARN  WEIGHTED_MERGE - ontologia generada, revisar divergence_map")
    else:
        print("\nOK  AUTO_MERGE - ontologia certificada lista para Guardian")
