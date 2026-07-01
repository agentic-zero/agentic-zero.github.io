# SWARM_ARCHITECTURE_v1.md

**Agentic Zero — Arquitectura definitiva de Swarm**
Generado por Claude, 25 Jun 2026. Basado en el código real de ambos lados (GPT: `pioneer_team/swarm/`, Claude: `swarm/` + `agentic_shield/` + `the_machine/`), no en el roadmap original.

**Principio rector, ya acordado entre ambos:**

> **Cada artefacto generado tiene exactamente un productor. Los consumidores validan, enriquecen o consumen — nunca regeneran de forma independiente.**

---

## 1. PIPELINE COMPLETO (productor único en cada paso)

```
Architect (pioneer_team/architect/)
        |
        v
Level 2 SIOPs  (00_enterprise_intent/level_2_siops/*.json)
        |
        v
[VALIDADOR] swarm_topology_validator.py (Claude)
        |   - colisión de slug, ciclos, rutas colgantes, campos requeridos
        |   - NO escribe nada. Solo aprueba/rechaza antes de seguir.
        v
swarm_splitter.py (GPT)  <-- ÚNICO PRODUCTOR
        |
        +--> 10_swarm/organisms/<SLUG>/siop_internal.json
        +--> 10_swarm/organisms/<SLUG>/organism_blueprint_seed.json
        +--> 10_swarm/coordination/swarm_coordination_<proceso>.json
        +--> 10_swarm/coordination/swarm_topology.json
        +--> 10_swarm/swarm_manifest.json
        |
        v
swarm_topology_builder.py (GPT)
        |
        +--> 10_swarm/runtime/swarm_topology_runtime.json
        +--> 10_swarm/runtime/escalation_routes.json
        +--> 10_swarm/runtime/shared_context_schema.json
        +--> 10_swarm/runtime/topology_readiness.json
        |
        | event_catalog.json YA NO SE GENERA AQUÍ (ver sección 3)
        v
organism_memory_seed_builder.py (GPT)  <-- ÚNICO PRODUCTOR
        |
        +--> 11_memory/<ORGANISM>/semantic_memory_seed.json
        +--> 11_memory/<ORGANISM>/episodic_seed.json
        +--> 11_memory/<ORGANISM>/risk_seed.json
        +--> 11_memory/<ORGANISM>/kpi_seed.json
        +--> 11_memory/<ORGANISM>/learning_contract.json
        +--> 11_memory/memory_manifest.json
        |
        v
swarm_coordinator_seed_builder.py (GPT)  <-- ÚNICO PRODUCTOR
        |
        +--> 12_coordinator/swarm_coordinator_seed.json
        +--> 12_coordinator/coordinator_runtime_contract.json
        +--> 12_coordinator/coordinator_shield_contract.json
        +--> 12_coordinator/coordinator_learning_contract.json
        +--> 12_coordinator/coordinator_readiness.json
        |
        v
swarm_generator.py (GPT)  <-- ÚNICO PRODUCTOR DE CÓDIGO EJECUTABLE
        |
        +--> 13_swarm_runtime/coordinator/swarm_coordinator_runtime.py
        +--> 13_swarm_runtime/coordinator/coordinator_config.json
        +--> 13_swarm_runtime/organisms/<ORGANISM>/architect_blueprint.json
        +--> 13_swarm_runtime/organisms/<ORGANISM>/agent_runtime.py
        +--> 13_swarm_runtime/organisms/<ORGANISM>/organism_config.json
        +--> 13_swarm_runtime/swarm_runtime_manifest.json
        |
        | [REGRESIÓN] swarm_generator.py (Claude, reconvertido)
        | compara esta salida contra el fixture canónico de producción
        | (distribuciones_norte, 4 organismos verificados byte a byte)
        v
RUNTIME EN EJECUCIÓN (13_swarm_runtime/*.py corriendo de verdad)
        |
        v
runtime_core/event_bus.py + event_router.py
        |
        | event_catalog.py (Claude) <-- ÚNICO PRODUCTOR de event_catalog.json
        | deriva de swarm_coordination_<proceso>.json (ya generado arriba)
        v
the_machine/observer.py
        |  - se ancla contra los siop_internal.json reales (organism profiles)
        v
the_machine/pattern_detector.py -> prescriptor.py
        |
        v
agentic_shield/  (Claude — ya cerrado, sin cambios)
        policy_engine.py -> compliance_engine.py -> threshold_engine.py
        -> approval_engine.py / human_accountability.py -> audit_trails.py
        |
        v
swarm/swarm_coordinator.py (Claude)  <-- ÚNICO PRODUCTOR de detección de conflictos en runtime
        |  - lee swarm_events.jsonl que emiten los agent_runtime.py reales
        |  - detecta gaps (organismos que no han reportado) y conflictos
        |  - NO resuelve, solo detecta y entrega
        v
swarm/constraint_resolution_agent.py (Claude)  <-- ÚNICO PRODUCTOR de resolución de conflictos
        - resuelve por confianza ponderada, o escala si hay impacto crítico
        - idempotente
```

---

## 2. OWNERSHIP — tabla de productor único por artefacto

| Artefacto | Productor único | Quién consume |
|---|---|---|
| `siop_internal.json` | `swarm_splitter.py` (GPT) | `swarm_generator.py` (GPT), `policy_engine.py`, `compliance_engine.py`, `observer.py` |
| `organism_blueprint_seed.json` | `swarm_splitter.py` (GPT) | `swarm_generator.py` (GPT) |
| `swarm_coordination_<proceso>.json` | `swarm_splitter.py` (GPT) | `swarm_topology_builder.py` (GPT), `event_catalog.py` (Claude), `swarm_coordinator.py` (Claude), `constraint_resolution_agent.py` (Claude) |
| `swarm_topology.json`, `swarm_topology_runtime.json`, `escalation_routes.json`, `shared_context_schema.json`, `topology_readiness.json` | `swarm_topology_builder.py` (GPT) | Runtime |
| **`event_catalog.json`** | **`event_catalog.py` (Claude)** | `event_router.py`, `policy_engine.py`, `compliance_engine.py`, `observer.py` |
| `11_memory/*` (semantic/episodic/risk/kpi seeds, learning contracts) | `organism_memory_seed_builder.py` (GPT) | The Machine |
| `12_coordinator/*` (coordinator seeds y contratos) | `swarm_coordinator_seed_builder.py` (GPT) | `swarm_generator.py` (GPT) |
| `agent_runtime.py`, `swarm_coordinator_runtime.py`, `*_config.json`, `swarm_runtime_manifest.json` | `swarm_generator.py` (GPT) | Runtime (ejecución real) |
| Detección de conflictos en runtime (`swarm_conflicts.jsonl`, `swarm_cycle_status.json`) | `swarm_coordinator.py` (Claude) | `constraint_resolution_agent.py` (Claude) |
| Resolución de conflictos (`constraint_resolutions.jsonl`) | `constraint_resolution_agent.py` (Claude) | Shield (vía escalación si aplica) |

**Ningún otro módulo escribe ninguno de estos artefactos.** Si en el futuro un módulo nuevo necesita modificar uno, no lo regenera — llama al productor único o le pide que añada el campo que falte.

---

## 3. EL CASO event_catalog.json — decisión ya tomada, documentada aquí para que quede permanente

Antes de esta sesión, `swarm_topology_builder.py` (GPT) generaba su propio `event_catalog.json` con schema `{event_name, source, targets, payload_schema, required_context, ...}` en la misma ruta donde `event_catalog.py` (Claude) ya escribía `{event_name, category, origin, targets, shield_required}` — dos productores compitiendo por el mismo archivo.

**Decisión final (acordada entre ambos):** `event_catalog.py` (Claude) es el único productor. `swarm_topology_builder.py` deja de generar `event_catalog.json` directamente; en su lugar, una vez que `swarm_coordination_<proceso>.json` está escrito, se invoca `event_catalog.py --coordination-file <path>` para derivar el catálogo real desde los `event_routes` ya presentes en ese archivo.

---

## 4. RESPONSABILIDADES POR MÓDULO

### Lado GPT (autoría/materialización — "qué existe")

| Módulo | Responsabilidad |
|---|---|
| `swarm_splitter.py` | Transforma la decomposición del Architect (Level 2 SIOPs) en la estructura real de organismos y la topología de coordinación |
| `swarm_topology_builder.py` | Deriva los artefactos de runtime de topología (rutas de escalación, schema de contexto compartido) a partir de la topología ya materializada |
| `organism_memory_seed_builder.py` | Siembra la memoria inicial de The Machine por organismo (semántica, episódica, riesgo, KPI, contrato de aprendizaje) |
| `swarm_coordinator_seed_builder.py` | Define el contrato del coordinador (runtime, Shield, aprendizaje) antes de generarlo como código |
| `swarm_generator.py` | Genera el código Python ejecutable real: agentes por organismo y el coordinador del swarm |

### Lado Claude (validación/runtime — "qué es correcto, y qué pasa cuando corre de verdad")

| Módulo | Responsabilidad |
|---|---|
| `swarm_topology_validator.py` (renombrado desde `swarm_splitter.py`) | Valida la topología propuesta **antes** de que `swarm_splitter.py` (GPT) la materialice. No escribe nada. |
| `swarm_generator.py` (reconvertido) | Test de regresión — compara la salida real de `swarm_generator.py` (GPT) contra el fixture canónico de producción (`distribuciones_norte`), no genera nada en producción |
| `event_catalog.py` | Único productor de `event_catalog.json`, derivado de `swarm_coordination_<proceso>.json` |
| `swarm_coordinator.py` | Detecta, en runtime real, gaps de ejecución y conflictos entre organismos para el mismo `scenario_id` |
| `constraint_resolution_agent.py` | Resuelve los conflictos detectados — auto-resolución ponderada por confianza, o escalación si hay impacto crítico o baja confianza |

---

## 5. CONVENCIÓN CANÓNICA — `organism`

**Acordado:** `organism` es el identificador canónico en todo el runtime. `name` queda como metadato de presentación (UI, informes), nunca como clave de lookup.

Regla de slug, **idéntica en ambos lados, sin excepción:**
```
"Demand Planning Organism" -> quitar sufijo " Organism" -> "Demand Planning"
                            -> mayúsculas, no-alfanumérico a "_" -> "DEMAND_PLANNING"
```

Módulos que ya implementan esta regla exacta: `event_catalog.py`, `observer.py`, `policy_engine.py`, `compliance_engine.py`, `swarm_topology_validator.py`, `swarm_coordinator.py`, `constraint_resolution_agent.py` (Claude, 7 módulos). Código nuevo de GPT debe usar `organism` directo, sin cadena de fallback a `name`.

---

## 6. VALIDADORES (Claude) — nunca generan artefactos de producción

```
swarm_topology_validator.py
  - schema validation (campos requeridos por organismo)
  - consistency validation (colisión de slug)
  - graph validation (ciclos, rutas colgantes — DFS)
  - exit code 1 si encuentra ERROR, bloquea avance del pipeline

swarm_generator.py (Claude, regresión)
  - input: salida real de swarm_generator.py (GPT) para un cliente
  - output: PASS/FAIL comparando contra el fixture canónico
  - nunca escribe a 10_swarm/, 11_memory/, 12_coordinator/, 13_swarm_runtime/
```

---

## 7. TESTS REQUERIDOS ANTES DE DECLARAR SWARM GREEN

| # | Test | Cubre |
|---|---|---|
| 1 | `swarm_topology_validator.py` contra una topología real | 0 errores en topología válida |
| 2 | `swarm_topology_validator.py` contra una topología rota a propósito | Detecta colisión de slug, ciclo, ruta colgante |
| 3 | `swarm_splitter.py` (GPT) end-to-end desde Level 2 SIOPs reales | Genera `siop_internal.json`/`organism_blueprint_seed.json` correctos |
| 4 | `event_catalog.py` invocado tras `swarm_splitter.py` (GPT) | Deriva catálogo correcto desde la topología recién generada por GPT, no por Claude |
| 5 | `swarm_generator.py` (GPT) end-to-end | Genera `agent_runtime.py`/`swarm_coordinator_runtime.py` ejecutables |
| 6 | `swarm_generator.py` (Claude, regresión) contra la salida del test 5 | PASS si coincide con el fixture canónico |
| 7 | Runtime real: 2+ organismos emiten eventos conflictivos para el mismo `scenario_id` | `swarm_coordinator.py` detecta el conflicto |
| 8 | `constraint_resolution_agent.py` sobre el conflicto del test 7 | Auto-resuelve o escala según confianza/impacto, correctamente |
| 9 | Pipeline completo de extremo a extremo, un cliente real desde cero | Los 13 pasos del pipeline (sección 1) corren sin colisión de artefactos |

---

## 8. LO QUE QUEDA FUERA DE ESTE DOCUMENTO (decisión explícita, no olvido)

- Integración del `swarm_coordinator_runtime.py` generado por GPT con `swarm_coordinator.py`/`constraint_resolution_agent.py` de Claude (hoy son paralelos, no conectados) — pendiente de la revisión de integración detallada
- Multi-tenant / múltiples clientes corriendo el pipeline simultáneamente — no cubierto aquí
- Manejo de fallos parciales a mitad del pipeline (ej. `swarm_splitter.py` corre bien pero `swarm_topology_builder.py` falla) — no cubierto aquí, recomendado para la revisión de integración

---

## 9. IMPLEMENTACIÓN REAL — 26 Jun 2026, validada de extremo a extremo

Esta sección documenta el trabajo de implementación real (no solo diseño) hecho sobre el código de ambos lados, con el pipeline completo de 9 módulos corriendo de verdad sobre datos reales del fixture de producción (`distribuciones_norte`, 11 organismos).

### 9.1 Fix aplicado — `event_catalog.json` (sección 3)

`swarm_topology_builder.py` (GPT) ya **no** genera `event_catalog.json` — delega a `runtime_core/event_catalog.py` (Claude) pasándole el `coordination_file` que ya tenía cargado. La función `build_event_catalog()` original queda como código muerto, marcado explícitamente como deprecado (no es un descuido).

**Verificado:** pipeline real `swarm_splitter.py` → `swarm_topology_builder.py` → `event_catalog.py` produce 20 eventos, schema correcto (`category`/`origin`/`targets`/`shield_required`), `demand_planning_updated` con los 4 targets reales — idéntico al resultado validado hace semanas, ahora producido por código de ambos lados encadenado.

### 9.2 Hallazgo adicional — el bug de slug estaba copiado en 4 sitios, no en 1

Al corregir el lookup `organism`/`name` en `swarm_splitter.py`, se descubrió que el algoritmo de slug en sí (no solo el campo de origen) **no quitaba el sufijo `" Organism"`** — y esa misma función `_slug()` estaba **copiada de forma independiente en 4 archivos distintos**, cada uno con la misma omisión:

| Archivo | Función afectada | Uso |
|---|---|---|
| `swarm_splitter.py` (GPT) | `_slug()` / `_upper_slug()` | Nombra `10_swarm/organisms/<SLUG>/` |
| `organism_memory_seed_builder.py` (GPT) | `_slug()` / `_upper_slug()` | Nombra `11_memory/<SLUG>/` |
| `swarm_generator.py` (GPT) | `_slug()` (uso mixto: organismos **y** nombres de sistema) | Nombra `13_swarm_runtime/organisms/<SLUG>/` |
| `swarm_coordinator_seed_builder.py` (GPT) | — | Confirmado limpio, no maneja slugs de organismo |

**Por qué nunca se notó:** en `swarm_splitter.py`, el lookup probaba `name` antes que `organism`, y `name` no lleva el sufijo — así que el bug quedaba enmascarado por una coincidencia de datos, no por estar realmente corregido. En cuanto se pasó a usar `organism` directamente (la decisión ya acordada en la sección 5), el bug se manifestaba de inmediato: `"Demand Planning Organism"` → `DEMAND_PLANNING_ORGANISM` en vez de `DEMAND_PLANNING`, desincronizando `11_memory/` y `13_swarm_runtime/organisms/` respecto a `10_swarm/organisms/`.

**Fix aplicado en los 3 archivos reales:** la regla de slug ahora quita el sufijo `" Organism"` antes de slugificar, idéntica byte a byte a `organism_to_slug()` de Claude. En `swarm_generator.py`, donde `_slug()` también se usa para nombres de sistema (no organismos, ej. `"SAP IBP"` → `SAP_IBP_HOST` para variables de entorno), se añadió una función separada `organism_slug()` específica para organismos, sin tocar el uso genérico existente.

**Verificado:** tras el fix, las carpetas de organismo en `10_swarm/organisms/`, `11_memory/` y `13_swarm_runtime/organisms/` son **exactamente las mismas 11**, confirmado programáticamente (`swarm == memory == runtime`), no solo a simple vista.

### 9.3 Validación end-to-end completa — pipeline real, no simulado

Ejecutado con 11 Level 2 SIOPs reales (derivados del fixture de producción) a través de los 9 módulos en orden:

```
swarm_splitter.py (GPT)              -> 11 organismos, slugs correctos
swarm_topology_builder.py (GPT)      -> 11 nodos, 17 edges, 20 eventos (via event_catalog.py)
swarm_topology_validator.py (Claude) -> Valid: True, 0 errores
organism_memory_seed_builder.py (GPT)-> 11 carpetas de memoria, slugs coincidentes
swarm_coordinator_seed_builder.py (GPT) -> ready_for_swarm_generator: True
swarm_generator.py (GPT)             -> código Python real generado, COMPILA
swarm_coordinator.py (Claude)        -> detecta conflicto real sobre datos del pipeline
constraint_resolution_agent.py (Claude) -> ESCALATED correctamente (baja confianza)
```

**Ningún paso fue simulado o mockeado.** Cada módulo se ejecutó con la salida real del anterior.

### 9.4 Archivos entregados (corregidos, no solo diseñados)

- `swarm_splitter.py` (GPT) — fix de slug + lookup `organism`
- `swarm_topology_builder.py` (GPT) — delegación a `event_catalog.py`
- `organism_memory_seed_builder.py` (GPT) — fix de slug
- `swarm_generator.py` (GPT, entregado como `gpt_swarm_generator.py` para no chocar con el archivo de Claude del mismo nombre) — fix de slug específico para organismos
- `swarm_topology_validator.py` (Claude, renombrado desde `swarm_splitter.py`) — textos de salida actualizados tras el renombrado
- `swarm_coordinator.py`, `constraint_resolution_agent.py` (Claude) — sin cambios, re-validados contra el pipeline real

**Pendiente, no bloqueante:** reconvertir formalmente `swarm_generator.py` (Claude) en validador de regresión contra la salida de `gpt_swarm_generator.py` (hoy ese rol se cumplió manualmente en esta sesión, falta encapsularlo en un script reutilizable).

---

*Documento generado por Claude. Sección 9 añadida tras implementación y validación real el 26 Jun 2026. Revisión cruzada de GPT pendiente antes de considerarlo cerrado — mismo patrón ya usado para los documentos de sync anteriores.*
