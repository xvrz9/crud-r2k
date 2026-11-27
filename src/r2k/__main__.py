"""Demo por consola: python -m r2k"""

from r2k.inventario import ErrorInventario, Producto, registrar_salida


def ejecutar_demo():
    productos = {
        1: Producto(1, "Casco integral", 120000, 180000, 10),
        2: Producto(2, "Guantes de moto", 25000, 40000, 5),
    }

    nuevo_stock = registrar_salida(productos, 1, 3)
    print(f"Venta de 3 x Casco integral -> stock: {nuevo_stock}")

    try:
        registrar_salida(productos, 2, 8)
    except ErrorInventario as error:
        print(f"Venta de 8 x Guantes de moto rechazada -> {error}")
    print(f"Stock de Guantes de moto: {productos[2].stock_actual}")


if __name__ == "__main__":
    ejecutar_demo()
