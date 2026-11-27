"""Aplicación web de R2K. Se abre con iniciar.bat o con: python -m r2k.app

Tiene dos partes:
- Las pantallas (/, /editar, /ventas, /reporte) que ve el dueño.
- Las rutas en JSON del Diseño S4, sección 6, que usan esas pantallas.
"""

import threading
import webbrowser
from datetime import date

from flask import Flask, g, jsonify, render_template, request

from r2k import datos
from r2k import inventario as inv

PUERTO = 5000

MESES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
    "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]

# Qué código HTTP devuelve cada error del inventario (Diseño S4, sección 6)
CODIGOS = {
    inv.ProductoInvalidoError: 400,
    inv.CantidadInvalidaError: 400,
    inv.ProductoNoEncontradoError: 404,
    inv.VentaNoEncontradaError: 404,
    inv.StockInsuficienteError: 409,
    inv.ProductoConStockError: 409,
}


def pesos(valor):
    """790000 -> $790.000"""
    return "$" + f"{valor:,}".replace(",", ".")


def crear_app(ruta_db=datos.RUTA_DB):
    app = Flask(__name__)
    app.jinja_env.filters["pesos"] = pesos

    def con():
        if "con" not in g:
            g.con = datos.conectar(ruta_db)
        return g.con

    @app.teardown_appcontext
    def cerrar(_error):
        conexion = g.pop("con", None)
        if conexion is not None:
            conexion.close()

    @app.errorhandler(inv.ErrorInventario)
    def error_inventario(error):
        return jsonify(error=str(error)), CODIGOS.get(type(error), 400)

    def cuerpo():
        return request.get_json(silent=True) or {}

    # Pantallas

    @app.get("/")
    def pantalla_productos():
        buscar = request.args.get("buscar", "")
        productos = datos.listar_productos(con(), buscar)
        return render_template("productos.html", productos=productos, buscar=buscar)

    @app.get("/editar/<int:id_producto>")
    def pantalla_editar(id_producto):
        producto = con().execute(
            "SELECT * FROM producto WHERE id_producto = ? AND activo = 1",
            (id_producto,),
        ).fetchone()
        if producto is None:
            return render_template("base.html", error="Ese producto no existe"), 404
        return render_template(
            "editar.html",
            producto=producto,
            entradas=datos.listar_entradas(con(), id_producto),
        )

    @app.get("/ventas")
    def pantalla_ventas():
        return render_template(
            "ventas.html",
            productos=datos.listar_productos(con()),
            ventas=datos.listar_ventas(con()),
        )

    @app.get("/reporte")
    def pantalla_reporte():
        mes = request.args.get("mes") or date.today().strftime("%Y-%m")
        try:
            resultado = datos.reporte_mensual(con(), mes)
        except ValueError as error:
            return render_template("base.html", error=str(error)), 400
        detalle = datos.ventas_del_mes(con(), mes)
        anio, numero = mes.split("-")
        return render_template(
            "reporte.html",
            reporte=resultado,
            detalle=detalle,
            dias=datos.ventas_por_dia(detalle, mes),
            nombre_mes=f"{MESES[int(numero) - 1]} de {anio}",
            unidades=sum(fila["cantidad"] for fila in detalle),
            num_ventas=len({fila["id_venta"] for fila in detalle}),
        )

    # Rutas JSON (Diseño S4, sección 6)

    @app.get("/productos")
    def buscar_productos():
        filas = datos.listar_productos(con(), request.args.get("buscar", ""))
        return jsonify([dict(fila) for fila in filas])

    @app.post("/productos")
    def crear_producto():
        d = cuerpo()
        id_producto = datos.crear_producto(
            con(),
            d.get("nombre"),
            d.get("precio_venta"),
            d.get("stock_actual"),
        )
        return jsonify(id_producto=id_producto), 201

    @app.put("/productos/<int:id_producto>")
    def editar_producto(id_producto):
        d = cuerpo()
        datos.editar_producto(
            con(), id_producto, d.get("nombre"), d.get("precio_venta")
        )
        return jsonify(mensaje="Producto actualizado")

    @app.delete("/productos/<int:id_producto>")
    def eliminar_producto(id_producto):
        datos.eliminar_producto(con(), id_producto)
        return jsonify(mensaje="Producto eliminado")

    @app.post("/entradas")
    def registrar_entrada():
        d = cuerpo()
        stock = datos.registrar_entrada(
            con(), d.get("id_producto"), d.get("cantidad"), d.get("fecha")
        )
        return jsonify(stock_actual=stock), 201

    @app.post("/ventas")
    def registrar_venta():
        d = cuerpo()
        id_venta, total = datos.registrar_venta(con(), d.get("items"), d.get("fecha"))
        return jsonify(id_venta=id_venta, total=total), 201

    @app.patch("/ventas/<int:id_venta>/detalles/<int:id_detalle>")
    def corregir_venta(id_venta, id_detalle):
        total = datos.corregir_detalle(
            con(), id_venta, id_detalle, cuerpo().get("cantidad")
        )
        return jsonify(total=total)

    @app.get("/reportes/mensual")
    def reporte_mensual():
        try:
            return jsonify(datos.reporte_mensual(con(), request.args.get("mes")))
        except ValueError as error:
            return jsonify(error=str(error)), 400

    return app


def main():
    app = crear_app()
    # Abre el navegador un segundo después, cuando el servidor ya arrancó
    threading.Timer(1, webbrowser.open, [f"http://localhost:{PUERTO}"]).start()
    print(f"CRUD R2K abierto en http://localhost:{PUERTO}")
    print("No cierre esta ventana mientras use la aplicación.")
    app.run(host="127.0.0.1", port=PUERTO)


if __name__ == "__main__":
    main()
