# Agentic Zero — Tecnologías y Herramientas de Referencia
## Bloc de notas para mejoras futuras

> Registro rápido de tecnologías, productos y conceptos detectados en artículos,
> investigación y competencia. Cada entrada incluye qué es, por qué importa a AZ
> y cómo podría integrarse o inspirar una mejora.
> Actualizar en cada sesión cuando aparezca algo relevante.

---

## ÍNDICE

| # | Tecnología / Herramienta | Origen | Categoría | Prioridad AZ |
|---|--------------------------|--------|-----------|--------------|
| T001 | CollectivIQ | Steve Nouri / LinkedIn | Multi-LLM / Governance | 🔴 Alta |
| T002 | Work Graph (Asana) | Asana | Context Layer / Orquestación | 🟡 Media-Alta |
| T003 | CooperBench Shield | Stanford HAI / Zhu & Yang ICLR 2026 | Swarm / Multi-Agent | 🔴 Alta |
| T004 | StackAI | Adquirida por Asana May 2026 | Cross-system Execution | 🟡 Media |
| T005 | Asana AI Teammates | Asana | Human-Agent Workflows | 🟡 Media |
| T006 | LayerX Enterprise AI Monitor | LayerX Research 2025 | Shadow AI / Governance | 🟢 Baja |

---

## ENTRADAS DETALLADAS

---

### [T001] CollectivIQ
**Origen:** Steve Nouri (14M seguidores LinkedIn) — producto propio
**Categoría:** Orquestador multi-LLM / Trust layer para decisiones humanas
**Fecha detección:** Junio 2026

#### Qué es
Plataforma que consulta múltiples LLMs simultáneamente (GPT, Claude, Gemini, Grok),
compara las respuestas, detecta contradicciones y genera una respuesta cross-verificada
antes de que el humano tome una decisión. Elimina PII antes de procesar.
Genera audit trail de cada decisión.

#### Funciones clave
- Multi-LLM query en paralelo
- Consensus Engine — busca acuerdo entre modelos
- Contradiction Detection — marca donde los modelos difieren
- PII Removal — elimina datos sensibles antes del prompt
- Audit Trail — registra cada decisión y qué modelos la respaldaron
- Continuous Evaluation — benchmark continuo de modelos emergentes

#### Por qué importa a AZ
CollectivIQ resuelve "decision leakage" (decisiones humanas mal informadas).
AZ resuelve "operational waste" (procesos empresariales ineficientes).
Son capas distintas — CollectivIQ es pre-decisión humana, AZ es pre-operación de agente.

#### Inspiración para AZ
- Nuestro Multi-Model Comparador (T001 → implementado Sprint 7) está inspirado en este concepto
- Diferencia clave: AZ lo aplica a certificación permanente de procesos, no a respuestas efímeras
- Posible integración futura: CollectivIQ como capa de validación humana
  encima de los agentes AZ para decisiones de alto impacto

#### Estado
- [x] Multi-Model Comparador v1.0 implementado — Sprint 7 — inspirado en CollectivIQ
- [ ] Explorar partnership o integración como capa complementaria

---

### [T002] Work Graph (Asana)
**Origen:** Asana — producto core, 18 años de desarrollo
**Categoría:** Context layer / Mapa de trabajo organizacional
**Fecha detección:** Junio 2026

#### Qué es
Modelo de datos que captura las relaciones entre el trabajo (tareas, proyectos, objetivos),
la información (documentos, comentarios, decisiones) y las personas (equipos, responsables,
aprobadores). A diferencia del modelo compartimentado (uno a uno), Work Graph permite
relaciones uno a muchos — una tarea puede pertenecer a múltiples proyectos, un objetivo
puede conectar con varios equipos.

#### Por qué tiene una pinta fantástica
Es exactamente la capa de contexto que los agentes necesitan para operar con inteligencia.
Sin Work Graph (o equivalente), el agente empieza de cero en cada ejecución.
Con Work Graph, el agente sabe quién aprueba qué, qué deadlines importan,
qué proyectos están conectados y cuál es el objetivo que hay que mover.

#### Diferencia con Process Library AZ
| | Work Graph (Asana) | Process Library (AZ) |
|---|---|---|
| Qué mapea | Quién hace qué, cuándo, con qué objetivo | Cómo opera el proceso end-to-end |
| Nivel | Trabajo diario / coordinación humana | Proceso operacional certificado |
| Para qué | Agentes de tarea (Asana AI Teammates) | Agentes autónomos de operación |
| Regulatorio | Governance básica | EU AI Act + ISO 42001 + GDPR |

#### Inspiración para AZ — AZ Work Graph
Construir un equivalente para supply chain regulada:
- Mapa de relaciones entre procesos (qué proceso alimenta a cuál)
- Propietarios por proceso (quién aprueba, quién ejecuta, quién supervisa)
- Estado en tiempo real (qué está corriendo, qué está esperando aprobación)
- Conectado con el dashboard del cliente y el Evidence Shield

#### Estado
- [ ] Diseñar AZ Process Graph como evolución de la Process Library
- [ ] Evaluar integración AZ + Asana (Work Graph + Process Library = capas complementarias)
- [ ] Prioridad: post-launch, Sprint 9-10

---

### [T003] CooperBench Shield (Context Sharing Lateral)
**Origen:** Stanford HAI — Zhu & Yang, ICLR 2026 (abril 2026)
**Categoría:** Arquitectura Swarm / Protección coordination gap multi-agente
**Fecha detección:** Sprint 7 — sesión 11 Jun 2026

#### Qué es
Framework de benchmark y arquitectura para sistemas multi-agente.
Documenta que los sistemas multi-agente pierden ~50% de su capacidad
cuando coordinan sin los mecanismos correctos (coordination gap).

#### Los 4 principios del CooperBench Shield
1. **Reward Coordination** — alinear los incentivos de cada agente con el objetivo global
2. **Commitment + Verification** — cada agente declara su acción antes de ejecutar,
   el sistema verifica que no hay conflictos
3. **Periodic Merges** — estado compartido sincronizado en puntos clave del workflow
4. **Strong Inter-Agent Channels** — canales de comunicación directa entre agentes
   (no solo a través del orquestador central)

#### Por qué es crítico para AZ
Cuando AZ escale de 1 agente (Inmaculada) a Swarm (múltiples agentes coordinados
por proceso — ventas + compras + logística + finanzas + governance + riesgo),
sin CooperBench Shield el sistema perderá ~50% de capacidad en coordinación.
Es el problema que separa un PoC de un sistema productivo robusto.

#### Inspiración para AZ — Context Sharing Lateral
Implementar los 4 principios como módulo en el Pioneer Team:
- Shared state bus entre agentes del Swarm
- Commitment protocol antes de cada acción cross-agente
- Merge points en el workflow (ej. antes de cerrar un OTC cycle)
- Canales directos Builder ↔ Guardian ↔ Packager sin pasar por queue

#### Estado
- [ ] Diseño de arquitectura CooperBench Shield — próximo Sprint
- [ ] Implementar Context Sharing Lateral como desbloqueante 7 del LinkedIn post
- [ ] Prioridad: ALTA — antes de escalar a Swarm con cualquier cliente

---

### [T004] StackAI
**Origen:** Tony Rosinol + Bernard Aceituno (MIT PhDs) — adquirida por Asana Mayo 2026
**Categoría:** No-code cross-system execution / Multi-agent workflows
**Fecha detección:** Junio 2026

#### Qué es
Plataforma no-code para construir, testear y desplegar agentes AI que ejecutan
workflows complejos a través de múltiples sistemas enterprise: Salesforce, Asana,
SharePoint, Oracle, Docusign, AWS, document systems, aplicaciones industriales.
Bi-directional sync. Multi-agent workflows. Casos en financial services,
healthcare y professional services — sectores regulados.

#### Frase fundacional de Rosinol
> "General-purpose agents talk. Specialized agents act."

#### Por qué importa a AZ
StackAI + Asana es el competidor indirecto más peligroso a 18-24 meses.
Tienen cross-system execution (territorio AZ) + no-code + enterprise governance básica
+ miles de clientes Asana + maquinaria de ventas enterprise.

#### Diferenciadores AZ vs StackAI
- AZ tiene 189+ procesos pre-certificados — StackAI empieza desde cero
- AZ tiene compliance regulatorio embebido (EU AI Act, ISO 42001, GxP, IATF)
- AZ tiene ROI medido con Evidence Shield
- AZ está especializado en supply chain regulada (vertical defensible)

#### Inspiración para AZ
- El concepto no-code de StackAI es aspiracional para la pricing page
- Evaluar si AZ puede ofrecer un "configurador no-code" para clientes Essential
  que quieran personalizar reglas de negocio sin tocar código

#### Estado
- [ ] Monitorizar roadmap StackAI post-adquisición — revisión trimestral
- [ ] Evaluar riesgo de colisión en sector industrial en 12 meses
- [ ] Inspiración: configurador no-code para clientes Essential — Sprint 10+

---

### [T005] Asana AI Teammates
**Origen:** Asana — producto activo
**Categoría:** Human-Agent collaborative workflows
**Fecha detección:** Junio 2026

#### Qué es
Agentes AI con identidad propia dentro de Asana — tienen permisos específicos,
pueden aprobar tareas, enrutar solicitudes, interactuar con sistemas y participar
en workflows junto a humanos. Multiplayer: varios humanos pueden interactuar
con el mismo agente, mejorarlo y supervisarlo.

#### Concepto clave — "Agent Palooza" (Dan Rogers, CEO Asana)
El riesgo de agentes corriendo sin controles: sin aprobaciones definidas,
sin control de acceso a datos, sin límites de coste. La respuesta de Asana
es agentes con scoped permissions, approval rules, audit trails y cost controls.

#### Inspiración para AZ
- El concepto de "AI Teammate con identidad propia" es exactamente lo que
  AZ debería comunicar: el agente OTC de Inmaculada no es una herramienta,
  es un miembro del equipo con responsabilidades definidas
- Los 3 controles de Rogers (qué aprueba / qué datos accede / qué coste genera)
  son exactamente lo que M11 Token Governance + M12 Evidence Shield resuelven
- Usar "AI Teammate" como lenguaje de cara al cliente en vez de "agente"

#### Estado
- [ ] Adoptar "AI Teammate" como terminología de cliente en materiales comerciales
- [ ] Los 3 controles de Rogers como checklist de governance en audit.html
- [ ] Inspiración para onboarding deck de Inmaculada

---

### [T006] LayerX Enterprise AI Monitor
**Origen:** LayerX Research — informe 2025
**Categoría:** Shadow AI detection / Enterprise AI governance
**Fecha detección:** Junio 2026 (citado por Steve Nouri)

#### Qué es
Plataforma de monitorización del uso real de AI en empresas.
Detecta uso no autorizado de AI (shadow AI) desde cuentas personales,
mide exposición de datos sensibles y proporciona governance de AI usage.

#### Datos del informe 2025 (los más citables del mercado)
- 89% del uso empresarial de AI es invisible para IT
- 71% ocurre desde cuentas personales (ChatGPT, Claude, Gemini personal)
- 14 prompts/día por empleado con datos de empresa
- ~50% de esos datos son información sensible de la empresa

#### Por qué importa a AZ
Estos datos son el argumento de venta más poderoso que tenemos:
Si el 89% del uso es invisible y el 50% expone datos sensibles,
la alternativa es un agente certificado que opera dentro de los sistemas
del cliente, con EU AI Act embebido, sin exponer datos a modelos externos.

#### Estado
- [ ] Usar los 4 datos de LayerX en argumentario comercial y LinkedIn post
- [ ] Citar fuente: "LayerX Enterprise AI Report 2025"
- [ ] No requiere integración técnica — es inteligencia de mercado

---

## RADAR — Tecnologías a seguir

| Tecnología | Por qué seguirla | Cuándo revisar |
|---|---|---|
| Asana + StackAI roadmap | Competidor indirecto emergente | Trimestral |
| CollectivIQ evolución | Posible partner / inspiración | Semestral |
| CooperBench updates | Base técnica del Shield | Cuando salga paper siguiente |
| Google Gemini tiers | Modelo en nuestro comparador | Mensual |
| xAI grok roadmap | Modelo principal de Herald | Mensual |
| EU AI Act implementación | Agosto 2026 obligatorio | Agosto 2026 |

---

## PLANTILLA PARA NUEVAS ENTRADAS

```
### [TNNN] Nombre de la tecnología
**Origen:** Empresa / Autor / Paper
**Categoría:** [Multi-LLM / Swarm / Context / Execution / Governance / ...]
**Fecha detección:** DD MMM YYYY

#### Qué es
[descripción en 3-5 frases]

#### Por qué importa a AZ
[impacto directo en el negocio o la arquitectura]

#### Inspiración para AZ
[cómo podría integrarse o inspirar una mejora concreta]

#### Estado
- [ ] acción concreta
```

---

*Ultima actualización: 11 junio 2026 — Sprint 7*
*Proxima revision: inicio Sprint 8*
