from dataclasses import dataclass


class StockInsuficienteError(Exception):
    pass


class CantidadInvalidaError(Exception):
    pass


class ProductoNoEncontradoError(Exception):
    pass


@dataclass
class Producto:
    id_producto: int
    nombre: str
    precio_compra: int  # pesos colombianos, entero (nunca float)
    precio_venta: int
    stock_actual: int


def registrar_salida(productos, id_producto, cantidad):
    if id_producto not in productos:
        raise ProductoNoEncontradoError(f"No existe el producto {id_producto}")
    if cantidad <= 0:
        raise CantidadInvalidaError(f"Cantidad inválida: {cantidad}")
    p = productos[id_producto]
    if cantidad > p.stock_actual:
        raise StockInsuficienteError(
            f"{p.nombre}: stock {p.stock_actual}, se pidieron {cantidad}"
        )
    p.stock_actual = p.stock_actual - cantidad
    return p.stock_actual