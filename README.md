# CRUD R2K

Proyecto final del Seminario de IA Aplicada al Ciclo de Vida del Software (FET).

## 1. Qué es

Sistema para que R2K, una microempresa de accesorios para motos en Neiva, deje de llevar el inventario y
las cuentas en un cuaderno. El objetivo es controlar qué mercancía entra y qué se vende.

Por ahora está la lógica del inventario, sin base de datos ni interfaz web todavía:

- `registrar_salida`: registra una venta y descuenta el stock (HU-06). Su contrato está en
  [Funcionalidad de la semana 5](#funcionalidad-de-la-semana-5).
- `registrar_entrada`: suma la mercancía que llega (HU-05).
- `eliminar_producto`: elimina un producto solo si tiene stock 0 (HU-04).
- `reporte_mensual`: lo vendido en un mes, por producto, y el total (HU-10).

## 2. Requisitos

- Python 3.10 o superior (probado con 3.10 y 3.13).
- `pip` y `git`.
- El código de `src/` solo usa la biblioteca estándar. Las dependencias de `requirements.txt` son
  herramientas de desarrollo, con versión fija: `pytest` (pruebas), `ruff` (linter) y `pip-audit`
  (auditoría de dependencias).

## 3. Instalación

Windows (PowerShell):

```powershell
git clone https://github.com/xvrz9/crud-r2k.git
cd crud-r2k
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Linux o macOS:

```bash
git clone https://github.com/xvrz9/crud-r2k.git
cd crud-r2k
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

El proyecto no necesita variables de entorno todavía. Cuando las necesite, se copia `.env.example` como
`.env` (que está en `.gitignore`) y se llenan ahí los valores.

## 4. Ejecución

Todavía no hay interfaz. Hay una demostración por consola que registra una venta normal y una rechazada.

Windows (PowerShell):

```powershell
$env:PYTHONPATH = "src"
python -m r2k
```

Linux o macOS:

```bash
PYTHONPATH=src python -m r2k
```

Salida esperada:

```
Venta de 3 x Casco integral -> stock: 7
Venta de 8 x Guantes de moto rechazada -> Guantes de moto: hay 5 en stock y se intentaron vender 8
Stock de Guantes de moto: 5
```

Para usar la función desde otro código:

```python
from r2k.inventario import Producto, registrar_salida

productos = {1: Producto(1, "Casco integral", 120000, 180000, 10)}
registrar_salida(productos, 1, 3)  # devuelve 7
```

## 5. Pruebas

Un comando para cada cosa, desde la raíz del repositorio:

```bash
pytest -v                         # todas las pruebas
ruff check .                      # linter con reglas E, F, B y S (configurado en pyproject.toml)
pip-audit -r requirements.txt     # vulnerabilidades conocidas en las dependencias
```

- `tests/test_inventario.py`: las 9 pruebas de la semana 5 (normales, de límite y de error).
- `tests/test_abuso.py`: pruebas de abuso de la semana 6 (cantidades que no son enteros, productos con
  datos imposibles, stock intacto después de cada error).
- `tests/test_reglas.py`: pruebas de la semana 7 (particiones, límites y tabla de decisión). Los casos
  están explicados en [registro_pruebas.md](registro_pruebas.md).
- `tests/test_demo.py`: comprueba la demostración por consola.

`pyproject.toml` agrega `src` al path de pytest, por eso no hay que instalar el paquete.

## 6. Estructura

```
crud-r2k/
├── README.md                 # este archivo
├── bitacora_ia.md            # registro del uso de IA (semanas 5, 6 y 7)
├── revision_seguridad.md     # informe de revisión de código y seguridad (semana 6)
├── registro_pruebas.md       # tablas de casos y pruebas rotas a propósito (semana 7)
├── pyproject.toml            # configuración de pytest y de ruff
├── requirements.txt          # herramientas de desarrollo con versión fija
├── .env.example              # plantilla de variables de entorno (hoy no se usa ninguna)
├── .gitignore
├── src/r2k/
│   ├── __init__.py
│   ├── __main__.py           # demostración: python -m r2k
│   └── inventario.py         # Producto, errores y las reglas del inventario
└── tests/
    ├── conftest.py           # datos de prueba inventados
    ├── test_inventario.py
    ├── test_abuso.py
    ├── test_reglas.py
    └── test_demo.py
```

## 7. Uso de IA

Usé Claude como ayuda en el proyecto. En [bitacora_ia.md](bitacora_ia.md) anoté lo que le pedí, qué
acepté, qué no y por qué.

- **Semana 5:** me ayudó a pensar los casos de prueba de la venta y a ordenar mejor el código.
- **Semana 6:** le pedí que revisara el código buscando errores y problemas de seguridad. Lo que
  encontró lo probé antes de corregirlo. Los cambios se hicieron en una rama aparte
  (`agente/revision-s6`) y los revisé antes de pasarlos a la principal. También me ayudó a redactar
  la documentación.
- **Semana 7:** me sugirió casos de prueba. Los revisé uno por uno y quité o arreglé los que no
  servían.
- No cambié pruebas para que pasaran, no acepté nada sin probarlo y no subí datos reales del negocio.

## 8. Autor y licencia

- **Autor:** Sergio Alejandro Vargas Trujillo, Fundación Escuela Tecnológica de Neiva (FET).
- **Licencia:** proyecto académico. Todavía no se ha elegido una licencia abierta, así que todos los
  derechos quedan reservados por el autor.

---

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
- **Errores** (en todos el stock **no cambia**; todos heredan de `ErrorInventario`):
  - `ProductoNoEncontradoError`: el `id_producto` no existe.
  - `CantidadInvalidaError`: la cantidad es menor que 1 o no es un entero (semana 6: `2.5`, `True`,
    `"3"` y `None` también se rechazan).
  - `StockInsuficienteError`: la cantidad es mayor que `stock_actual`.
- **Semana 6:** `Producto` lanza `ProductoInvalidoError` al crearse si un precio o el stock no es un
  entero mayor o igual a 0.

### Ejemplos

| # | Stock inicial | Producto | Cantidad | Salida esperada |
|---|---|---|---|---|
| 1 | 10 | 1 (Casco integral) | 3 | `7` |
| 2 | 5 | 2 (Guantes de moto) | 1 | `4` |
| 3 | 5 | 2 (Guantes de moto) | 5 | `0` |
| 4 | 5 | 2 (Guantes de moto) | 8 | `StockInsuficienteError`, el stock sigue en 5 |
| 5 | 10 | 1 (Casco integral) | 0 | `CantidadInvalidaError` |
| 6 | — | 99 (no existe) | 1 | `ProductoNoEncontradoError` |
| 7 | 10 | 1 (Casco integral) | 2.5 | `CantidadInvalidaError`, el stock sigue en 10 |
