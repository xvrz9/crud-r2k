# Guía de despliegue: CRUD R2K

Cómo dejar CRUD R2K funcionando en el portátil del dueño de R2K. Todo es gratis y, después de
instalarlo, no necesita internet.

## 1. Qué se necesita

- Un portátil con Windows 10 u 11.
- Python 3.10 o superior, descargado de python.org (gratis).
- Internet solo durante la instalación, para descargar Flask.

## 2. Instalación (una sola vez)

1. **Instalar Python.** Descargarlo de python.org y, en la primera pantalla del instalador, marcar la
   casilla **"Add python.exe to PATH"**.
2. **Descargar el proyecto.** En GitHub, botón **Code → Download ZIP**. Descomprimirlo en
   `Documentos\R2K`.
3. **Instalar lo que usa la app.** Entrar a la carpeta y darle doble clic a `instalar.bat`. Crea un
   entorno de Python dentro de la carpeta (`.venv`) e instala Flask. Al final dice
   "Instalación terminada".
4. **Crear el acceso directo.** Clic derecho en `iniciar.bat` → **Enviar a → Escritorio (crear acceso
   directo)**. Se le puede cambiar el nombre a "R2K".

## 3. Abrir la aplicación

Doble clic en el acceso directo "R2K". Se abre una ventana negra (no hay que cerrarla mientras se usa
la app) y el navegador en `http://localhost:5000`.

- La primera vez se crea sola la base de datos `r2k.db` en la carpeta del proyecto.
- La app solo escucha en el mismo portátil (`127.0.0.1`): nadie más en la red puede entrar.
- En la ventana negra sale un aviso en inglés que dice "development server". Es normal: ese servidor
  sirve para una sola persona en su propio equipo, que es este caso.
- Para cerrarla, se cierra la ventana negra.

## 4. Comprobar que quedó bien

Después de instalar, hacer esta prueba corta con datos de ejemplo:

| Paso | Qué se hace | Qué debe pasar |
|---|---|---|
| 1 | Crear «Sticker de prueba», compra $1.000, venta $2.000, cantidad 1 | Aparece en la lista |
| 2 | Venderlo | El stock queda en 0 |
| 3 | Abrir el reporte del mes actual | Sale el sticker y el total $2.000 |
| 4 | Eliminar el sticker (ya tiene stock 0) | Desaparece de la lista, pero sigue en el reporte |

Después de la prueba se borra `r2k.db` con la app cerrada, para que el dueño empiece con la base
limpia.

## 5. Actualizar a una versión nueva

1. Cerrar la app y sacar una copia de seguridad (ver el [plan de operación](09_plan_operacion.md)).
2. Descargar el ZIP nuevo y reemplazar los archivos de la carpeta, **menos `r2k.db`**.
3. Darle doble clic otra vez a `instalar.bat` y abrir la app.

## 6. Para el desarrollador

- Las pruebas se corren con `pytest -v` y el linter con `ruff check .` (ver el README).
- En cada `push` a GitHub, el pipeline de GitHub Actions corre las pruebas y el linter. Solo se le
  entrega una versión nueva al dueño si el pipeline está en verde.
- `r2k.db` está en `.gitignore`: los datos reales del negocio nunca se suben al repositorio.
