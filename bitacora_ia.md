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

Asistente: Claude (Claude Code). Lo usé como segundo revisor del código y para aplicar las correcciones
en la rama `agente/revision-s6`.
Commit revisado: `104eada`. Informe completo: [docs/06_revision_codigo_S6.md](docs/06_revision_codigo_S6.md).

| # | Fecha | Sugerencia o prompt | Decisión | Razón | Cómo lo verifiqué | Commit |
|---|---|---|---|---|---|---|
| 7 | 2026-11-14 | **Revisión con IA.** Prompt: «Actúa como revisor senior de código y de seguridad. No edites archivos. Revisa con tres criterios (corrección y pruebas, diseño y legibilidad, seguridad). Entrega una tabla de "Problemas seguros" y otra de "Sospechas" con archivo:línea, categoría y severidad, y una línea por cada punto de seguridad. No inventes líneas. Máximo 12 hallazgos». Devolvió 8 problemas seguros y 3 sospechas. | Ajustada | 9 hallazgos eran reales y 2 sospechas (id duplicado y concurrencia) no se pueden reproducir en este incremento. La IA no vio los avisos del linter, la falta de `.env.example` ni revisó el historial de Git. | Cada hallazgo se reprodujo ejecutando el código de `104eada` o leyendo la línea citada. La tabla con el resultado está en la sección 3 del informe. | 4b77c44 |
| 8 | 2026-11-14 | **Corrección.** La IA propuso rechazar con `CantidadInvalidaError` cualquier cantidad que no sea entero, incluido `bool`. | Aceptada | Con `2.5` el stock quedaba en `7.5` y con `True` se vendía 1 unidad. El contrato dice que solo se venden unidades enteras. | Primero se escribieron las pruebas de abuso: `7 failed, 10 passed`. Después de la corrección: `17 passed`. `tests/test_inventario.py` sin cambios. | 930e81a |
| 9 | 2026-11-14 | La IA sugirió agregar el `assert` de «el stock no cambia» dentro de dos pruebas de la semana 5. | Rechazada | La regla es no modificar pruebas existentes. Se escribieron dos pruebas nuevas en `tests/test_abuso.py` que comprueban lo mismo. | `git diff 104eada..HEAD -- tests/test_inventario.py` no muestra nada. `pytest -q`: 27 passed en ese commit. | ae651b9 |
| 10 | 2026-11-14 | La IA sugirió fijar la versión de pytest y moverla a un `requirements-dev.txt`. | Ajustada | Se fijó la versión, pero se dejó un solo archivo: todas las dependencias son de desarrollo y `src/` solo usa la biblioteca estándar. | `pip-audit -r requirements.txt`: `No known vulnerabilities found`. Instalación probada en una carpeta limpia. | bb3b61d |
| 11 | 2026-11-14 | La IA marcó como sospecha que `Producto` aceptaba stock y precios negativos o decimales. | Aceptada | Se comprobó que `Producto(1, "X", -5, 1.5, -3)` se creaba sin error, contra los supuestos del contrato. | 8 pruebas nuevas; fallaban antes (error de importación de `ProductoInvalidoError`) y pasan después: `25 passed`. | ad1ffd8 |
| 12 | 2026-11-14 | **Aplicar las correcciones.** Con la tabla de hallazgos ya decidida, le pedí aplicar las correcciones en la rama `agente/revision-s6`, un commit por cada una, sin modificar las pruebas existentes y sin reescribir el historial. | Aceptada con revisión del diff | Trabajar en otra rama me dejó revisar cada cambio antes de pasarlo a `main`. Cada commit hace una sola cosa. | `git diff --stat 104eada..agente/revision-s6`: 12 archivos, ninguno es `tests/test_inventario.py`. `pytest -v`: 28 passed. `ruff check .`: All checks passed. Luego se integró a `main` con `git merge --no-ff`. | rama `agente/revision-s6` |

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
corregir: así cada hallazgo queda demostrado y no solo copiado. Aplicar las correcciones en otra rama y
revisar el diff por commits pequeños fue más fácil que revisar un solo cambio grande.

---

# Semana 7: suite de pruebas con técnicas formales

Asistente: Claude (Claude Code). Registro completo: [docs/07_plan_pruebas_S7.md](docs/07_plan_pruebas_S7.md).

| # | Fecha | Sugerencia o prompt | Decisión | Razón | Cómo lo verifiqué | Commit |
|---|---|---|---|---|---|---|
| 13 | 2026-11-22 | Le di las reglas de `registrar_salida`, `registrar_entrada`, `calcular_ganancia` y `estado_stock` y le pedí particiones, límites y una tabla de decisión. | Aceptada | Los casos tenían sentido y me sirvieron para ver ambigüedades, como qué hacer con cantidades decimales en la entrada. | Revisé cada esperado contra la regla, no contra el código. | cdccda9 |
| 14 | 2026-11-22 | Le pedí generar `tests/test_reglas.py` desde las tablas, con `parametrize` y `pytest.raises`. La primera versión dio `44 passed`. | Ajustada | Había pruebas repetidas de la semana 5, una prueba débil con `isinstance` y un comentario por cada fila. Las quité. | `pytest -v` y rompí el código 4 veces. | 9a4349e |
| 15 | 2026-11-27 | Al revisar contra el documento de requisitos final me di cuenta de que `calcular_ganancia` y `estado_stock` no están en el alcance: la app solo registra lo que se vende. Le pedí cambiarlas por `eliminar_producto` (HU-04) y `reporte_mensual` (HU-10) y acortar los docstrings. | Ajustada | Revisé que el mensaje de error de HU-04 y el ejemplo del reporte (total 790000) fueran los mismos del documento. Dejé `_validar_stock_suficiente` separada porque así quedó en la revisión de la semana 6. | `pytest -v`: 55 passed. `ruff check .`: sin avisos. Las pruebas de las semanas 5 y 6 siguen pasando. | 92c4c3f |
| 16 | 2026-11-27 | Rompí el código 4 veces para ver si las pruebas nuevas lo detectan. | Aceptada | En las 4 falló al menos una prueba. En la (b) vi que las pruebas de octubre y diciembre no lo detectaban porque esas ventas eran de 1 unidad; la de noviembre sí. | Tabla de la sección 3 del registro. Al devolver el código: 55 passed. | 92c4c3f |
| 17 | 2026-11-27 | Los datos de prueba (productos con ñ, apóstrofo, nombre vacío, precio 0 y un producto eliminado, y ventas en los bordes del mes) los propuso la IA. | Ajustada | Quité el producto con margen negativo porque ya no hay ganancia. Agregué ventas el 31 de octubre y el 1 de diciembre para probar los bordes del mes. | No hay datos reales del negocio ni de personas. | 92c4c3f |

## Reflexión de la semana 7

Que todas las pruebas pasen no quiere decir que estén bien. La primera versión tenía pruebas repetidas
y otras que pasaban con cualquier valor. Lo que más me sirvió fue romper el código a propósito, porque
ahí se ve si una prueba sirve o no. También aprendí que hay que comparar las pruebas con los requisitos
y no solo con el código: tenía pruebas muy completas de una ganancia que el cliente nunca pidió.

---

# Entrega final: app web, despliegue y operación (semanas 8 a 10)

Asistente: Claude (Claude Code), como herramienta para escribir código más rápido. Yo definí qué
tenía que hacer la app a partir de mis documentos de requisitos y diseño, revisé cada cambio, probé la
app en mi portátil como la usaría mi primo y corregí lo que no servía. Rama: `entrega-final`.

| # | Fecha | Sugerencia o prompt | Decisión | Razón | Cómo lo verifiqué | Commit |
|---|---|---|---|---|---|---|
| 18 | 2026-11-27 | Organicé los documentos de cada semana en `docs/` y armé la guía de despliegue y el plan de operación con apoyo del asistente. | Ajustada | El asistente había puesto unos PDF de la semana 1 que no eran los que entregué. Los cambié por mis dos archivos originales, sin modificarlos. | Abrí cada documento desde la tabla del README. | ef35864, efd51b0, 7290f7d |
| 19 | 2026-11-27 | Escribí primero las pruebas de la app con los dos escenarios de cada historia de mi documento de requisitos y después la app con Flask y SQLite, usando el asistente para generar el código. | Aceptada | Así cada historia queda comprobada con los mismos datos y mensajes del documento. | Las pruebas fallaron antes de que existiera la app. Después: `83 passed`. La instalé con `instalar.bat` y la abrí con `iniciar.bat` en mi portátil. | dd7b858, a357b4d |
| 20 | 2026-11-27 | La primera versión tenía una pestaña aparte, «Mercancía», solo para sumar unidades. | Ajustada | Al probarla vi que esa pantalla sobraba. La quité y puse «Agregar unidades» dentro de Productos. | Agregué unidades a un producto y revisé que el stock subiera. | 8d08656 |
| 21 | 2026-11-27 | El código generado pedía precio de compra al crear un producto y costo al agregar unidades. | Rechazada | Detecté que esos datos solo servían para calcular la ganancia, que yo ya había sacado del alcance. Los quité de la app y dejé la explicación en el README, porque los documentos S3 y S4 ya estaban entregados. | `pytest`: 84 passed. Volví a crear productos y solo pedía nombre, precio de venta y cantidad. | 969c9b1 |
| 22 | 2026-11-27 | El diseño generado era muy básico: colores fuertes, el «Volver» suelto abajo y un reporte que era solo una tabla con un número. | Ajustada | Cambié el diseño a colores sobrios, sin emojis, con botones con estilo, y al reporte le agregué gráficas y el detalle de cada venta. | Revisé cada pantalla en el navegador con datos de ejemplo. `85 passed`. | f4fdb47 |
| 23 | 2026-11-27 | Antes de subir, revisé con el asistente que nada del código contradijera mis documentos de requisitos y diseño. | Aceptada | Aparecieron dos mensajes de error que no decían exactamente lo mismo que el documento (HU-03 y HU-05/HU-08). Los dejé iguales. | Las pruebas ahora comparan el mensaje palabra por palabra. `85 passed`. | 04f3a20 |
| 24 | 2026-11-27 | Quité los comentarios del código y lo simplifiqué. La explicación de cada línea la dejé en un documento aparte para estudiarla. | Aceptada | Quería un código limpio que yo pudiera explicar en la sustentación. | `85 passed`, `ruff check .` sin avisos, y volví a probar vender, corregir y eliminar. | 921e0f2 |
| 25 | 2026-11-27 | El pipeline de GitHub Actions salió en verde pero con dos advertencias de que una versión de Node.js iba a dejar de funcionar. | Aceptada | Vi las advertencias en la pestaña Actions y actualicé las dos acciones a la versión nueva. | La siguiente ejecución del pipeline. | ff9b5c3, c0c4cff |

## Resumen de la entrega final

| Decisión | Entradas |
|---|---|
| Aceptadas | 19, 23, 24, 25 |
| Aceptadas con cambios (ajustadas) | 18, 20, 22 |
| Rechazadas | 21 |

## Errores que atraparon las pruebas (entrega final)

- Antes de escribir la app, las pruebas de `tests/test_app.py` fallaban todas: así sé que de verdad prueban algo.
- Al quitar el precio de compra, las pruebas mostraron todo lo que había que cambiar para que la app siguiera haciendo lo mismo.
- Al cambiar los mensajes, las pruebas de HU-03, HU-05 y HU-08 confirmaron que dicen lo mismo que el documento.

## Reflexión de la entrega final

Lo que más me sirvió fue usar la app yo mismo antes de darla por terminada. Las pruebas pasaban, pero
fue al usarla que encontré un precio de compra que no servía para nada y una pestaña de más. El
asistente escribe rápido, pero no conoce a mi primo ni cómo trabaja; eso lo tuve que decidir yo.
También aprendí que cuando se cambia el alcance hay que revisar todo lo que dependía de lo que se
quitó, no solo la función principal. Y dejar la explicación de cada línea aparte me obligó a entender
el código antes de sustentarlo.
