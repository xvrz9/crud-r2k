import pytest

from r2k.inventario import Producto


@pytest.fixture
def catalogo():
    return {
        1: Producto(1, "Guantes Ñandú", 25000, 40000, 5),
        2: Producto(2, "Casco D'Angelo", 120000, 180000, 10),
        3: Producto(3, "Impermeable Tía Rosa", 35000, 55000, 0),
        4: Producto(4, "", 8000, 12000, 3),
        5: Producto(5, "Calcomanía R2K", 0, 0, 50),
        6: Producto(6, "Llavero de moto", 5000, 5000, 20),
        7: Producto(7, "Visor polarizado en liquidación", 30000, 20000, 4),
    }
