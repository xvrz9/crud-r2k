import calendar
import sqlite3
from datetime import date
from pathlib import Path

from r2k import inventario as inv

RUTA_DB = Path(__file__).resolve().parents[2] / "r2k.db"

ESQUEMA = """
CREATE TABLE IF NOT EXISTS producto (
    id_producto   INTEGER PRIMARY KEY,
    nombre        TEXT NOT NULL,
    precio_venta  INTEGER NOT NULL,
    stock_actual  INTEGER NOT NULL,
    activo        INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS entrada (
    id_entrada     INTEGER PRIMARY KEY,
    id_producto    INTEGER NOT NULL REFERENCES producto (id_producto),
    fecha          TEXT NOT NULL,
    cantidad       INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS venta (
    id_venta INTEGER PRIMARY KEY,
    fecha    TEXT NOT NULL,
    total    INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS detalle_venta (
    id_detalle      INTEGER PRIMARY KEY,
    id_venta        INTEGER NOT NULL REFERENCES venta (id_venta),
    id_producto     INTEGER NOT NULL REFERENCES producto (id_producto),
    cantidad        INTEGER NOT NULL,
    precio_unitario INTEGER NOT NULL,
    subtotal        INTEGER NOT NULL
);
"""


def conectar(ruta=RUTA_DB):
    con = sqlite3.connect(ruta)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript(ESQUEMA)
    return con


def _hoy():
    return date.today().isoformat()


def _validar_fecha(fecha):
    try:
        date.fromisoformat(fecha)
    except (TypeError, ValueError):
        raise inv.ProductoInvalidoError(
            "La fecha debe tener la forma AAAA-MM-DD"
        ) from None


def _sin_stock(hay):
    unidades = "1 unidad" if hay == 1 else f"{hay} unidades"
    return inv.StockInsuficienteError(f"Stock insuficiente: solo hay {unidades}")


def _cargar(con, id_producto):
    fila = con.execute(
        "SELECT * FROM producto WHERE id_producto = ?", (id_producto,)
    ).fetchone()
    if fila is None:
        return {}
    producto = inv.Producto(
        fila["id_producto"],
        fila["nombre"],
        0,
        fila["precio_venta"],
        fila["stock_actual"],
        bool(fila["activo"]),
    )
    return {producto.id_producto: producto}


def _guardar_stock(con, producto):
    con.execute(
        "UPDATE producto SET stock_actual = ?, activo = ? WHERE id_producto = ?",
        (producto.stock_actual, int(producto.activo), producto.id_producto),
    )


def obtener_producto(con, id_producto):
    return con.execute(
        "SELECT * FROM producto WHERE id_producto = ? AND activo = 1", (id_producto,)
    ).fetchone()


def listar_productos(con, buscar=""):
    return con.execute(
        "SELECT * FROM producto WHERE activo = 1 AND nombre LIKE ? ORDER BY nombre",
        (f"%{buscar.strip()}%",),
    ).fetchall()


def crear_producto(con, nombre, precio_venta, stock_actual):
    inv.validar_producto(nombre, precio_venta, stock_actual)
    with con:
        cursor = con.execute(
            "INSERT INTO producto (nombre, precio_venta, stock_actual) "
            "VALUES (?, ?, ?)",
            (nombre.strip(), precio_venta, stock_actual),
        )
    return cursor.lastrowid


def editar_producto(con, id_producto, nombre, precio_venta):
    if obtener_producto(con, id_producto) is None:
        raise inv.ProductoNoEncontradoError(f"No existe el producto {id_producto}")
    inv.validar_producto(nombre, precio_venta, mensaje="El precio debe ser mayor que 0")
    with con:
        con.execute(
            "UPDATE producto SET nombre = ?, precio_venta = ? WHERE id_producto = ?",
            (nombre.strip(), precio_venta, id_producto),
        )


def eliminar_producto(con, id_producto):
    productos = _cargar(con, id_producto)
    inv.eliminar_producto(productos, id_producto)
    with con:
        _guardar_stock(con, productos[id_producto])


def registrar_entrada(con, id_producto, cantidad, fecha=None):
    fecha = fecha or _hoy()
    _validar_fecha(fecha)
    productos = _cargar(con, id_producto)
    nuevo_stock = inv.registrar_entrada(productos, id_producto, cantidad)
    with con:
        con.execute(
            "INSERT INTO entrada (id_producto, fecha, cantidad) VALUES (?, ?, ?)",
            (id_producto, fecha, cantidad),
        )
        _guardar_stock(con, productos[id_producto])
    return nuevo_stock


def listar_entradas(con, id_producto, limite=10):
    return con.execute(
        "SELECT * FROM entrada WHERE id_producto = ? ORDER BY id_entrada DESC LIMIT ?",
        (id_producto, limite),
    ).fetchall()


def registrar_venta(con, items, fecha=None):
    fecha = fecha or _hoy()
    _validar_fecha(fecha)
    if not isinstance(items, list) or not items:
        raise inv.CantidadInvalidaError("La venta no tiene productos")

    productos = {}
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get("id_producto"), int):
            raise inv.ProductoNoEncontradoError("Falta el producto de la venta")
        id_producto = item["id_producto"]
        if id_producto not in productos:
            productos.update(_cargar(con, id_producto))
        try:
            inv.registrar_salida(productos, id_producto, item.get("cantidad"))
        except inv.StockInsuficienteError:
            raise _sin_stock(productos[id_producto].stock_actual) from None

    total = sum(
        productos[i["id_producto"]].precio_venta * i["cantidad"] for i in items
    )
    with con:
        id_venta = con.execute(
            "INSERT INTO venta (fecha, total) VALUES (?, ?)", (fecha, total)
        ).lastrowid
        for item in items:
            precio = productos[item["id_producto"]].precio_venta
            cantidad = item["cantidad"]
            con.execute(
                "INSERT INTO detalle_venta "
                "(id_venta, id_producto, cantidad, precio_unitario, subtotal) "
                "VALUES (?, ?, ?, ?, ?)",
                (id_venta, item["id_producto"], cantidad, precio, precio * cantidad),
            )
        for producto in productos.values():
            _guardar_stock(con, producto)
    return id_venta, total


def corregir_detalle(con, id_venta, id_detalle, cantidad_nueva):
    detalle = con.execute(
        "SELECT * FROM detalle_venta WHERE id_detalle = ? AND id_venta = ?",
        (id_detalle, id_venta),
    ).fetchone()
    if detalle is None:
        raise inv.VentaNoEncontradaError(f"No existe la venta {id_venta}")

    productos = _cargar(con, detalle["id_producto"])
    producto = productos[detalle["id_producto"]]
    try:
        inv.corregir_venta(producto, detalle["cantidad"], cantidad_nueva)
    except inv.StockInsuficienteError:
        raise _sin_stock(producto.stock_actual) from None

    with con:
        con.execute(
            "UPDATE detalle_venta SET cantidad = ?, subtotal = ? WHERE id_detalle = ?",
            (cantidad_nueva, cantidad_nueva * detalle["precio_unitario"], id_detalle),
        )
        con.execute(
            "UPDATE venta SET total = (SELECT SUM(subtotal) FROM detalle_venta "
            "WHERE id_venta = ?) WHERE id_venta = ?",
            (id_venta, id_venta),
        )
        _guardar_stock(con, producto)
    return con.execute(
        "SELECT total FROM venta WHERE id_venta = ?", (id_venta,)
    ).fetchone()["total"]


def listar_ventas(con, limite=30):
    return con.execute(
        "SELECT v.id_venta, v.fecha, v.total, d.id_detalle, d.cantidad, "
        "d.precio_unitario, d.subtotal, p.nombre "
        "FROM venta v JOIN detalle_venta d USING (id_venta) "
        "JOIN producto p USING (id_producto) "
        "ORDER BY v.id_venta DESC, d.id_detalle LIMIT ?",
        (limite,),
    ).fetchall()


def ventas_del_mes(con, mes):
    return con.execute(
        "SELECT v.id_venta, v.fecha, p.nombre, d.cantidad, d.precio_unitario, "
        "d.subtotal FROM venta v JOIN detalle_venta d USING (id_venta) "
        "JOIN producto p USING (id_producto) WHERE v.fecha LIKE ? "
        "ORDER BY v.fecha, v.id_venta, d.id_detalle",
        (f"{mes}-%",),
    ).fetchall()


def reporte_mensual(con, mes):
    ventas = [
        (f["fecha"], f["nombre"], f["cantidad"], f["precio_unitario"])
        for f in ventas_del_mes(con, mes)
    ]
    return inv.reporte_mensual(ventas, mes)


def ventas_por_dia(detalle, mes):
    anio, numero = (int(parte) for parte in mes.split("-"))
    dias = [0] * calendar.monthrange(anio, numero)[1]
    for fila in detalle:
        dias[int(fila["fecha"][8:10]) - 1] += fila["subtotal"]
    return dias
