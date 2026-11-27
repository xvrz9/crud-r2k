# CRUD R2K

Proyecto final del Seminario de IA Aplicada al Ciclo de Vida del Software (FET).

[![Pruebas](https://github.com/xvrz9/crud-r2k/actions/workflows/pruebas.yml/badge.svg)](https://github.com/xvrz9/crud-r2k/actions/workflows/pruebas.yml)

## 1. Qué es

CRUD R2K es una aplicación para que el dueño de R2K, una microempresa de accesorios para motos y
stickers en Neiva, deje el cuaderno: registra sus productos, la mercancía que le llega y las ventas, y ve
al final del mes cuánto vendió y de qué productos. La usa solo él, en su portátil, sin pagar nada.

Es una aplicación web local (Python, Flask y SQLite) que se abre en el navegador del mismo portátil
([ADR-001](docs/04_diseno_y_ADR_S4.pdf)). Lo que hace, según el
[documento de requisitos](docs/03_requisitos_S3.pdf):

| Historia | Qué hace | Pantalla |
|---|---|---|
| HU-01 | Registrar un producto con sus precios y cantidad | Productos |
| HU-02 | Buscar un producto por nombre | Productos |
| HU-03 | Editar el nombre y los precios (las ventas viejas conservan su precio) | Productos → Editar |
| HU-04 | Eliminar un producto agotado (solo con stock 0) | Productos |
| HU-05 | Registrar la mercancía que llega; el stock sube solo | Mercancía |
| HU-06 | Registrar una venta; el stock baja solo | Ventas |
| HU-08 | Corregir la cantidad de una venta mal anotada | Ventas |
| HU-10 | Reporte del mes: cuánto se vendió de cada producto y el total | Reporte del mes |
| RNF-03 | Copia de seguridad de los datos a una memoria USB | `copia_usb.bat` |

No calcula ganancias ni gastos (HU-07 y HU-09 quedaron fuera por decisión del cliente).

## 2. Requisitos

- Windows 10 u 11 para el dueño (los `.bat`). Para desarrollar sirve también Linux o macOS.
- Python 3.10 o superior (probado con 3.10 y 3.13).
- `requirements.txt`: lo que necesita la app (Flask).
- `requirements-dev.txt`: lo anterior más las herramientas de desarrollo: `pytest` (pruebas), `ruff`
  (linter) y `pip-audit` (vulnerabilidades en las dependencias).

## 3. Instalación y uso

**Para el dueño (Windows):** está explicado paso a paso en la
[guía de despliegue](docs/08_guia_despliegue.md). En resumen:

1. Instalar Python desde python.org marcando "Add python.exe to PATH".
2. Doble clic en `instalar.bat` (una sola vez).
3. Doble clic en `iniciar.bat`: se abre el navegador en `http://localhost:5000`.
4. Para la copia de seguridad: `copia_usb.bat` (ver el [plan de operación](docs/09_plan_operacion.md)).

**Para desarrollar:**

Windows (PowerShell):

```powershell
git clone https://github.com/xvrz9/crud-r2k.git
cd crud-r2k
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
$env:PYTHONPATH = "src"
python -m r2k.app
```

Linux o macOS:

```bash
git clone https://github.com/xvrz9/crud-r2k.git
cd crud-r2k
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
PYTHONPATH=src python -m r2k.app
```

La base de datos `r2k.db` se crea sola la primera vez y está en `.gitignore`: los datos del negocio no
se suben al repositorio. La app no usa variables de entorno ni claves.

## 4. Cómo está hecha

- `src/r2k/inventario.py`: las reglas del negocio, sin base de datos (vender, entradas, eliminar,
  corregir, reporte). Es el código de las semanas 5 a 7, con las reglas nuevas de HU-01, HU-03 y HU-08.
- `src/r2k/datos.py`: guarda y lee en SQLite. Carga los productos, llama a las reglas de
  `inventario.py` y guarda el resultado.
- `src/r2k/app.py`: la aplicación Flask. Tiene las pantallas y las rutas JSON del
  [Diseño S4, sección 6](docs/04_diseno_y_ADR_S4.pdf).
- `src/r2k/templates/` y `src/r2k/static/`: las pantallas (HTML), el estilo con letra grande y un
  JavaScript corto que envía los formularios.
- `src/r2k/copia.py`: la copia de seguridad a la USB.

Sigue funcionando la demostración por consola de la semana 5: `python -m r2k`.

## 5. Pruebas

Un comando para cada cosa, desde la raíz del repositorio:

```bash
pytest -v                         # todas las pruebas
ruff check .                      # linter con reglas E, F, B y S (configurado en pyproject.toml)
pip-audit -r requirements.txt     # vulnerabilidades conocidas en las dependencias
```

El [pipeline de GitHub Actions](https://github.com/xvrz9/crud-r2k/actions/workflows/pruebas.yml)
corre los tres en cada `push`, con Python 3.10 y 3.13.

- `tests/test_inventario.py`: las 9 pruebas de la semana 5 (normales, de límite y de error).
- `tests/test_abuso.py`: pruebas de abuso de la semana 6 (cantidades que no son enteros, productos con
  datos imposibles, stock intacto después de cada error).
- `tests/test_reglas.py`: pruebas de la semana 7 (particiones, límites y tabla de decisión). Los casos
  están explicados en [docs/07_plan_pruebas_S7.md](docs/07_plan_pruebas_S7.md).
- `tests/test_demo.py`: comprueba la demostración por consola.
- `tests/test_app.py`: los dos escenarios de cada historia del documento de requisitos, contra la
  aplicación con una base de datos temporal.
- `tests/test_copia.py`: la copia de seguridad.

Todas las pruebas usan datos de ejemplo, no las cuentas reales del negocio.

## 6. Estructura

```
crud-r2k/
├── README.md                 # este archivo
├── bitacora_ia.md            # registro del uso de IA
├── docs/                     # documentos de cada semana (ver la tabla de abajo)
├── instalar.bat              # instala la app (una sola vez)
├── iniciar.bat               # abre la app
├── copia_usb.bat             # copia de seguridad a la USB
├── requirements.txt          # lo que necesita la app (Flask)
├── requirements-dev.txt      # pruebas, linter y auditoría
├── pyproject.toml            # configuración de pytest y de ruff
├── .github/workflows/        # pipeline de GitHub Actions
├── src/r2k/
│   ├── inventario.py         # reglas del negocio
│   ├── datos.py              # base de datos SQLite
│   ├── app.py                # aplicación Flask
│   ├── copia.py              # copia de seguridad
│   ├── __main__.py           # demostración por consola de la semana 5
│   ├── templates/            # pantallas
│   └── static/               # estilo y JavaScript
└── tests/
    ├── conftest.py           # datos de prueba inventados
    ├── test_inventario.py
    ├── test_abuso.py
    ├── test_reglas.py
    ├── test_demo.py
    ├── test_app.py
    └── test_copia.py
```

Documentos de cada semana, en `docs/`:

| Semana | Documento |
|---|---|
| 1 | [Laboratorio comparativo](docs/01_laboratorio_S1.pdf) y [mapa conceptual](docs/01_mapa_conceptual_S1.pdf) |
| 2 | [Propuesta del proyecto](docs/02_propuesta_S2.pdf) y [banco de prompts](docs/02_banco_prompts_S2.pdf) |
| 3 | [Documento de requisitos](docs/03_requisitos_S3.pdf) y [banco de prompts](docs/03_banco_prompts_S3.pdf) |
| 4 | [Documento de diseño con el ADR-001](docs/04_diseno_y_ADR_S4.pdf) |
| 5 | [Funcionalidad de la semana 5](#funcionalidad-de-la-semana-5) (en este README) |
| 6 | [Revisión de código y seguridad](docs/06_revision_codigo_S6.md) |
| 7 | [Plan y registro de pruebas](docs/07_plan_pruebas_S7.md) |
| 8 | [Guía de despliegue](docs/08_guia_despliegue.md) |
| 9 | [Plan de operación](docs/09_plan_operacion.md) |

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
