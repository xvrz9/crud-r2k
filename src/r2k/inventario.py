"""Reglas del inventario de R2K: productos y registro de ventas.

No usa base de datos. El inventario es un diccionario de id_producto a Producto.
"""

from dataclasses import dataclass

CANTIDAD_MINIMA_VENTA = 1
CAMPOS_ENTEROS = ("precio_compra", "precio_venta", "stock_actual")


class ErrorInventario(Exception):
    """Error base del inventario."""


class StockInsuficienteError(ErrorInventario):
    pass


class CantidadInvalidaError(ErrorInventario):
    pass


class ProductoNoEncontradoError(ErrorInventario):
    pass


class ProductoInvalidoError(ErrorInventario, ValueError):
    pass


def _es_entero(valor):
    # bool es subclase de int en Python, por eso se descarta aparte
    return isinstance(valor, int) and not isinstance(valor, bool)


@dataclass
class Producto:
    """Producto del inventario. Precios en pesos enteros."""

    id_producto: int
    nombre: str
    precio_compra: int
    precio_venta: int
    stock_actual: int

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
    if producto is None:
        raise ProductoNoEncontradoError(f"No existe el producto {id_producto}")
    return producto


def _validar_cantidad(cantidad):
    if not _es_entero(cantidad):
        raise CantidadInvalidaError(
            f"La cantidad debe ser un número entero (recibido: {cantidad!r})"
        )
    if cantidad < CANTIDAD_MINIMA_VENTA:
        raise CantidadInvalidaError(
            f"La cantidad debe ser al menos {CANTIDAD_MINIMA_VENTA} "
            f"(recibido: {cantidad})"
        )


def _validar_stock_suficiente(producto, cantidad):
    if cantidad > producto.stock_actual:
        raise StockInsuficienteError(
            f"{producto.nombre}: hay {producto.stock_actual} en stock "
            f"y se intentaron vender {cantidad}"
        )


def registrar_salida(productos, id_producto, cantidad):
    """Registra una venta y descuenta el stock (HU-06). Devuelve el nuevo stock.

    Si hay un error el stock no cambia.
    """
    producto = _buscar_producto(productos, id_producto)
    _validar_cantidad(cantidad)
    _validar_stock_suficiente(producto, cantidad)
    producto.stock_actual -= cantidad
    return producto.stock_actual
