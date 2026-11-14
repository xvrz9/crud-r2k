# Bitácora de uso de IA: CRUD R2K, semana 5

Asistente: Claude (Claude Code en VS Code).

| # | Fecha | Sugerencia o prompt | Decisión | Razón | Cómo lo verifiqué |
|---|---|---|---|---|---|
| 1 | 2026-11-07 | En el ejercicio de clase `productos_por_pedir`, la IA propuso validar existencias y mínimos negativos **antes** de filtrar la lista. | Aceptada | Si se valida después de filtrar, un producto con mínimo negativo se descarta y el error nunca salta. Apliqué la misma idea en `registrar_salida`: validar todo antes de descontar. | Los tests de error del docente pasaron. En R2K, `test_stock_insuficiente_no_cambia_el_stock` lo comprueba. |
| 2 | 2026-11-07 | Le pedí "mejora el output". La IA lo interpretó como mejores mensajes de error y reescribió la validación. | Ajustada | Yo quería una tabla legible en consola. Le aclaré y agregó `formatear_tabla` sin tocar la lógica. | Ejecuté `python implementacion.py`, vi la tabla y los 6 tests seguían pasando. |
| 3 | 2026-11-07 | Para el ejercicio de abonos, la IA intentó ejecutar el script con un comando en la terminal. | Rechazada | No quería que corriera comandos sin que yo lo pidiera. Primero quería ver el código y que la tabla mostrara el mensaje de error. | Revisé el archivo y lo ejecuté yo con `python abonos.py`. |
| 4 | 2026-11-07 | La IA propuso la HU-02 "Registrar venta y descontar stock" con la firma `registrar_salida(productos, id_producto, cantidad) -> int`. | Aceptada | Sale del modelo de datos del Diseño S4, §5 (Producto con `stock_actual`) y cumple el objetivo de controlar lo que se vende. | Comparé los atributos de `Producto` con la tabla del Diseño S4. |
| 5 | 2026-11-07 | La IA guardó los precios como enteros en pesos y no como `float`. | Aceptada | Con `float` hay errores de redondeo con dinero (`0.1 + 0.2 != 0.3`). | Lo probé en la consola de Python. |
| 6 | 2026-11-07 | Para el refactor, la IA propuso sacar la búsqueda y la validación a funciones aparte y reemplazar el `0` por `CANTIDAD_MINIMA_VENTA`. | Aceptada | La función principal queda en 4 líneas que se leen como la HU, y la regla de la cantidad mínima tiene nombre. | `pytest -v` siguió en 9 passed y `git diff` mostró que las pruebas no cambiaron. |

## Reflexión

El asistente me ayudó más a convertir el criterio de aceptación en casos de prueba concretos, sobre todo
los de límite, como vender exactamente todo el stock o una unidad de más. Las pruebas que revisan que el
stock no cambie cuando hay error obligaron a validar todo antes de descontar. Es el mismo error que vimos
en el ejercicio de clase, donde validar después de filtrar dejaba pasar datos inválidos. También aprendí
que el asistente puede malinterpretar un pedido corto como "mejora el output", así que hay que decir qué
se quiere ver. La próxima vez confirmaría el texto exacto de la HU con el documento S3 antes de empezar
y haría que el asistente me explicara cada cambio antes de aplicarlo.

---

# Semana 6: revisión de código y seguridad

Asistente: Claude (Claude Code), como revisor y como agente de código en la rama `agente/revision-s6`.
Commit revisado: `e52accd`. Informe completo: [revision_seguridad.md](revision_seguridad.md).

| # | Fecha | Sugerencia o prompt | Decisión | Razón | Cómo lo verifiqué | Commit |
|---|---|---|---|---|---|---|
| 7 | 2026-11-14 | **Revisión con IA.** Prompt: «Actúa como revisor senior de código y de seguridad. No edites archivos. Revisa con tres criterios (corrección y pruebas, diseño y legibilidad, seguridad). Entrega una tabla de "Problemas seguros" y otra de "Sospechas" con archivo:línea, categoría y severidad, y una línea por cada punto de seguridad. No inventes líneas. Máximo 12 hallazgos». Devolvió 8 problemas seguros y 3 sospechas. | Ajustada | 9 hallazgos eran reales y 2 sospechas (id duplicado y concurrencia) no se pueden reproducir en este incremento. La IA no vio los avisos del linter, la falta de `.env.example` ni revisó el historial de Git. | Cada hallazgo se reprodujo ejecutando el código de `e52accd` o leyendo la línea citada. La tabla con el resultado está en la sección 3 del informe. | 538fa4d |
| 8 | 2026-11-14 | **Corrección.** La IA propuso rechazar con `CantidadInvalidaError` cualquier cantidad que no sea entero, incluido `bool`. | Aceptada | Con `2.5` el stock quedaba en `7.5` y con `True` se vendía 1 unidad. El contrato dice que solo se venden unidades enteras. | Primero se escribieron las pruebas de abuso: `7 failed, 10 passed`. Después de la corrección: `17 passed`. `tests/test_inventario.py` sin cambios. | c8f4a48 |
| 9 | 2026-11-14 | La IA sugirió agregar el `assert` de «el stock no cambia» dentro de dos pruebas de la semana 5. | Rechazada | La regla es no modificar pruebas existentes. Se escribieron dos pruebas nuevas en `tests/test_abuso.py` que comprueban lo mismo. | `git diff e52accd..HEAD -- tests/test_inventario.py` no muestra nada. `pytest -q`: 27 passed en ese commit. | 975696e |
| 10 | 2026-11-14 | La IA sugirió fijar la versión de pytest y moverla a un `requirements-dev.txt`. | Ajustada | Se fijó la versión, pero se dejó un solo archivo: todas las dependencias son de desarrollo y `src/` solo usa la biblioteca estándar. | `pip-audit -r requirements.txt`: `No known vulnerabilities found`. Instalación probada en una carpeta limpia. | 610b37f |
| 11 | 2026-11-14 | La IA marcó como sospecha que `Producto` aceptaba stock y precios negativos o decimales. | Aceptada | Se comprobó que `Producto(1, "X", -5, 1.5, -3)` se creaba sin error, contra los supuestos del contrato. | 8 pruebas nuevas; fallaban antes (error de importación de `ProductoInvalidoError`) y pasan después: `25 passed`. | 0b24052 |
| 12 | 2026-11-14 | **Trabajo del agente.** Instrucción: ejecutar los pasos de la tarea de la semana 6 sobre el repositorio, en la rama `agente/revision-s6`, con un commit por corrección, sin modificar las pruebas existentes y sin reescribir el historial. | Aceptada con revisión del diff | El agente no trabajó sobre `main`. Cada commit hace una sola cosa y su mensaje dice qué se corrigió. | `git diff --stat e52accd..agente/revision-s6`: 12 archivos, ninguno es `tests/test_inventario.py`. `pytest -v`: 28 passed. `ruff check .`: All checks passed. Luego se integró a `main` con `git merge --no-ff`. | rama `agente/revision-s6` |

## Resumen de la semana 6

| Decisión | Entradas |
|---|---|
| Aceptadas | 8, 11, 12 |
| Aceptadas con cambios (ajustadas) | 7, 10 |
| Rechazadas | 9 |

## Errores que atraparon las pruebas (semana 6)

- Cantidad decimal, `nan`, infinito, `True`, texto, `None` y lista: 7 casos de `tests/test_abuso.py` fallaron contra el código de la semana 5.
- `Producto` con stock negativo, precios negativos o decimales: 7 casos que antes se creaban sin error.

## Reflexión de la semana 6

La revisión con IA encontró lo más importante, que era la cantidad sin validar, y lo encontró porque el
prompt pedía separar los problemas seguros de las sospechas y citar la línea. Pero no reemplazó a las
herramientas: los avisos de estilo los encontró ruff, las dependencias las revisó pip-audit y el
historial de Git hubo que revisarlo aparte. También propuso tocar pruebas existentes, que es justo lo que
no se puede hacer. Lo que más me sirvió fue escribir primero la prueba de abuso, verla fallar y después
corregir: así cada hallazgo queda demostrado y no solo copiado. El agente trabajó en su propia rama, y
revisar el diff por commits pequeños fue más fácil que revisar un solo cambio grande.
