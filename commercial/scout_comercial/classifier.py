"""
AGENTIC ZERO -- Scout Comercial v1.0
classifier.py -- Clasificador AL1-AL4

Logica de clasificacion basada en los parametros del formulario audit.html.
Replica exactamente la logica del frontend para consistencia.

AL1 -- Standard         ERP estandar + volumen < 500/dia
AL2 -- High Volume      ERP estandar + volumen >= 500/dia
AL3 -- Complex          ERP tailored/custom/none o multi-sistema
AL4 -- Multi-Agent      2+ procesos complejos interconectados

Ubicacion: F:/agentic-zero/commercial/scout_comercial/classifier.py
"""

from dataclasses import dataclass
from typing import Optional


# ERPs que disparan AL3 por complejidad de integracion
COMPLEX_ERPS = ["tailored", "custom", "none", "legacy", "bespoke", "proprietary"]

# ERP conocidos y su nivel de complejidad de integracion (1=simple, 3=complejo)
ERP_COMPLEXITY = {
    "sap":            1,  # RFC/BAPI bien documentado
    "sap ecc":        1,
    "sap hana":       1,
    "sap s/4hana":    1,
    "oracle":         2,
    "ms dynamics":    1,
    "dynamics 365":   1,
    "business central": 1,
    "infor":          2,
    "epicor":         2,
    "netsuite":       1,
    "odoo":           1,
    "tailored":       3,
    "custom":         3,
    "none":           3,
}

# Procesos que por naturaleza requieren multi-agente (AL4)
MULTI_AGENT_TRIGGERS = [  # Solo procesos que REQUIEREN swarm por definicion
    "BPMN-OTC-001",  # OTC completo
    "BPMN-PTP-001",  # P2P completo
    "BPMN-IBP-001",  # IBP
    "SCOR-P1",       # Planning cluster
]

# Paquetes de procesos relacionados (para detectar AL4)
PROCESS_CLUSTERS = {
    "order_to_cash":    ["BPMN-OTC-001", "SCOR-D1", "SCOR-S1", "BPMN-FIN-001"],
    "procure_to_pay":   ["BPMN-PTP-001", "SCOR-S1", "SCOR-S2", "BPMN-FIN-001"],
    "planning":         ["SCOR-P1", "BPMN-IBP-001", "BPMN-MRP-001"],
    "manufacturing":    ["SCOR-M1", "SCOR-M2", "SCOR-M3", "BPMN-MFG-001"],
}


@dataclass
class ClassificationResult:
    autonomy_level: str          # AL1 / AL2 / AL3 / AL4
    label: str                   # etiqueta legible
    deploy_time: str             # tiempo estimado de deploy
    recommended_tier: str        # Essential / Standard / Enterprise
    setup_fee: float             # EUR
    monthly_fee: float           # EUR
    annual_fee: float            # EUR
    processes_detected: list     # procesos de biblioteca detectados
    cluster_detected: Optional[str]  # cluster de procesos si aplica
    rationale: str               # por que esta clasificacion
    auto_proposal: bool          # True si puede generar propuesta automatica


def classify(
    erp: str,
    volume: int,
    process_mapping: str,
    sector: str = "",
    team_size: int = 0,
) -> ClassificationResult:
    """
    Clasifica un lead en AL1-AL4 basandose en los parametros del audit.

    Args:
        erp:             ERP declarado por el cliente
        volume:          ordenes/transacciones por dia
        process_mapping: campo process_mapping de Formspree (L1:L2[refs] || ...)
        sector:          sector del cliente
        team_size:       numero de personas en el equipo operacional
    """
    erp_lower = erp.lower().strip()

    # Extraer procesos de biblioteca del process_mapping
    processes = _extract_processes(process_mapping)

    # Detectar cluster de procesos
    cluster = _detect_cluster(processes)

    # Regla 1: ERP complejo -> AL3 minimo
    is_complex_erp = any(c in erp_lower for c in COMPLEX_ERPS)

    # Regla 2: Volumen alto -> AL2 minimo
    is_high_volume = volume >= 500

    # Regla 3: Multi-proceso interconectado -> AL4
    is_multi_agent = (
        len(processes) >= 3
        or cluster is not None
        or (len(processes) >= 2 and any(p in processes for p in MULTI_AGENT_TRIGGERS))
    )

    # Clasificacion
    if is_multi_agent and (is_complex_erp or is_high_volume):
        al = "AL4"
    elif is_multi_agent:
        al = "AL4"
    elif is_complex_erp:
        al = "AL3"
    elif is_high_volume:
        al = "AL2"
    else:
        al = "AL1"

    return _build_result(al, processes, cluster, erp, volume, sector)


def _extract_processes(process_mapping: str) -> list:
    """
    Extrae los process_ids de biblioteca del campo process_mapping.
    Formato: "categoria: subcat [PROC-001,PROC-002] | subcat2 [PROC-003] || categoria2: ..."
    """
    if not process_mapping or process_mapping == "Not specified":
        return []

    processes = []
    import re
    # Buscar referencias entre corchetes: [BPMN-OTC-001,SCOR-D1.1]
    refs = re.findall(r'\[([^\]]+)\]', process_mapping)
    for ref_group in refs:
        for ref in ref_group.split(','):
            ref = ref.strip()
            if ref and (ref.startswith('BPMN') or ref.startswith('SCOR') or
                       ref.startswith('ISO') or ref.startswith('NIST')):
                if ref not in processes:
                    processes.append(ref)
    return processes


def _detect_cluster(processes: list) -> Optional[str]:
    """Detecta si los procesos pertenecen a un cluster conocido."""
    for cluster_name, cluster_procs in PROCESS_CLUSTERS.items():
        matches = sum(1 for p in processes if any(p.startswith(cp) for cp in cluster_procs))
        if matches >= 2:
            return cluster_name
    return None


def _build_result(
    al: str,
    processes: list,
    cluster: Optional[str],
    erp: str,
    volume: int,
    sector: str
) -> ClassificationResult:
    """Construye el resultado completo de clasificacion."""

    configs = {
        "AL1": {
            "label":          "AL1 -- Standard - Deploy 24h",
            "deploy_time":    "24 horas",
            "tier":           "Essential",
            "setup_fee":      490.0,
            "monthly_fee":    490.0,
            "annual_fee":     4900.0,
            "auto_proposal":  True,
            "rationale":      f"ERP estandar ({erp}) con volumen manejable ({volume}/dia). "
                              f"Perfil ideal para Essential con deploy en 24h."
        },
        "AL2": {
            "label":          "AL2 -- High Volume - Deploy 48h",
            "deploy_time":    "48 horas",
            "tier":           "Standard",
            "setup_fee":      990.0,
            "monthly_fee":    990.0,
            "annual_fee":     9900.0,
            "auto_proposal":  True,
            "rationale":      f"Volumen alto ({volume}/dia) requiere agente con mayor capacidad "
                              f"de procesamiento. Standard recomendado."
        },
        "AL3": {
            "label":          "AL3 -- Complex Integration",
            "deploy_time":    "5-7 dias habiles",
            "tier":           "Standard o Enterprise segun alcance",
            "setup_fee":      1990.0,
            "monthly_fee":    990.0,
            "annual_fee":     9900.0,
            "auto_proposal":  False,
            "rationale":      f"ERP no estandar o integracion compleja ({erp}). "
                              f"Requiere evaluacion tecnica antes de propuesta."
        },
        "AL4": {
            "label":          "AL4 -- Multi-Agent Swarm",
            "deploy_time":    "10-15 dias habiles",
            "tier":           "Enterprise",
            "setup_fee":      4900.0,
            "monthly_fee":    1800.0,
            "annual_fee":     19800.0,
            "auto_proposal":  False,
            "rationale":      f"Multiples procesos interconectados detectados "
                              f"({len(processes)} procesos, cluster: {cluster}). "
                              f"Requiere arquitectura Swarm y AUDIT presencial."
        },
    }

    cfg = configs[al]
    return ClassificationResult(
        autonomy_level=al,
        label=cfg["label"],
        deploy_time=cfg["deploy_time"],
        recommended_tier=cfg["tier"],
        setup_fee=cfg["setup_fee"],
        monthly_fee=cfg["monthly_fee"],
        annual_fee=cfg["annual_fee"],
        processes_detected=processes,
        cluster_detected=cluster,
        rationale=cfg["rationale"],
        auto_proposal=cfg["auto_proposal"],
    )


# CLI para testing
if __name__ == "__main__":
    import argparse, json

    parser = argparse.ArgumentParser(description="Scout Comercial -- Clasificador AL1-AL4")
    parser.add_argument("--erp",     default="SAP ECC", help="ERP del cliente")
    parser.add_argument("--volume",  type=int, default=50, help="Ordenes/dia")
    parser.add_argument("--mapping", default="", help="process_mapping de Formspree")
    parser.add_argument("--sector",  default="distribution")
    args = parser.parse_args()

    result = classify(args.erp, args.volume, args.mapping, args.sector)

    print(f"\n{'='*50}")
    print(f"  Clasificacion  : {result.autonomy_level}")
    print(f"  Label          : {result.label}")
    print(f"  Tier           : {result.recommended_tier}")
    print(f"  Deploy         : {result.deploy_time}")
    print(f"  Setup fee      : EUR {result.setup_fee:,.0f}")
    print(f"  Mensual        : EUR {result.monthly_fee:,.0f}")
    print(f"  Auto-propuesta : {result.auto_proposal}")
    print(f"  Procesos       : {result.processes_detected}")
    print(f"  Cluster        : {result.cluster_detected}")
    print(f"  Razon          : {result.rationale}")
    print(f"{'='*50}")
