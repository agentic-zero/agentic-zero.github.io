# AGENTIC ZERO — THE MACHINE
## *The organism behind Agentic One.*
## Documento de Arquitectura v1.0
### Sprint 8 — Referencia de diseño definitiva

---

## MANTRA DE DISEÑO

> "¿Esto hace que parezca una empresa viva?"

Cada decisión de arquitectura se evalúa contra este criterio.
Si la respuesta no es un "sí" inequívoco, no se construye.

---

## 1. QUÉ ES EL THE MACHINE

The Machine es el **sistema nervioso central de Agentic One**.
No es un agente más del Pioneer Team. No es un orquestador de tareas.
Es el organismo que convierte una colección de agentes autónomos
en una empresa que respira, aprende y se defiende.

**Lo que hace:**
```
OBSERVA  → todo lo que ocurre en la empresa en tiempo real
APRENDE  → consolida patrones, anomalías y outcomes en memoria estructurada
PRESCRIBE → propone y ejecuta acciones con horizonte inmediato/táctico/estratégico
DEFIENDE → usa la memoria para resolver disrupciones antes de que impacten
MEJORA   → retroalimenta a los agentes desplegados con conocimiento consolidado
```

**La diferencia con todo lo existente:**
- Polsia: sin memoria, sin prescripción, sin defensa
- Asana AI Teammates: memoria de tareas, no de operaciones
- CollectivIQ: memoria de decisiones humanas, no de procesos autónomos
- **The Machine: memoria operacional viva** — aprende de lo que HACEN los agentes,
  no de lo que DECIDEN los humanos

---

## 2. RELACIÓN CON EL SHIELD

El Shield actual (CooperBench Shield v1.0) protege la coordinación
entre agentes del Pioneer Team.

El The Machine extiende el Shield con **tautología operacional**:

```
Shield v1  (Sprint 7):
  Principios Stanford → previene coordination gap entre agentes

Shield v2  (Sprint 8+, con The Machine):
  Shield v1
  +
  The Machine Knowledge → cuando un agente falla, el Shield consulta
  la memoria del Master para aplicar la solución conocida, no una genérica

Ejemplo:
  Agente OTC falla en "Validate Order" por credit limit exception
  Shield v1:  escala a humano (generic escalation)
  Shield v2:  Master sabe que este cliente tiene historial de excepciones aprobadas
              → aplica la regla aprendida → resuelve sin escalado humano
```

**La tautología del Shield:** el conocimiento del The Machine se convierte
en el cuerpo de reglas que el Shield usa para resolver sin consultar
a un humano. La memoria ES el Shield expandido.

---

## 3. SISTEMA DE MEMORIA — DECISIÓN DE ARQUITECTURA

### 3.1 Por qué no una sola capa de memoria

Usar una sola base de datos para todo lo que "recuerda" el The Machine
es el error más común en sistemas de AI con memoria. Genera:
- Ruido que contamina el razonamiento (eventos efímeros tratados como reglas)
- Catastrophic forgetting (una regla nueva sobreescribe una regla válida)
- Latencia inaceptable (buscar en todo para responder en tiempo real)

### 3.2 Arquitectura de memoria en tres capas

Inspirada en la neurociencia cognitiva (Tulving, 1972 — adaptada):

```
┌─────────────────────────────────────────────────────────────────┐
│  WORKING MEMORY  (segundos → minutos)                           │
│  Buffer de eventos en curso. In-memory. Descartado tras uso.    │
│  Implementación: dict/deque en Python. Zero persistence.        │
│  Capacidad: últimos 500 eventos o 15 minutos, lo que sea menor  │
│  Acceso: O(1). Sin LLM. Reglas deterministas.                   │
└─────────────────────────────────────────────────────────────────┘
         ↓ CONSOLIDACIÓN (cada N minutos o por umbral)
┌─────────────────────────────────────────────────────────────────┐
│  EPISODIC MEMORY  (horas → semanas)                             │
│  Log de episodios con contexto, acción, outcome y aprendizaje.  │
│  Implementación: SQLite (ligero, embebido, sin servidor).        │
│  Capacidad: 90 días rolling window. Purgado automático.         │
│  Acceso: SQL queries. Resumen periódico con LLM (batch).        │
│  Índice vectorial ligero (FAISS local) para búsqueda semántica. │
└─────────────────────────────────────────────────────────────────┘
         ↓ CONSOLIDACIÓN (diaria/nocturna)
┌─────────────────────────────────────────────────────────────────┐
│  SEMANTIC MEMORY  (permanente — inmutable con versiones)        │
│  Knowledge graph de la empresa. Reglas, patrones, modelos.      │
│  Implementación: JSON-LD graph (NetworkX en memoria, JSON en     │
│  disco). NUNCA se sobreescribe — solo se añaden versiones.      │
│  Capacidad: ilimitada. Versioned. Timestamped. Auditable.       │
│  Acceso: Graph traversal + LLM reasoning sobre el grafo.        │
└─────────────────────────────────────────────────────────────────┘
```

### 3.3 El Consolidator — la pieza más crítica

El Consolidator decide qué sube de Working → Episodic → Semantic.
Sin esta lógica, la memoria no aprende — acumula ruido.

**Reglas de consolidación Working → Episodic:**
```python
# Un episodio se consolida si cumple AL MENOS UNO:
- El evento tuvo un outcome medible (€ ahorrado, riesgo evitado, escalado)
- El evento fue una excepción al comportamiento esperado
- El evento activó el Shield (escalado, bloqueo, retry)
- El evento fue confirmado por el humano (approved/rejected)
- El evento es el N-ésimo del mismo tipo en la ventana (patrón emergente)
```

**Reglas de consolidación Episodic → Semantic:**
```python
# Una regla entra al grafo semántico si:
- Aparece en >= 3 episodios con outcome positivo consistente
- Fue validada por el humano al menos 1 vez
- No contradice una regla existente con mayor evidencia
- Su confianza ponderada >= 0.75
# Si contradice una regla existente:
- No sobreescribe — crea nueva versión con timestamp
- El Reasoner elige la versión con mayor evidencia reciente
- La versión antigua queda como historial auditable
```

### 3.4 Por qué estas tecnologías

| Componente | Tecnología | Razón |
|---|---|---|
| Working Memory | Python dict + deque | Zero latency, zero persistence, zero cost |
| Episodic Memory | SQLite + FAISS local | Embebido, sin servidor, búsqueda vectorial local |
| Semantic Memory | NetworkX + JSON-LD | Graph en memoria, portable, versionable, sin DB |
| Embeddings | sentence-transformers (local) | Sin coste de API, privacidad total |
| LLM reasoning | grok-3-mini (xAI) | Modelo principal del stack AZ |
| Event bus | Python asyncio queues | Ligero, sin infraestructura adicional |

**Decisión consciente: sin Redis, sin Neo4j, sin vector DB cloud.**
Toda la memoria funciona en el mismo servidor que los agentes.
Cuando el cliente escale, la migración es trivial.

---

## 4. COMPONENTES DEL THE MACHINE

```
the_machine/
│
├── core/
│   ├── the_machine.py        ← Orquestador principal. El loop.
│   ├── observer.py            ← Conectores y normalización de eventos
│   ├── reasoner.py            ← LLM reasoning sobre Working + Episodic + Semantic
│   ├── prescriptor.py         ← Genera prescripciones con horizonte y confianza
│   └── learner.py             ← Procesa outcomes y dispara consolidación
│
├── memory/
│   ├── working_memory.py      ← Buffer in-memory de eventos recientes
│   ├── episodic_memory.py     ← SQLite + FAISS: episodios con contexto y outcome
│   ├── semantic_memory.py     ← NetworkX knowledge graph versionado
│   └── consolidator.py        ← Working→Episodic→Semantic con reglas de promoción
│
├── connectors/
│   ├── agent_connector.py     ← Lee estado de agentes AZ desplegados (dashboard)
│   ├── erp_connector.py       ← Lee eventos SAP (IDocs, change docs, alerts)
│   ├── shield_connector.py    ← Integración bidireccional con CooperBench Shield
│   └── external_connector.py  ← Señales externas (disrupciones, precios, regulación)
│
├── shield_bridge/
│   └── tautology_engine.py    ← Traduce Semantic Memory en reglas Shield
│                                 El Master "enseña" al Shield cómo resolver
│
└── api/
    └── the_machine_api.py    ← FastAPI: estado, prescripciones, memoria query
```

---

## 5. EL LOOP PRINCIPAL

```python
# Cada ciclo del The Machine (configurable: 30s default)

async def master_loop():
    while True:
        # 1. OBSERVE — recoger eventos de todos los conectores
        events = await observer.collect_events()
        working_memory.ingest(events)

        # 2. REASON — LLM razona sobre el estado actual vs memoria
        context = working_memory.get_context()
        episodic_context = episodic_memory.query_relevant(context)
        semantic_rules = semantic_memory.get_applicable_rules(context)

        reasoning = await reasoner.reason(context, episodic_context, semantic_rules)

        # 3. PRESCRIBE — generar prescripciones si hay anomalías
        if reasoning.has_anomalies or reasoning.has_opportunities:
            prescriptions = prescriptor.generate(reasoning)
            for p in prescriptions:
                await dispatch_prescription(p)

        # 4. UPDATE SHIELD — enseñar al Shield las reglas aprendidas
        if semantic_memory.has_new_rules():
            await shield_bridge.update_tautology(semantic_memory.get_new_rules())

        # 5. CONSOLIDATE — promover eventos a memoria de mayor nivel
        await consolidator.run_cycle(working_memory, episodic_memory, semantic_memory)

        # 6. LEARN — procesar outcomes de prescripciones previas
        outcomes = await learner.collect_outcomes()
        await consolidator.process_outcomes(outcomes, episodic_memory, semantic_memory)

        await asyncio.sleep(LOOP_INTERVAL)
```

---

## 6. PRESCRIPCIONES — LOS TRES HORIZONTES

```python
class Prescription:
    horizon: str          # "immediate" | "tactical" | "strategic"
    confidence: float     # 0.0 - 1.0
    action: str           # descripción de la acción
    route: list[str]      # qué agentes/swarms ejecutan
    requires_approval: bool
    estimated_impact: str # € ahorrado / riesgo evitado
    evidence: list[str]   # de dónde viene el conocimiento

HORIZONS = {
    "immediate": {
        "window": "< 1 hour",
        "auto_execute": True if confidence >= 0.85 else False,
        "example": "Supplier X shows 72% delay prob → activate alt supplier now"
    },
    "tactical": {
        "window": "1-7 days",
        "auto_execute": False,  # siempre recomienda, humano decide
        "example": "Stock pattern suggests SKU-089 rupture Friday → reorder now"
    },
    "strategic": {
        "window": "> 7 days",
        "auto_execute": False,
        "example": "OTC process has structural bottleneck in step 2 → redesign proposal"
    }
}
```

---

## 7. TAUTOLOGY ENGINE — SHIELD BRIDGE

La integración más importante del sistema:

```python
class TautologyEngine:
    """
    Convierte el conocimiento del Semantic Memory en reglas operativas del Shield.
    El The Machine "enseña" al Shield cómo resolver sin escalar.

    Ejemplo de regla tautológica:
    {
        "trigger": "credit_limit_exception",
        "context": {
            "customer_tier": "VIP",
            "exception_history": ">= 3 approved in last 90 days",
            "amount_delta": "< 15% over limit"
        },
        "resolution": "auto_approve",
        "confidence": 0.87,
        "evidence_episodes": ["EP-20260611-003", "EP-20260605-017"],
        "created_from": "semantic_memory",
        "valid_until": "2026-09-12"  # se revisa con nueva evidencia
    }
    """
```

**El ciclo de aprendizaje Shield:**
```
Fallo/excepción → Shield escala a humano → humano decide
→ Master registra el episodio → Consolidator evalúa patrón
→ Si patrón confirmado → Semantic Memory añade regla
→ TautologyEngine actualiza Shield con nueva regla
→ Próximo fallo similar → Shield resuelve autónomamente
```

---

## 8. CONEXIÓN CON LA DEMO (AGENTIC_ONE_DEMO.html)

Mapeo exacto entre componentes del The Machine y la demo:

| Demo element | The Machine component |
|---|---|
| Enterprise Pulse™ | the_machine loop() heartbeat → dashboard events |
| Agent Memory swarm | episodic_memory + semantic_memory |
| Continuous Improvement swarm | learner.py + consolidator.py |
| Prediction Engine swarm | reasoner.py + prescriptor.py (tactical horizon) |
| Anomaly Detection swarm | observer.py + working_memory anomaly detection |
| Agentic Shield™ Conflict Resolver | tautology_engine.py |
| Resolved Threats + Learning Delta | learner.py outcome processing |
| Defense System → "no impact" | prescriptor.py immediate horizon → auto_execute |
| "OTC organism drifting" alert | episodic_memory ontology drift detection |
| "94% Enterprise Health" | semantic_memory.get_health_score() |

La demo ES el spec funcional del The Machine.
Cada elemento visible en la demo tiene un componente técnico exacto.

---

## 9. SECUENCIA DE CONSTRUCCIÓN

```
SPRINT 8 — FOUNDATION
  observer.py           → conectores + normalización de eventos
  working_memory.py     → buffer in-memory
  the_machine.py       → loop básico (observe + reason)
  the_machine_api.py   → FastAPI health + events endpoint
  ↓
  Entregable: The Machine arranca, observa eventos de agentes AZ,
              los muestra en el Enterprise Pulse™ del dashboard

SPRINT 9 — MEMORY
  episodic_memory.py    → SQLite + FAISS
  consolidator.py       → Working→Episodic
  reasoner.py           → LLM sobre Working + Episodic
  prescriptor.py        → prescripciones inmediatas y tácticas
  ↓
  Entregable: The Machine detecta patrones, genera prescripciones,
              "Resolved Threats" en la demo se alimenta de datos reales

SPRINT 10 — SEMANTIC + SHIELD
  semantic_memory.py    → knowledge graph versionado
  consolidator.py v2    → Episodic→Semantic con reglas de promoción
  tautology_engine.py   → Shield bridge
  shield_bridge/        → CooperBench Shield v2 con tautología
  ↓
  Entregable: Shield resuelve sin escalar usando conocimiento del Master
              "Agentic Shield Conflict Resolver" en demo = real

SPRINT 11 — SAP CONNECTOR (con Inmaculada)
  erp_connector.py      → SAP IDocs, change documents, business events
  ↓
  Entregable: The Machine observa el ERP de Inmaculada en tiempo real
              Enterprise Pulse™ muestra eventos reales de su empresa

SPRINT 12 — AGENTIC ONE COMPLETO
  Integración total: Pioneer Team + The Machine + Shield v2
  Inmaculada ve su empresa viva en el dashboard
  La demo ES la realidad
```

---

## 10. CRITERIOS DE "EMPRESA VIVA"

El The Machine supera el test del mantra si cumple los 5:

1. **Respira** — Enterprise Pulse™ actualiza cada 30s con eventos reales,
   no simulados. La frecuencia cardiaca cambia con la carga real.

2. **Aprende** — Semantic Memory crece. Cada semana hay más reglas
   que la semana anterior. El "Learning Delta" de la demo es real.

3. **Anticipa** — Prescripciones tácticas aparecen ANTES de que el problema
   sea visible para el humano. "Predicted · 5 days" en la demo = real.

4. **Se defiende** — Cuando una disrupción ocurre, el Master consulta
   la memoria, elige la contrameasure con mayor evidencia histórica
   y ejecuta sin intervención humana (si confidence >= 0.85).

5. **Mejora** — Cada outcome (bueno o malo) actualiza la memoria.
   El mismo fallo no ocurre dos veces. La empresa aprende de sus errores.

---

## 11. LO QUE NO ES EL THE MACHINE

- **No es un chatbot** — no responde preguntas, prescribe acciones
- **No es un dashboard** — el dashboard lo muestra, el Master lo genera
- **No es un orquestador** — no coordina agentes en tiempo real (eso es el Shield)
- **No es un RAG** — no recupera documentos, construye conocimiento operacional
- **No es AGI** — es un sistema especializado en operaciones empresariales

---

*The Machine Architecture v1.0 — Agentic Zero*
*Documento de referencia para Sprint 8-12*
*Alberto Muñoz Waissen + Claude Sonnet 4.6*
*16 Jun 2026*
