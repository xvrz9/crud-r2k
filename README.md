# CRUD R2K

Sistema para que R2K, una microempresa de accesorios para motos en Neiva, deje de llevar el inventario y
las cuentas en un cuaderno. Proyecto final del Seminario de IA Aplicada al Ciclo de Vida del Software (FET).

Autor: Sergio Alejandro Vargas Trujillo

## Funcionalidad de la semana 5

### Historia de usuario

**HU-06: Registrar la venta de un producto y descontar el stock** (Prioridad: Must)

Como dueño de R2K, quiero registrar cada producto que vendo para que se descuente automáticamente
del stock, para saber en todo momento cuánta mercancía me queda sin revisar el cuaderno.

**Criterios de aceptación**

```gherkin
Escenario 1: Venta normal
  Dado que el producto "Casco integral" tiene 10 unidades en stock
  Cuando registro la venta de 3 unidades
  Entonces el stock del "Casco integral" queda en 7

Escenario 2: Vender todo lo que hay
  Dado que "Guantes de moto" tiene 5 unidades en stock
  Cuando registro la venta de 5 unidades
  Entonces el stock queda en 0

Escenario 3 (error): Stock insuficiente
  Dado que "Guantes de moto" tiene 5 unidades en stock
  Cuando intento registrar la venta de 8 unidades
  Entonces el sistema rechaza la venta con un mensaje de stock insuficiente
  Y el stock sigue en 5
```

### Contrato

- **Firma:** `registrar_salida(productos: dict[int, Producto], id_producto: int, cantidad: int) -> int`
- **Recibe:**
  - `productos`: el inventario actual, un diccionario de `id_producto` a `Producto`.
  - `id_producto`: el id del producto vendido.
  - `cantidad`: las unidades vendidas, como entero.
- **Devuelve:** el nuevo `stock_actual` del producto después de la venta.
- **Efecto:** modifica `stock_actual` del producto dentro del diccionario recibido.
- **Supuestos:**
  - `Producto` usa los atributos del modelo de datos del Diseño S4, §5.
  - Los precios son enteros en pesos colombianos, nunca `float`.
  - Solo se vende en unidades enteras.
  - El stock nunca queda negativo y no hay ventas a crédito (pregunta P-05 abierta).
- **Casos límite:** vender exactamente todo el stock deja 0; la cantidad mínima es 1; vender stock + 1 falla.
- **Errores** (en todos el stock **no cambia**):
  - `ProductoNoEncontradoError`: el `id_producto` no existe.
  - `CantidadInvalidaError`: la cantidad es menor que 1.
  - `StockInsuficienteError`: la cantidad es mayor que `stock_actual`.

### Ejemplos

| # | Stock inicial | Producto | Cantidad | Salida esperada |
|---|---|---|---|---|
| 1 | 10 | 1 (Casco integral) | 3 | `7` |
| 2 | 5 | 2 (Guantes de moto) | 1 | `4` |
| 3 | 5 | 2 (Guantes de moto) | 5 | `0` |
| 4 | 5 | 2 (Guantes de moto) | 8 | `StockInsuficienteError`, el stock sigue en 5 |
| 5 | 10 | 1 (Casco integral) | 0 | `CantidadInvalidaError` |
| 6 | — | 99 (no existe) | 1 | `ProductoNoEncontradoError` |

### Cómo ejecutar las pruebas

```bash
pip install -r requirements.txt
pytest -v
```

Un solo comando corre todas las pruebas. `pytest.ini` agrega `src` al path.

### Estructura

```
crud-r2k/
├── README.md
├── bitacora_ia.md
├── .gitignore
├── pytest.ini
├── requirements.txt
├── src/r2k/inventario.py
└── tests/test_inventario.py
```
