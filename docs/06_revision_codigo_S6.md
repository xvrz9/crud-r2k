# Informe de revisión de código y seguridad

Proyecto: CRUD R2K
Estudiante: Sergio Alejandro Vargas Trujillo
Fecha: 2026-11-14
Commit revisado: `104eada` (entrega de la semana 5, antes de las correcciones)

## 1. Herramientas y criterios

- **Linter:** ruff 0.16.9 con las reglas E, F, B y S. Configuración en `pyproject.toml`. Antes: 9 avisos (3 E501 y 6 S101). Después: `All checks passed!`.
- **Auditoría de dependencias:** pip-audit 2.10.1 con `pip-audit -r requirements.txt`. Resultado: `No known vulnerabilities found`.
- **Pruebas:** pytest 9.1.1. Antes: 9 passed. Después: 28 passed. `tests/test_inventario.py` no se modificó.
- **Lista de revisión:** la de la semana 6 (corrección y pruebas, diseño y legibilidad, seguridad).
- **Revisión con IA:** Claude (Claude Code), con el prompt de revisión de la semana (ver sección 3).

### Puntos de seguridad revisados

| Punto | ¿Aplica? | Resultado |
|---|---|---|
| Inyección (consultas con parámetros) | No, porque el incremento no tiene base de datos, comandos de sistema ni `eval`. Las f-strings solo arman mensajes de error. | Sin hallazgos. Lo más cercano es la entrada sin validar: ver H-01 y H-02. |
| Secretos (código, historial, .gitignore, .env.example) | Sí | Sin claves en el código ni en el historial (`git log -p --all` hasta `104eada`, filtrado por key, secret, password y token: 0 resultados). `.env` ya estaba en `.gitignore`. Faltaba `.env.example`: ver H-04. |
| Contraseñas (scrypt, bcrypt o argon2 con sal) | No, porque el proyecto todavía no tiene usuarios ni guarda contraseñas. | No aplica. Queda en pendientes para cuando exista el inicio de sesión. |
| Control de acceso (rol verificado y prueba de abuso) | No todavía, porque `registrar_salida` es una función de dominio sin usuario ni rol, y los permisos del vendedor siguen sin definir con el cliente (pregunta P-02). | No aplica. Las pruebas de abuso de este incremento son de entrada inválida (H-01, H-02). Ver pendientes. |
| Dependencias (existen, necesarias, versión fijada, pip-audit) | Sí | pytest, ruff y pip-audit existen en PyPI y son necesarias para pruebas, linter y auditoría. La versión no estaba fijada: ver H-03. pip-audit sin vulnerabilidades. |

## 2. Tabla de hallazgos

Las líneas son las del commit revisado `104eada`.

| Id | Archivo y línea | Problema | Categoría (OWASP o tipo) | Severidad | Corrección | Commit |
|---|---|---|---|---|---|---|
| H-01 | src/r2k/inventario.py:34-39 y 53 | La cantidad no se valida como entero: `2.5` deja el stock en `7.5`, `nan` lo deja en `nan`, `True` vende 1 y `"3"` lanza `TypeError` sin controlar | Validación de entrada (CWE-20), integridad de datos | Media | `_validar_cantidad` rechaza lo que no sea `int` (y `bool`) con `CantidadInvalidaError`; 8 pruebas de abuso | 930e81a |
| H-02 | src/r2k/inventario.py:18-24 | `Producto` acepta stock negativo y precios negativos o decimales | Validación de entrada (CWE-20) | Media | `__post_init__` lanza `ProductoInvalidoError`; 8 pruebas | ad1ffd8 |
| H-03 | requirements.txt:1 | `pytest>=8.0` sin versión fija: cada instalación puede traer otra versión | A06 Componentes vulnerables y desactualizados | Baja | Versiones exactas de pytest, ruff y pip-audit | bb3b61d |
| H-04 | raíz del repositorio; .gitignore:1 | No existía `.env.example` y `.gitignore` no cubría `.env.local` ni otras variantes | Secretos / A05 Configuración | Baja | `.env.example` y `.gitignore` con `.env.*` | 881addb |
| H-05 | src/r2k/inventario.py:31, 37 y 46 | Tres líneas de más de 88 caracteres (E501) | Estilo | Baja | Líneas partidas | 97b3ea0 |
| H-06 | raíz del repositorio | No había linter configurado; la configuración estaba repartida | Calidad | Baja | ruff en `pyproject.toml`; pytest pasa de `pytest.ini` a `pyproject.toml` | ccb1086 |
| H-07 | tests/test_inventario.py:39-41 y 58-60 | Dos pruebas de error no comprueban que el stock quede intacto, aunque el README lo promete | Pruebas | Baja | Dos pruebas nuevas en `tests/test_abuso.py`, sin tocar las existentes | ae651b9 |
| H-08 | src/r2k/inventario.py:34 y 6-15 | `_validar_cantidad` hacía dos cosas y los errores no tenían una base común | Diseño y legibilidad | Baja | Se separa `_validar_stock_suficiente` y se agrega `ErrorInventario` | 5bbfd9d |
| H-09 | src/r2k/inventario.py:27, 34 y 47-50 | Funciones sin docstring y docstring principal sin errores ni efecto | Legibilidad | Baja | Docstrings en las funciones principales (se acortaron el 2026-11-27) | e59416c |
| H-10 | README.md | Faltaban instalación, ejecución, uso de IA y licencia; no había forma de ejecutar nada | Documentación | Baja | README con ocho secciones y demostración `python -m r2k` | 4306bad, a800487 |

**Severidad:** alta (permite acceder o cambiar datos sin permiso, o expone secretos), media (error probable o riesgo con condiciones), baja (estilo o mantenibilidad). No hubo hallazgos de severidad alta.

### Avisos del linter no corregidos

| Regla | Archivo y línea | Por qué se mantiene |
|---|---|---|
| S101 | tests/ (todos los `assert`) | `assert` es la forma normal de comprobar en pytest. Se ignora solo en `tests/*` con `per-file-ignores`; en `src/` la regla sigue activa. |

## 3. Revisión con IA

**Prompt usado** (entrada 7 de `bitacora_ia.md`): rol de revisor senior de código y seguridad, solo lectura; contexto del incremento; tres criterios (corrección y pruebas, diseño y legibilidad, seguridad); salida en dos tablas, «Problemas seguros» y «Sospechas», con archivo:línea, categoría y severidad; una línea por cada uno de los cinco puntos de seguridad; restricciones: no inventar líneas, máximo 12 hallazgos.

| Hallazgo de la IA | ¿Real o falso positivo? | Cómo lo verifiqué |
|---|---|---|
| P1. La cantidad `2.5` o `nan` daña el stock | Real (H-01) | Ejecutando sobre `104eada`: `registrar_salida(inv, 1, 2.5)` devolvió `7.5`; con `nan` devolvió `nan` |
| P2. `True` se acepta como cantidad | Real (H-01) | Ejecutando: devolvió `9` |
| P3. `"3"` o `None` lanzan `TypeError` genérico | Real (H-01) | Ejecutando: `TypeError: '<' not supported…`; el stock siguió en 10 |
| P4. Las pruebas no cubren cantidades no enteras | Real (H-01) | Los 7 casos nuevos fallaron antes de la corrección (`7 failed, 10 passed`) |
| P5. `_validar_cantidad` hace dos cosas | Real (H-08) | Leyendo las líneas 34-43: dos `if` con reglas distintas |
| P6. Docstrings incompletos | Real (H-09) | Leyendo las líneas 27, 34 y 47-50 |
| P7. `pytest>=8.0` sin fijar | Real (H-03) | `requirements.txt:1`. No se aceptó la parte de crear `requirements-dev.txt`: todas las dependencias son de desarrollo |
| P8. Dos pruebas de error no revisan el stock | Real (H-07) | Leyendo las líneas 39-41 y 58-60. La IA sugería agregar el `assert` a esas pruebas; se rechazó porque las pruebas no se modifican y se escribieron pruebas nuevas |
| S1. `Producto` no valida sus campos (sospecha) | Real (H-02) | Ejecutando: `Producto(1, "X", -5, 1.5, -3)` se creó sin error |
| S2. El id está duplicado en la clave y en el producto (sospecha) | Falso positivo por ahora | No hay forma de que cause un error en este incremento: la búsqueda solo usa la clave y las pruebas arman el diccionario a mano. Queda en pendientes |
| S3. Validar y descontar son dos pasos, riesgo de concurrencia (sospecha) | Falso positivo por ahora | No es reproducible: todo corre en memoria y en un solo hilo. Queda en pendientes para cuando haya base de datos |

**Lo que la IA no encontró:**

- Los tres avisos E501 del linter (H-05) y que no había linter configurado (H-06). Los encontró ruff.
- Que faltaba `.env.example` (H-04). Dijo «secretos: no aplica» y solo miró los archivos actuales; no revisó el historial de Git. El historial se revisó aparte con `git log -p --all`.
- No ejecutó pip-audit (lo reconoció en sus notas), así que no podía afirmar que pytest no tuviera vulnerabilidades.
- Que el README no explicaba cómo instalar ni ejecutar el proyecto (H-10).

## 4. Pendientes

| Pendiente | Por qué no se corrigió todavía | Plan |
|---|---|---|
| Control de acceso por rol (dueño y vendedor) | No hay usuarios en este incremento y los permisos del vendedor no están definidos (P-02) | Al agregar usuarios: verificar el rol en cada operación restringida, con prueba de abuso |
| Contraseñas con scrypt o argon2 | No hay inicio de sesión todavía | Usar `hashlib.scrypt` con sal cuando exista el registro de usuarios |
| Descuento de stock atómico (S3) | Solo es un riesgo con base de datos o peticiones simultáneas | Hacer la validación y el descuento en una sola transacción al agregar persistencia |
| Id duplicado en la clave y en `Producto` (S2) | No causa errores hoy | Decidir la fuente de verdad cuando exista la capa que arma el inventario |
| `Producto` no se vuelve a validar si se le asigna un valor después de creado, y no valida el nombre | La única función que modifica el stock ya lo valida | Evaluar una clase inmutable o validar en la capa de persistencia |
| ~~Confirmar el texto de la HU-02 con el documento de requisitos de la semana 3~~ | Resuelto el 2026-11-27: en el documento final la venta es la HU-06 | Se corrigió el README |

**Claves expuestas:** Ninguna. Nunca se subió una clave al repositorio; se comprobó en el historial completo.
