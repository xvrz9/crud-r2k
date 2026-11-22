# Registro de pruebas: tabla de casos y pruebas de la IA

Proyecto: CRUD R2K
Estudiante: Sergio Alejandro Vargas
Fecha: 2026-11-22

Las pruebas nuevas están en `tests/test_reglas.py` y los datos en `tests/conftest.py` (fixture `catalogo`).
Cuando una prueba está en otro archivo, el id lleva el nombre del archivo. Las pruebas de las semanas 5 y 6
(`test_inventario.py` y `test_abuso.py`) no se modificaron.

## 1. Tabla de casos

### Regla: registrar_salida descuenta del stock las unidades vendidas (HU-02)

**Regla completa (el oráculo):** al registrar una venta, la cantidad debe ser un entero mayor o igual a 1;
si no, `CantidadInvalidaError`. Si la cantidad es mayor que el stock, `StockInsuficienteError` con el nombre
del producto en el mensaje. Si el producto no existe, `ProductoNoEncontradoError`. Si todo está bien,
descuenta la cantidad y devuelve el nuevo stock. Si hay cualquier error, el stock no cambia.

| Técnica | Partición o límite | Entrada | Esperado | Prueba que lo cubre |
|---|---|---|---|---|
| Partición válida | 1 <= cantidad <= stock | stock 10, cantidad 3 | 7 | test_inventario.py::test_venta_normal_descuenta_el_stock |
| Límite | Cantidad mínima válida | stock 5, cantidad 1 | 4 | test_inventario.py::test_venta_de_una_unidad_descuenta_uno |
| Límite | Último valor inválido antes del mínimo | cantidad 0 | CantidadInvalidaError, stock 10 | test_inventario.py::test_cantidad_cero_o_negativa_lanza_error[0] |
| Partición inválida | Cantidad negativa | cantidad -1 | CantidadInvalidaError, stock 10 | test_inventario.py::test_cantidad_cero_o_negativa_lanza_error[-1] |
| Partición inválida | Cantidad que no es entero | 2.5, nan, True, "3", None | CantidadInvalidaError, stock 10 | test_abuso.py::test_cantidad_que_no_es_entero_se_rechaza_y_no_cambia_el_stock[decimal] (y los demás ids) |
| Límite | Vender exactamente el stock | stock 5, cantidad 5 | 0 | test_inventario.py::test_vender_todo_el_stock_lo_deja_en_cero |
| Límite | Una unidad más que el stock | stock 5, cantidad 6 | StockInsuficienteError | test_inventario.py::test_vender_una_unidad_mas_que_el_stock_falla |
| Partición inválida | Cantidad mayor que el stock | stock 5, cantidad 8 | StockInsuficienteError, stock 5 | test_inventario.py::test_stock_insuficiente_no_cambia_el_stock |
| Partición inválida | Producto agotado | stock 0, cantidad 1 | StockInsuficienteError, stock 0 | test_vender_producto_agotado_falla_y_el_stock_sigue_en_cero |
| Partición inválida | Producto inexistente | id 99 | ProductoNoEncontradoError | test_inventario.py::test_producto_inexistente_lanza_error |
| Dato difícil | Nombre con ñ y tilde en el mensaje | "Guantes Ñandú", stock 5, cantidad 6 | StockInsuficienteError con "Guantes Ñandú" | test_mensaje_de_stock_insuficiente_conserva_la_enie |

**Ambigüedades encontradas:** ninguna nueva. Las de la semana 6 (cantidad no entera) ya están resueltas
en `test_abuso.py`.

### Regla: registrar_entrada suma al stock la mercancía que llega

**Regla completa (el oráculo):** `registrar_entrada(productos, id_producto, cantidad)` suma la cantidad al
stock y devuelve el nuevo stock. La cantidad debe ser mayor o igual a 1; si no, `CantidadInvalidaError`.
Si el producto no existe, `ProductoNoEncontradoError`.

| Técnica | Partición o límite | Entrada | Esperado | Prueba que lo cubre |
|---|---|---|---|---|
| Límite | Cantidad mínima válida | stock 5, cantidad 1 | 6 | test_registrar_entrada_suma_al_stock[limite_cantidad_uno] |
| Límite | Último valor inválido antes del mínimo | cantidad 0 | CantidadInvalidaError, stock sin cambios | test_registrar_entrada_invalida_no_cambia_el_stock[limite_cantidad_cero] |
| Partición válida | Cantidad >= 1 | stock 10, cantidad 15 | 25 | test_registrar_entrada_suma_al_stock[entrada_normal] |
| Partición válida | Producto con stock 0 | stock 0, cantidad 4 | 4 | test_registrar_entrada_suma_al_stock[reabastece_agotado] |
| Partición válida | Volumen grande | stock 10, cantidad 1000 | 1010 | test_registrar_entrada_suma_al_stock[volumen] |
| Partición válida | El nuevo stock queda guardado | stock 5, cantidad 2 | stock_actual 7 | test_registrar_entrada_guarda_el_stock_en_el_producto |
| Partición inválida | Cantidad negativa | cantidad -5 | CantidadInvalidaError, stock sin cambios | test_registrar_entrada_invalida_no_cambia_el_stock[cantidad_negativa] |
| Partición inválida | Cantidad decimal | cantidad 2.5 | CantidadInvalidaError, stock sin cambios | test_registrar_entrada_invalida_no_cambia_el_stock[cantidad_decimal] |
| Partición inválida | Cantidad bool | cantidad True | CantidadInvalidaError, stock sin cambios | test_registrar_entrada_invalida_no_cambia_el_stock[cantidad_bool] |
| Partición inválida | Producto inexistente | id 99 | ProductoNoEncontradoError, ningún stock cambia | test_registrar_entrada_invalida_no_cambia_el_stock[producto_inexistente] |

**Ambigüedades encontradas:**
- La regla no decía qué pasa con una cantidad que no es entera. Decidí rechazarla con `CantidadInvalidaError`,
  igual que en `registrar_salida`, y agregué los casos `cantidad_decimal` y `cantidad_bool`.
- La regla no decía si el stock cambia cuando hay un error. Se aplica lo mismo que en la venta: no cambia.

### Regla: calcular_ganancia suma el margen de las ventas

**Regla completa (el oráculo):** `calcular_ganancia(ventas, productos)` recibe una lista de
`(id_producto, cantidad)`. Ganancia = suma de `(precio_venta - precio_compra) * cantidad`. Lista vacía da 0.
Producto inexistente da `ProductoNoEncontradoError`; cantidad menor que 1 da `CantidadInvalidaError`.

| Técnica | Partición o límite | Entrada | Esperado | Prueba que lo cubre |
|---|---|---|---|---|
| Límite | Lista vacía | [] | 0 | test_calcular_ganancia[vacia] |
| Límite | Cantidad mínima válida | Guantes Ñandú (25.000 / 40.000) x 1 | 15000 | test_calcular_ganancia[una_unidad] |
| Límite | Último valor inválido antes del mínimo | [(1, 0)] | CantidadInvalidaError | test_calcular_ganancia_invalida[limite_cantidad_cero] |
| Partición válida | Una venta de varias unidades | Casco D'Angelo (120.000 / 180.000) x 2 | 120000 | test_calcular_ganancia[dos_cascos] |
| Partición válida | Varias ventas | [(1, 2), (2, 1), (4, 3)] | 30.000 + 60.000 + 12.000 = 102000 | test_calcular_ganancia[varias] |
| Partición válida | Precio 0 | Calcomanía (0 / 0) x 10 | 0 | test_calcular_ganancia[precio_cero] |
| Partición válida | Margen 0 | Llavero (5.000 / 5.000) x 3 | 0 | test_calcular_ganancia[margen_cero] |
| Partición válida | Venta a pérdida | Visor (30.000 / 20.000) x 2 | -20000 | test_calcular_ganancia[perdida] |
| Partición válida | La pérdida resta a la ganancia | [(1, 1), (7, 2)] | 15.000 - 20.000 = -5000 | test_calcular_ganancia[perdida_resta_a_la_ganancia] |
| Partición válida | El resultado es entero, no float | [(1, 1)] | 15000 y tipo int | test_calcular_ganancia_devuelve_entero_y_no_float |
| Partición válida | No modifica el stock | [(1, 2), (2, 1)] | todos los stocks igual | test_calcular_ganancia_no_cambia_el_stock |
| Partición inválida | Cantidad negativa | [(1, -2)] | CantidadInvalidaError | test_calcular_ganancia_invalida[cantidad_negativa] |
| Partición inválida | Producto inexistente | [(99, 1)] | ProductoNoEncontradoError | test_calcular_ganancia_invalida[inexistente] |
| Partición inválida | Error en la segunda venta | [(1, 1), (99, 1)] | ProductoNoEncontradoError | test_calcular_ganancia_invalida[error_en_segunda] |

**Ambigüedades encontradas:**
- A-1. La regla no decía si calcular la ganancia descuenta stock. Decidí que no: la venta se registra con
  `registrar_salida` y esta función solo calcula.
- A-2. Si `precio_venta < precio_compra`, la fórmula da negativo. Decidí aceptarlo: si el negocio vende a
  pérdida, se tiene que ver en el resultado. Agregué un producto en liquidación a los datos.
- No hay decimales: el dinero va en enteros de pesos, por eso no uso `pytest.approx` y comparo con `==`.
  Como `15000 == 15000.0` es True en Python, agregué una prueba que revisa que el tipo sea `int`.

### Regla: estado_stock clasifica el stock como agotado, bajo u ok

**Regla completa (el oráculo):** `estado_stock(stock_actual, minimo)` devuelve "agotado" si el stock es 0;
"bajo" si 0 < stock <= minimo; "ok" si stock > minimo. Si stock < 0 o minimo < 0, `ValueError`.

| Técnica | Partición o límite | Entrada | Esperado | Prueba que lo cubre |
|---|---|---|---|---|
| Límite | Último valor inválido de stock | stock -1, minimo 3 | ValueError | test_estado_stock_negativo_lanza_value_error[-1-3] |
| Límite | Primer valor válido de stock | stock 0, minimo 3 | "agotado" | test_estado_stock[0-3-agotado] |
| Límite | Primer valor de "bajo" | stock 1, minimo 3 | "bajo" | test_estado_stock[1-3-bajo] |
| Límite | Último valor de "bajo" | stock 3, minimo 3 | "bajo" | test_estado_stock[3-3-bajo] |
| Límite | Primer valor de "ok" | stock 4, minimo 3 | "ok" | test_estado_stock[4-3-ok] |
| Partición válida | Stock muy por encima del mínimo | stock 50, minimo 3 | "ok" | test_estado_stock[50-3-ok] |
| Límite | Último valor inválido de minimo | stock 3, minimo -1 | ValueError | test_estado_stock_negativo_lanza_value_error[3--1] |
| Límite | Primer valor válido de minimo, stock 0 | stock 0, minimo 0 | "agotado" | test_estado_stock[0-0-agotado] |
| Límite | Primer valor válido de minimo, stock 1 | stock 1, minimo 0 | "ok" | test_estado_stock[1-0-ok] |
| Partición inválida | Los dos negativos | stock -1, minimo -1 | ValueError | test_estado_stock_negativo_lanza_value_error[-1--1] |

**Ambigüedades encontradas:**
- P-01. El cliente todavía no definió el umbral real de stock bajo. Por eso `minimo` es un parámetro y las
  pruebas usan 3 y 0.
- Con minimo 0 y stock 0, la regla cumple "agotado" (stock == 0) y también "stock <= minimo". Decidí que
  "agotado" tiene prioridad.

**Tabla de decisión:**

Condiciones: C1 = stock < 0 o minimo < 0; C2 = stock == 0; C3 = stock <= minimo. «-» significa que no importa.

| Regla | C1 | C2 | C3 | Resultado | Prueba que lo cubre |
|---|---|---|---|---|---|
| R1 | Sí | - | - | ValueError | test_estado_stock_negativo_lanza_value_error[-1-3], [3--1], [-1--1] |
| R2 | No | Sí | - | "agotado" | test_estado_stock[0-3-agotado], test_estado_stock[0-0-agotado] |
| R3 | No | No | Sí | "bajo" | test_estado_stock[1-3-bajo], test_estado_stock[3-3-bajo] |
| R4 | No | No | No | "ok" | test_estado_stock[4-3-ok], test_estado_stock[50-3-ok], test_estado_stock[1-0-ok] |

Las 8 combinaciones quedan en 4 reglas: con C1 = Sí, C2 y C3 no importan (4 combinaciones en R1). Con
C1 = No y C2 = Sí, C3 siempre es Sí porque minimo >= 0, así que la combinación (No, Sí, No) no puede ocurrir
y R2 junta 2 combinaciones.

## 2. Pruebas de la IA descartadas o corregidas

**Prompt usado:** le pedí al asistente que generara `tests/test_reglas.py` a partir de las reglas y tablas
de la sección 1, con `@pytest.mark.parametrize` y un comentario por fila, `pytest.raises` con el error
exacto, esperados fijos y los datos en una fixture de `tests/conftest.py`. Ver la entrada 14 de
[bitacora_ia.md](bitacora_ia.md). La primera versión tenía 44 casos (`44 passed`).

| Prueba generada | Decisión | Por qué | En su lugar |
|---|---|---|---|
| test_registrar_salida_valida[1-1-4], [1-5-0], [2-3-7] | Descartada | Redundante: mismos valores que tres pruebas de `test_inventario.py` | Cito esas pruebas en la sección 1 |
| test_registrar_salida_invalida[1-0-…], [1-6-…], [99-1-…] | Descartada | Redundante con `test_inventario.py` y no revisaba que el stock no cambie | Cito las pruebas existentes |
| test_registrar_salida_invalida[3-1-StockInsuficienteError] | Corregida | El caso del producto agotado es nuevo, pero no revisaba el stock después del error | test_vender_producto_agotado_falla_y_el_stock_sigue_en_cero, con `assert stock_actual == 0` |
| test_registrar_entrada_invalida[…] | Corregida | Débil: solo revisaba el error, no que el stock quedara igual. Un código que sume antes de validar pasaba | test_registrar_entrada_invalida_no_cambia_el_stock, compara todos los stocks antes y después. Agregué cantidad_decimal y cantidad_bool |
| test_nombres_dificiles_no_rompen_la_entrada[1..4] | Descartada | `registrar_entrada` no usa el nombre, así que no probaba los nombres. El esperado se calculaba y repetía la suma de otra prueba | Los nombres difíciles se prueban en el mensaje: test_mensaje_de_stock_insuficiente_conserva_la_enie |
| test_calcular_ganancia_coincide_con_la_formula | Descartada | El esperado se calculaba con la misma fórmula del código, y repetía test_calcular_ganancia[varias] | Nada: [varias] tiene el esperado escrito a mano |
| test_calcular_ganancia_devuelve_entero (`isinstance`) | Corregida | Débil: pasa con cualquier entero | test_calcular_ganancia_devuelve_entero_y_no_float: revisa el valor 15000 y `type(...) is int` |
| test_estado_stock_devuelve_texto (`isinstance str`) | Descartada | Débil y redundante: los `==` de test_estado_stock ya exigen el texto exacto | Nada |
| test_calcular_ganancia_no_cambia_el_stock | Conservada | El esperado salía de la documentación del código, no de la regla. Lo resolví con la ambigüedad A-1 | Ahora compara todos los stocks |
| Comentarios por fila en todas las pruebas | Corregida | Decidí dejar el código sin comentarios; la explicación de cada caso está en este registro | Cada fila tiene un `id` que dice qué caso es |

Conservadas sin cambios: test_mensaje_de_stock_insuficiente_conserva_la_enie, test_registrar_entrada_suma_al_stock,
test_registrar_entrada_guarda_el_stock_en_el_producto, test_calcular_ganancia, test_calcular_ganancia_invalida,
test_estado_stock y test_estado_stock_negativo_lanza_value_error. Agregué los casos perdida y
perdida_resta_a_la_ganancia por la ambigüedad A-2. Versión final: 36 casos en `test_reglas.py`, 64 en toda la suite.

## 3. Romper el código a propósito

Cada cambio se hizo solo, se corrió `pytest -v` y después `git restore src/r2k/inventario.py`.

| Cambio introducido | Archivo y línea | ¿Alguna prueba falló? | Qué hice |
|---|---|---|---|
| (a) En estado_stock, `<=` por `<` | inventario.py:256 | Sí, 1 failed: test_estado_stock[3-3-bajo] | Nada: la suite protege el borde stock == minimo |
| (b) En calcular_ganancia, `precio_venta` en vez de la resta | inventario.py:227 | Sí, 7 failed: test_calcular_ganancia[una_unidad], [dos_cascos], [margen_cero], [varias], [perdida], [perdida_resta_a_la_ganancia] y test_calcular_ganancia_devuelve_entero_y_no_float | Nada. [vacia] y [precio_cero] pasan, porque con precio 0 las dos fórmulas dan lo mismo |
| (c) registrar_entrada devuelve el stock original | inventario.py:199-200 | Sí, 4 failed: test_registrar_entrada_suma_al_stock[limite_cantidad_uno], [entrada_normal], [reabastece_agotado], [volumen] | Nada. test_registrar_entrada_guarda_el_stock_en_el_producto pasa porque el stock sí se guarda; esa prueba cubre otro error |
| (d) registrar_entrada suma antes de validar la cantidad | inventario.py:198-199 | Sí, 3 failed: test_registrar_entrada_invalida_no_cambia_el_stock[cantidad_negativa], [cantidad_decimal], [cantidad_bool] | Nada. Este error es el que la prueba corregida en la sección 2 ahora atrapa. [limite_cantidad_cero] pasa porque sumar 0 no cambia el stock |

En el primer intento de (c), el comando de edición no cambió el `return` y la suite dio `64 passed`. Revisé el
archivo, vi que el cambio no estaba, lo repetí bien y ahí salieron los 4 fallos. Después de cada restauración
la suite volvió a `64 passed`.

## 4. Datos de prueba

**Origen:** sintéticos, generados con IA y revisados por mí, en la fixture `catalogo` de `tests/conftest.py`.
Confirmo que no hay datos de personas reales. El modelo `Producto` no tiene teléfonos ni datos de contacto,
así que no se usaron.

**Casos difíciles incluidos:** ñ y tilde ("Guantes Ñandú"), apóstrofo ("Casco D'Angelo"), tilde en un
nombre de varias palabras ("Impermeable Tía Rosa"), nombre vacío (""), precio 0 ("Calcomanía R2K"),
stock 0 (Impermeable), margen 0 ("Llavero de moto"), margen negativo ("Visor polarizado en liquidación")
y volumen (entrada de 1000 unidades).
