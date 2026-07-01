# SAAS_TEST_MATRIX.md

**Generado por Claude — 25 Jun 2026. Validación real ejecutada (compilación + smoke test oficial + pruebas dirigidas de fallo), no estimación.**

---

## RESULTADO GLOBAL

```
SaaS Smoke Test oficial (saas_smoke_test.py):  12 / 12 PASS
Compilación de los 10 módulos:                  10 / 10 OK
Bugs reales encontrados:                         3 (2 críticos, 1 de negocio)
```

**Veredicto: NO declarar GREEN todavía.** El smoke test oficial pasa limpio porque solo prueba el camino feliz — las pruebas dirigidas de fallo (mismo método aplicado ayer a `security/`, donde encontramos 4 bugs reales antes de cerrar Fase 2.8) encontraron 3 problemas reales, 2 de ellos con el mismo patrón de bug que ya corregimos esta misma sesión en otro lugar.

---

## MATRIZ POR MÓDULO

| Módulo | Compila | Smoke test oficial | Hallazgo propio |
|---|---|---|---|
| `tenant_manager.py` | ✅ | ✅ | ⚠️ Enum sin blindar (ver Hallazgo 1) |
| `billing_manager.py` | ✅ | ✅ | ⚠️ Enum sin blindar + plan typo silencioso (Hallazgos 1 y 2) |
| `subscription_sync.py` | ✅ | ✅ | Hereda el crash de `billing_manager` sin capturarlo |
| `customer_portal.py` | ✅ | ✅ | ⚠️ **El más grave** — un billing corrupto tumba toda la vista del cliente |
| `usage_analytics.py` | ✅ | ✅ | Limpio |
| `monitoring_manager.py` | ✅ | ✅ | ⚠️ El sistema de monitorización crashea en vez de reportar CRITICAL |
| `deployment_manager.py` | ✅ | ✅ | ⚠️ Enum sin blindar (mismo patrón, no probado en producción aún) |
| `backup_manager.py` | ✅ | ✅ | ⚠️ Enum sin blindar + Hallazgo 3 (fuga de aislamiento entre tenants) |
| `disaster_recovery.py` | ✅ | ✅ | ⚠️ Enum sin blindar (2 ocurrencias) |
| `saas_smoke_test.py` | ✅ | ✅ | Limpio. Confirmada idempotencia en 3 corridas consecutivas sin limpiar estado |

---

## HALLAZGO 1 (CRÍTICO) — Reconstrucción de enum sin blindar, repetida en 5 módulos

**Mismo patrón exacto que se encontró y corrigió hoy en `security/entitlement_guard.py` y `security/license_manager.py`** — pero sin aplicar el mismo fix aquí.

```python
status=BillingStatus(data["status"]),   # billing_manager.py:112
status=TenantStatus(data["status"]),    # tenant_manager.py:99
status=DeploymentStatus(data["status"]), # deployment_manager.py:143
status=BackupStatus(data["status"]),    # backup_manager.py:149
status=RecoveryStatus(data["status"]),  # disaster_recovery.py:163, 187
```

Si el archivo JSON tiene un valor de `status` corrupto, mal escrito a mano, o parcialmente escrito por un crash a mitad de operación, `Enum(valor_invalido)` lanza `ValueError` **sin capturar**.

### Impacto real confirmado (no teórico)

```
>>> python3 -c "
from saas.customer_portal import CustomerPortal
portal = CustomerPortal()
portal.get_customer_view('dis_solar')  # con billing.json corrupto a mano
"
CRASH: ValueError: 'ACTVE' is not a valid BillingStatus
```

**Esto significa que un solo archivo de billing corrupto tumba la vista completa del Customer Portal para ese cliente.** No es un fallo aislado de un widget de billing — `get_customer_view()` revienta entero, así que el cliente vería una página de error en lugar de su dashboard.

```
>>> python3 -c "
from saas.monitoring_manager import MonitoringManager
MonitoringManager().run_checks('dis_solar')  # mismo archivo corrupto
"
CRASH: ValueError: 'ACTVE' is not a valid BillingStatus
```

**Más grave todavía:** el módulo cuyo propósito explícito es detectar y reportar `CRITICAL` **revienta en vez de reportar `CRITICAL`** ante ese mismo escenario. El sistema de monitorización no es resiliente exactamente al tipo de fallo que debería vigilar.

### Fix recomendado (ya existe el patrón, solo hay que replicarlo)

Exactamente el mismo `try/except ValueError: fallback a estado seguro` que ya está en producción en `entitlement_guard.check()` y `license_manager.load_license()`. Para `billing_manager`/`tenant_manager`/`deployment_manager` el fallback seguro sería el estado más restrictivo de cada enum (`SUSPENDED`, `LOCKED`, `FAILED` respectivamente). Para `backup_manager`/`disaster_recovery`, fallback a `FAILED`.

---

## HALLAZGO 2 (NEGOCIO, no seguridad) — Typo en nombre de plan factura silenciosamente a €0

```python
PLAN_PRICES = {"ESSENTIAL": 490.0, "STANDARD": 990.0, "ENTERPRISE": 1800.0}
...
monthly_amount=self.PLAN_PRICES.get(plan_key, 0.0)
```

Confirmado:
```
>>> billing_manager.create_billing(client_id='x', product='AGENTIC_ONE', plan='ENTERPRICE')  # typo real
Plan guardado: ENTERPRICE
Importe mensual: 0.0 EUR
```

Cualquier typo en el nombre del plan (al crear el tenant, en un formulario, en un script) factura a **€0/mes sin ningún aviso ni error**. No es un bug de seguridad, es un bug de ingresos silencioso. Recomendación: `create_billing` debería rechazar (`ValueError`) un `plan` que no esté en `PLAN_PRICES`, no aceptar y poner precio cero en silencio.

---

## HALLAZGO 3 (ARQUITECTÓNICO) — CORREGIDO

`backup_manager.create_backup(client_id="dis_solar")` copiaba `saas/state/` y `security/state/` **completos** (todas las subcarpetas, todos los clientes), no solo los archivos de `dis_solar`. Confirmado en la prueba original: el backup de `dis_solar` contenía `saas__state/billing/typo_test.json` — datos de otro cliente.

**Corregido:** `backup_manager.py` ahora copia una lista explícita de archivos con scope por `client_id` (`CLIENT_SCOPED_FILES`), no carpetas completas. Verificado tras el fix: un backup nuevo de `dis_solar` contiene exactamente 8 archivos, todos propios, ninguno de otros clientes. `disaster_recovery.py` sigue funcionando sin cambios sobre el nuevo formato (restauración de 8/8 archivos confirmada).

---

## LO QUE SÍ FUNCIONA BIEN — confirmado con prueba de integración real, no solo unitaria

**El flujo de negocio más importante de todo SaaS está validado de extremo a extremo:**

```
billing_manager.mark_past_due('dis_solar')
        v
subscription_sync.sync_client('dis_solar')  ->  entitlement_status: READ_ONLY
        v
SecurityGateway.authorize(action='execute')  ->  allowed: False, decision: DENY
```

Un impago real bloquea ejecución real, a través de toda la cadena, sin atajos. Esto es exactamente lo que el blueprint pedía probar en el Test 3, y funciona.

**Idempotencia confirmada:** 3 corridas consecutivas de `saas_smoke_test.py` sin limpiar estado, sin colisión (a diferencia del bug que sí encontramos hoy en el smoke test de `runtime_entrypoint.py`, aquí el diseño con guards `if not exists` ya lo evita correctamente).

**Separación de responsabilidades respetada:** `subscription_sync.py` nunca llama a Shield/Runtime/The Machine, tal como exige el blueprint — confirmado leyendo el código, no solo la documentación.

---

## RECOMENDACIÓN FINAL

**Los 3 hallazgos están corregidos y re-verificados, no solo documentados.** Archivos modificados: `billing_manager.py`, `tenant_manager.py`, `deployment_manager.py`, `backup_manager.py`, `disaster_recovery.py`.

- Hallazgo 1 (crash de enum en 5 módulos) → corregido, mismo patrón que `security/`. Re-probado: ya no crashea, falla cerrado al estado más restrictivo de cada enum.
- Hallazgo 2 (plan typo facturando a €0) → corregido. `create_billing` ahora rechaza explícitamente un plan no reconocido.
- Hallazgo 3 (fuga de aislamiento entre tenants en backups) → corregido. `backup_manager.py` ahora copia archivos con scope explícito por `client_id`, no carpetas compartidas completas.

**Smoke test oficial tras todos los fixes: 12/12, sin regresiones.**

**Veredicto: Fase 3.0 SaaS Foundation puede declararse GREEN** con estos 5 archivos actualizados.
