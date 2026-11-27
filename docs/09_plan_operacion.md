# Plan de operación: CRUD R2K

Qué hacer en el día a día para que la app funcione y no se pierdan los datos. La usa una sola persona,
el dueño de R2K, en su portátil.

## 1. Uso diario

- Abrir la app con el acceso directo "R2K" y dejar la ventana negra abierta mientras se usa.
- Registrar las entradas de mercancía cuando llegan y cada venta cuando se hace.
- Si una venta quedó mal anotada, corregirla desde la lista de ventas (no hay que borrar nada).
- Al terminar el día, cerrar la ventana negra.

## 2. Copia de seguridad

Todos los datos están en un solo archivo: `r2k.db`. Si el portátil se daña, lo único que hay que tener
es una copia de ese archivo (RNF-03).

**Cuándo:** cada semana y siempre al terminar el mes, después de ver el reporte.

**Cómo:**

1. Cerrar la app.
2. Conectar la memoria USB.
3. Doble clic en `copia_usb.bat` y escribir la letra de la USB (por ejemplo `E`).
4. La copia queda en la USB como `R2K_copias\r2k_AAAA-MM-DD.db`, con la fecha del día. Las copias
   viejas no se borran.

## 3. Recuperar los datos

Si se dañó el portátil o se borró `r2k.db`:

1. Instalar la app en el portátil (ver la [guía de despliegue](08_guia_despliegue.md)).
2. Copiar de la USB la copia más reciente a la carpeta del proyecto.
3. Cambiarle el nombre a `r2k.db`.
4. Abrir la app y revisar que estén los productos y el reporte del último mes.

Esta recuperación se prueba una vez al instalar, para estar seguros de que funciona.

## 4. Problemas comunes

| Qué pasa | Por qué | Qué hacer |
|---|---|---|
| El navegador dice que no puede abrir la página | La ventana negra está cerrada | Abrir otra vez con el acceso directo |
| La ventana negra se cierra sola al abrirla | Falta instalar o Python no está en el PATH | Volver a correr `instalar.bat`; si sigue, reinstalar Python marcando "Add python.exe to PATH" |
| "Stock insuficiente" al vender | Se intenta vender más de lo que hay | Revisar si falta registrar una entrada de mercancía |
| "No se puede eliminar: todavía tiene N unidades en stock" | Solo se eliminan productos agotados | Es normal. Si de verdad ya no está, vender o corregir hasta que quede en 0 |
| Una venta quedó mal | Error al anotar | Corregir la cantidad de esa venta |

## 5. Quién responde

| Qué | Responsable |
|---|---|
| Usar la app, registrar bien los datos y sacar las copias | El dueño de R2K |
| Arreglar errores del programa, probar los cambios y entregar versiones nuevas | Sergio Alejandro Vargas (desarrollador) |

Cuando el dueño encuentre un error, me avisa con lo que estaba haciendo y el mensaje que salió. Antes
de entregarle una versión nueva, el cambio tiene que pasar las pruebas y el pipeline en verde.

## 6. Datos y privacidad

- La app guarda productos, precios, entradas y ventas. No guarda datos de clientes ni de personas.
- Los datos se quedan en el portátil y en la USB del dueño. No se suben a internet ni al repositorio.
- En el repositorio y en los documentos del seminario solo hay datos de ejemplo.
