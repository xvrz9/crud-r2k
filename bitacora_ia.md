# Bitácora de uso de IA: CRUD R2K, semana 5

Asistente: Claude (Claude Code en VS Code).

| # | Fecha | Sugerencia o prompt | Decisión | Razón | Cómo lo verifiqué |
|---|---|---|---|---|---|
| 1 | 2026-11-07 | En el ejercicio de clase `productos_por_pedir`, la IA propuso validar existencias y mínimos negativos **antes** de filtrar la lista. | Aceptada | Si se valida después de filtrar, un producto con mínimo negativo se descarta y el error nunca salta. Apliqué la misma idea en `registrar_salida`: validar todo antes de descontar. | Los tests de error del docente pasaron. En R2K, `test_stock_insuficiente_no_cambia_el_stock` lo comprueba. |
| 2 | 2026-11-07 | Le pedí "mejora el output". La IA lo interpretó como mejores mensajes de error y reescribió la validación. | Ajustada | Yo quería una tabla legible en consola. Le aclaré y agregó `formatear_tabla` sin tocar la lógica. | Ejecuté `python implementacion.py`, vi la tabla y los 6 tests seguían pasando. |
| 3 | 2026-11-07 | Para el ejercicio de abonos, la IA intentó ejecutar el script con un comando en la terminal. | Rechazada | No quería que corriera comandos sin que yo lo pidiera. Primero quería ver el código y que la tabla mostrara el mensaje de error. | Revisé el archivo y lo ejecuté yo con `python abonos.py`. |
| 4 | 2026-11-07 | La IA propuso la HU "Registrar venta y descontar stock" (HU-06 en el documento de requisitos) con la firma `registrar_salida(productos, id_producto, cantidad) -> int`. | Aceptada | Sale del modelo de datos del Diseño S4, §5 (Producto con `stock_actual`) y cumple el objetivo de controlar lo que se vende. | Comparé los atributos de `Producto` con la tabla del Diseño S4. |
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
