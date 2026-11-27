# Registro de pruebas

Proyecto: CRUD R2K
Estudiante: Sergio Alejandro Vargas
Fecha: 2026-11-22, corregido el 2026-11-27

Las pruebas de esta semana están en `tests/test_reglas.py` y los datos en `tests/conftest.py`
(fixtures `catalogo` y `ventas`). Las de las semanas 5 y 6 (`test_inventario.py` y `test_abuso.py`)
siguen igual y también cuentan para `registrar_salida`.

**Corrección del 27 de noviembre:** la primera versión probaba `calcular_ganancia` y `estado_stock`.
Las quité porque en el documento de requisitos final (S3) la app no calcula ganancia ni maneja stock
mínimo. En su lugar probé `eliminar_producto` (HU-04) y `reporte_mensual` (HU-10), que sí están en
los requisitos.

## 1. Tabla de casos

### registrar_salida (HU-06)

**Regla:** la cantidad tiene que ser un entero de 1 o más, si no `CantidadInvalidaError`. Si es mayor
que el stock, `StockInsuficienteError` con el nombre del producto. Si el producto no existe o está
eliminado, `ProductoNoEncontradoError`. Si todo está bien descuenta y devuelve el stock nuevo. Si hay
error el stock no cambia.

| Técnica | Caso | Entrada | Esperado | Prueba |
|---|---|---|---|---|
| Partición válida | Venta normal | stock 10, cantidad 3 | 7 | test_inventario.py::test_venta_normal_descuenta_el_stock |
| Límite | Cantidad mínima | stock 5, cantidad 1 | 4 | test_inventario.py::test_venta_de_una_unidad_descuenta_uno |
| Límite | Cantidad 0 | cantidad 0 | CantidadInvalidaError | test_inventario.py::test_cantidad_cero_o_negativa_lanza_error[0] |
| Partición inválida | Negativa | cantidad -1 | CantidadInvalidaError | test_inventario.py::test_cantidad_cero_o_negativa_lanza_error[-1] |
| Partición inválida | No es entero | 2.5, True, "3", None | CantidadInvalidaError | test_abuso.py::test_cantidad_que_no_es_entero_se_rechaza_y_no_cambia_el_stock |
| Límite | Vender todo | stock 5, cantidad 5 | 0 | test_inventario.py::test_vender_todo_el_stock_lo_deja_en_cero |
| Límite | Una más que el stock | stock 5, cantidad 6 | StockInsuficienteError | test_inventario.py::test_vender_una_unidad_mas_que_el_stock_falla |
| Partición inválida | Agotado | stock 0, cantidad 1 | StockInsuficienteError, stock 0 | test_vender_producto_agotado_falla |
| Partición inválida | No existe | id 99 | ProductoNoEncontradoError | test_inventario.py::test_producto_inexistente_lanza_error |
| Partición inválida | Eliminado | id 6 (activo=False) | ProductoNoEncontradoError | test_no_se_puede_vender_un_producto_eliminado |
| Dato difícil | Ñ y tilde en el mensaje | "Guantes Ñandú", cantidad 6 | mensaje con "Guantes Ñandú" | test_mensaje_de_stock_insuficiente_con_enie |

### registrar_entrada (HU-05)

**Regla:** suma la cantidad al stock y devuelve el stock nuevo. La cantidad tiene que ser un entero de
1 o más. El producto tiene que existir y estar activo. Si hay error no cambia ningún stock.

| Técnica | Caso | Entrada | Esperado | Prueba |
|---|---|---|---|---|
| Límite | Cantidad mínima | stock 5, cantidad 1 | 6 | test_entrada_suma_al_stock[1-1-6] |
| Partición válida | Entrada normal | stock 10, cantidad 15 | 25 | test_entrada_suma_al_stock[2-15-25] |
| Partición válida | Producto agotado | stock 0, cantidad 4 | 4 | test_entrada_suma_al_stock[3-4-4] |
| Partición válida | Mucha cantidad | stock 10, cantidad 1000 | 1010 | test_entrada_suma_al_stock[2-1000-1010] |
| Límite | Cantidad 0 | cantidad 0 | CantidadInvalidaError | test_entrada_invalida_no_cambia_el_stock[1-0-...] |
| Partición inválida | Negativa | cantidad -5 | CantidadInvalidaError | test_entrada_invalida_no_cambia_el_stock[1--5-...] |
| Partición inválida | Decimal | cantidad 2.5 | CantidadInvalidaError | test_entrada_invalida_no_cambia_el_stock[1-2.5-...] |
| Partición inválida | No existe | id 99 | ProductoNoEncontradoError | test_entrada_invalida_no_cambia_el_stock[99-3-...] |
| Partición inválida | Eliminado | id 6 | ProductoNoEncontradoError | test_entrada_invalida_no_cambia_el_stock[6-3-...] |

**Ambigüedad:** la regla no decía si se acepta una cantidad decimal. La rechacé igual que en la venta.

### eliminar_producto (HU-04), función con varias condiciones

**Regla:** solo se puede eliminar si el producto existe, está activo y tiene stock 0. No se borra:
queda con `activo = False` para que sus ventas sigan saliendo en el reporte. Si tiene stock, sale
`ProductoConStockError` con «No se puede eliminar: todavía tiene N unidades en stock».

| Técnica | Caso | Entrada | Esperado | Prueba |
|---|---|---|---|---|
| Límite | Stock 0 | id 3, stock 0 | activo = False y sigue en el catálogo | test_eliminar_producto_con_stock_cero |
| Límite | Stock 1 | id 4, stock 1 | ProductoConStockError "tiene 1 unidades" | test_eliminar_producto_con_una_unidad_falla |
| Partición inválida | Con stock | id 1, stock 5 | ProductoConStockError, sigue activo | test_eliminar_producto_con_stock_falla |
| Partición inválida | No existe | id 99 | ProductoNoEncontradoError | test_eliminar_producto_que_no_existe_o_ya_se_elimino[99] |
| Partición inválida | Ya eliminado | id 6 | ProductoNoEncontradoError | test_eliminar_producto_que_no_existe_o_ya_se_elimino[6] |

**Tabla de decisión.** C1 = el producto existe, C2 = está activo, C3 = stock es 0. «-» = no importa.

| Regla | C1 | C2 | C3 | Resultado | Prueba |
|---|---|---|---|---|---|
| R1 | No | - | - | ProductoNoEncontradoError | test_eliminar_producto_que_no_existe_o_ya_se_elimino[99] |
| R2 | Sí | No | - | ProductoNoEncontradoError | test_eliminar_producto_que_no_existe_o_ya_se_elimino[6] |
| R3 | Sí | Sí | No | ProductoConStockError | test_eliminar_producto_con_stock_falla, test_eliminar_producto_con_una_unidad_falla |
| R4 | Sí | Sí | Sí | activo = False | test_eliminar_producto_con_stock_cero |

**Ambigüedad:** ¿un producto eliminado se puede volver a eliminar? Decidí que no: se trata igual que
uno que no existe.

### reporte_mensual (HU-10)

**Regla:** recibe las ventas `(fecha, nombre, cantidad, precio_unitario)` y un mes `"AAAA-MM"`. Devuelve
cada producto vendido en ese mes con su cantidad y valor (cantidad × precio), y el total vendido. Si el
mes no tiene esa forma o el mes no está entre 01 y 12, `ValueError`. Sin ventas, lista vacía y total 0.

| Técnica | Caso | Entrada | Esperado | Prueba |
|---|---|---|---|---|
| Partición válida | Ejemplo de la HU-10 | ventas, "2026-11" | Casco 3 $540.000, Guantes 5 $200.000, Espejo 2 $50.000, total 790000 | test_reporte_de_noviembre |
| Límite | Último día del mes anterior | venta del 2026-10-31 | no entra en noviembre, sí en octubre (180000) | test_reporte_de_noviembre, test_reporte_solo_cuenta_las_ventas_del_mes[2026-10-180000] |
| Límite | Primer día del mes siguiente | venta del 2026-12-01 | no entra en noviembre, sí en diciembre (40000) | test_reporte_solo_cuenta_las_ventas_del_mes[2026-12-40000] |
| Límite | Mes 01 sin ventas | "2026-01" | total 0 | test_reporte_solo_cuenta_las_ventas_del_mes[2026-01-0] |
| Límite | Lista vacía | [] | productos [] y total 0 | test_reporte_sin_ventas |
| Límite | Mes 00 | "2026-00" | ValueError | test_reporte_con_mes_invalido[2026-00] |
| Límite | Mes 13 | "2026-13" | ValueError | test_reporte_con_mes_invalido[2026-13] |
| Partición inválida | Mes sin cero | "2026-1" | ValueError | test_reporte_con_mes_invalido[2026-1] |
| Partición inválida | Texto o None | "noviembre", None | ValueError | test_reporte_con_mes_invalido[noviembre], [None] |

Los primeros días (2026-11-01) y últimos (2026-11-30) de noviembre están en la fixture `ventas` y entran
en el reporte de noviembre.

## 2. Pruebas de la IA descartadas o corregidas

Le pedí a Claude que escribiera las pruebas desde estas tablas con `parametrize`, `pytest.raises` con el
tipo de error y esperados fijos. Después revisé cada una contra la regla (ver bitácora, entradas 13 a 16).

| Prueba | Decisión | Por qué |
|---|---|---|
| Casos de venta normal, cantidad 0 y producto inexistente en `test_reglas.py` | Descartadas | Repetían las de la semana 5. Las cito en la tabla |
| Entrada inválida que solo revisaba el error | Corregida | No revisaba que el stock siguiera igual. Ahora compara todos los stocks antes y después |
| Nombres difíciles en la entrada | Descartada | `registrar_entrada` no usa el nombre, así que no probaba nada. Los nombres se prueban en el mensaje de error de la venta |
| Todas las de `calcular_ganancia` y `estado_stock` | Descartadas | El alcance final (S3) no tiene ganancia ni stock mínimo |
| Un comentario por cada fila del `parametrize` y `ids` largos | Corregida | Sobraban; la explicación de cada caso está en este registro |

## 3. Romper el código a propósito

Cada cambio se hizo solo en `src/r2k/inventario.py`, se corrió `pytest -q` y se devolvió el archivo.

| Cambio | Línea | Qué falló | Qué hice |
|---|---|---|---|
| (a) En eliminar_producto, `> 0` por `> 1` | 115 | 1 failed: test_eliminar_producto_con_una_unidad_falla | Nada, el borde de 1 unidad está cubierto |
| (b) En reporte_mensual, sumar `precio` en vez de `cantidad * precio` | 138 | 1 failed: test_reporte_de_noviembre | Me di cuenta de que las pruebas de octubre y diciembre no lo atrapan porque esas ventas son de 1 unidad. Lo deja cubierto la de noviembre |
| (c) Aceptar cualquier mes de dos dígitos (`\d{2}`) | 129 | 2 failed: test_reporte_con_mes_invalido[2026-00] y [2026-13] | Nada |
| (d) Quitar la revisión de `activo` al buscar el producto | 65 | 3 failed: test_no_se_puede_vender_un_producto_eliminado, test_entrada_invalida_no_cambia_el_stock[6-3-...], test_eliminar_producto_que_no_existe_o_ya_se_elimino[6] | Nada |

Al devolver el archivo: `55 passed`.

## 4. Datos de prueba

Sintéticos, inventados con ayuda de la IA y revisados por mí. No son las cuentas reales de R2K ni hay
datos de personas. Incluyen ñ y tilde ("Guantes Ñandú"), apóstrofo ("Casco D'Angelo"), nombre vacío,
precio 0, stock 0, un producto ya eliminado y ventas en el primer y último día del mes.
