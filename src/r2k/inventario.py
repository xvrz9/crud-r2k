import re
from dataclasses import dataclass

CANTIDAD_MINIMA = 1
CAMPOS_ENTEROS = ("precio_compra", "precio_venta", "stock_actual")
PRECIO_INVALIDO = "El precio de venta debe ser mayor que 0"


class ErrorInventario(Exception):
    pass


class StockInsuficienteError(ErrorInventario):
    pass


class CantidadInvalidaError(ErrorInventario):
    pass


class ProductoNoEncontradoError(ErrorInventario):
    pass


class ProductoInvalidoError(ErrorInventario, ValueError):
    pass


class ProductoConStockError(ErrorInventario):
    pass


class VentaNoEncontradaError(ErrorInventario):
    pass


def _es_entero(valor):
    return isinstance(valor, int) and not isinstance(valor, bool)


@dataclass
class Producto:
    id_producto: int
    nombre: str
    precio_compra: int
    precio_venta: int
    stock_actual: int
    activo: bool = True

    def __post_init__(self):
        for campo in CAMPOS_ENTEROS:
            valor = getattr(self, campo)
            if not _es_entero(valor) or valor < 0:
                raise ProductoInvalidoError(
                    f"{campo} debe ser un entero mayor o igual a 0 "
                    f"(recibido: {valor!r})"
                )


def _buscar_producto(productos, id_producto):
    producto = productos.get(id_producto)
    if producto is None or not producto.activo:
        raise ProductoNoEncontradoError(f"No existe el producto {id_producto}")
    return producto


def _validar_cantidad(cantidad):
    if not _es_entero(cantidad):
        raise CantidadInvalidaError(
            f"La cantidad debe ser un número entero (recibido: {cantidad!r})"
        )
    if cantidad < CANTIDAD_MINIMA:
        raise CantidadInvalidaError(f"La cantidad debe ser al menos {CANTIDAD_MINIMA}")


def _validar_stock_suficiente(producto, cantidad):
    if cantidad > producto.stock_actual:
        raise StockInsuficienteError(
            f"{producto.nombre}: hay {producto.stock_actual} en stock "
            f"y se intentaron vender {cantidad}"
        )


def validar_producto(nombre, precio_venta, stock_actual=0, mensaje=PRECIO_INVALIDO):
    if not isinstance(nombre, str) or not nombre.strip():
        raise ProductoInvalidoError("El nombre no puede estar vacío")
    if not _es_entero(precio_venta) or precio_venta <= 0:
        raise ProductoInvalidoError(mensaje)
    if not _es_entero(stock_actual) or stock_actual < 0:
        raise ProductoInvalidoError("La cantidad no puede ser negativa")


def registrar_salida(productos, id_producto, cantidad):
    producto = _buscar_producto(productos, id_producto)
    _validar_cantidad(cantidad)
    _validar_stock_suficiente(producto, cantidad)
    producto.stock_actual -= cantidad
    return producto.stock_actual


def registrar_entrada(productos, id_producto, cantidad):
    producto = _buscar_producto(productos, id_producto)
    _validar_cantidad(cantidad)
    producto.stock_actual += cantidad
    return producto.stock_actual


def corregir_venta(producto, cantidad_anterior, cantidad_nueva):
    _validar_cantidad(cantidad_nueva)
    _validar_stock_suficiente(producto, cantidad_nueva - cantidad_anterior)
    producto.stock_actual -= cantidad_nueva - cantidad_anterior
    return producto.stock_actual


def eliminar_producto(productos, id_producto):
    producto = _buscar_producto(productos, id_producto)
    if producto.stock_actual > 0:
        raise ProductoConStockError(
            f"No se puede eliminar: todavía tiene {producto.stock_actual} "
            "unidades en stock"
        )
    producto.activo = False


def reporte_mensual(ventas, mes):
    if not isinstance(mes, str) or not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", mes):
        raise ValueError(f"El mes debe tener la forma AAAA-MM (recibido: {mes!r})")

    resumen = {}
    for fecha, nombre, cantidad, precio in ventas:
        if not fecha.startswith(mes + "-"):
            continue
        fila = resumen.setdefault(nombre, {"nombre": nombre, "cantidad": 0, "valor": 0})
        fila["cantidad"] += cantidad
        fila["valor"] += cantidad * precio

    productos = list(resumen.values())
    total = sum(fila["valor"] for fila in productos)
    return {"mes": mes, "productos": productos, "total_vendido": total}
