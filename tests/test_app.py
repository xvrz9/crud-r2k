import pytest

from r2k import datos
from r2k.app import crear_app


@pytest.fixture
def ruta_db(tmp_path):
    return tmp_path / "prueba.db"


@pytest.fixture
def cliente(ruta_db):
    return crear_app(ruta_db).test_client()


def crear(cliente, nombre, venta, cantidad):
    resp = cliente.post(
        "/productos",
        json={"nombre": nombre, "precio_venta": venta, "stock_actual": cantidad},
    )
    assert resp.status_code == 201
    return resp.get_json()["id_producto"]


def vender(cliente, id_producto, cantidad, fecha="2026-11-10"):
    items = [{"id_producto": id_producto, "cantidad": cantidad}]
    return cliente.post("/ventas", json={"items": items, "fecha": fecha})


def lista(cliente, buscar=""):
    return cliente.get(f"/productos?buscar={buscar}").get_json()


def stock(cliente, id_producto):
    for producto in lista(cliente):
        if producto["id_producto"] == id_producto:
            return producto["stock_actual"]
    return None


def reporte(cliente, mes):
    return cliente.get(f"/reportes/mensual?mes={mes}")


# HU-01 crear producto


def test_hu01_producto_registrado_aparece_en_la_lista(cliente):
    crear(cliente, "Sticker reflectivo para casco", 8000, 20)
    producto = lista(cliente)[0]
    assert producto["nombre"] == "Sticker reflectivo para casco"
    assert producto["precio_venta"] == 8000
    assert producto["stock_actual"] == 20


def test_hu01_precio_de_venta_cero_no_se_guarda(cliente):
    resp = cliente.post(
        "/productos",
        json={
            "nombre": "Sticker reflectivo para casco",
            "precio_venta": 0,
            "stock_actual": 20,
        },
    )
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "El precio de venta debe ser mayor que 0"
    assert lista(cliente) == []


@pytest.mark.parametrize(
    "nombre, venta, cantidad",
    [
        ("", 8000, 20),
        ("Sticker", "8000", 20),
        ("Sticker", 8000, -1),
    ],
)
def test_hu01_datos_invalidos_no_se_guardan(cliente, nombre, venta, cantidad):
    resp = cliente.post(
        "/productos",
        json={"nombre": nombre, "precio_venta": venta, "stock_actual": cantidad},
    )
    assert resp.status_code == 400
    assert lista(cliente) == []


# HU-02 buscar producto


def test_hu02_busqueda_muestra_solo_los_que_coinciden(cliente):
    crear(cliente, "Espejo retrovisor", 25000, 8)
    crear(cliente, "Casco integral", 180000, 10)
    encontrados = lista(cliente, "espejo")
    assert len(encontrados) == 1
    assert encontrados[0]["nombre"] == "Espejo retrovisor"
    assert encontrados[0]["precio_venta"] == 25000
    assert encontrados[0]["stock_actual"] == 8


def test_hu02_busqueda_sin_resultados(cliente):
    crear(cliente, "Espejo retrovisor", 25000, 8)
    assert lista(cliente, "xyz123") == []
    pagina = cliente.get("/?buscar=xyz123").get_data(as_text=True)
    assert "No se encontraron productos" in pagina


# HU-03 editar producto


def test_hu03_precio_nuevo_no_cambia_las_ventas_anteriores(cliente):
    casco = crear(cliente, "Casco abierto", 120000, 10)
    for _ in range(3):
        vender(cliente, casco, 1)
    resp = cliente.put(
        f"/productos/{casco}",
        json={"nombre": "Casco abierto", "precio_venta": 135000},
    )
    assert resp.status_code == 200
    vender(cliente, casco, 1)
    fila = reporte(cliente, "2026-11").get_json()["productos"][0]
    assert fila["cantidad"] == 4
    assert fila["valor"] == 3 * 120000 + 135000


def test_hu03_precio_negativo_se_rechaza(cliente):
    casco = crear(cliente, "Casco abierto", 120000, 10)
    resp = cliente.put(
        f"/productos/{casco}",
        json={"nombre": "Casco abierto", "precio_venta": -5000},
    )
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "El precio de venta debe ser mayor que 0"
    assert lista(cliente)[0]["precio_venta"] == 120000


def test_hu03_editar_producto_que_no_existe(cliente):
    resp = cliente.put(
        "/productos/99",
        json={"nombre": "X", "precio_venta": 2},
    )
    assert resp.status_code == 404


# HU-04 eliminar producto agotado


def test_hu04_producto_agotado_se_elimina_y_sigue_en_el_reporte(cliente):
    cubre = crear(cliente, "Cubre manubrio", 15000, 1)
    vender(cliente, cubre, 1, fecha="2026-10-15")
    resp = cliente.delete(f"/productos/{cubre}")
    assert resp.status_code == 200
    assert lista(cliente) == []
    fila = reporte(cliente, "2026-10").get_json()["productos"][0]
    assert fila["nombre"] == "Cubre manubrio"


def test_hu04_producto_con_stock_no_se_elimina(cliente):
    espejo = crear(cliente, "Espejo retrovisor", 25000, 4)
    resp = cliente.delete(f"/productos/{espejo}")
    assert resp.status_code == 409
    assert resp.get_json()["error"] == (
        "No se puede eliminar: todavía tiene 4 unidades en stock"
    )
    assert stock(cliente, espejo) == 4


# HU-05 entradas de mercancía


def test_hu05_entrada_sube_el_stock_y_se_guarda(cliente, ruta_db):
    guaya = crear(cliente, "Guaya de freno", 8000, 2)
    resp = cliente.post(
        "/entradas",
        json={"id_producto": guaya, "cantidad": 10, "fecha": "2026-11-20"},
    )
    assert resp.status_code == 201
    assert stock(cliente, guaya) == 12
    con = datos.conectar(ruta_db)
    entrada = datos.listar_entradas(con, guaya)[0]
    con.close()
    assert (entrada["fecha"], entrada["cantidad"]) == ("2026-11-20", 10)


def test_hu05_cantidad_cero_no_cambia_el_stock(cliente):
    guaya = crear(cliente, "Guaya de freno", 8000, 2)
    resp = cliente.post("/entradas", json={"id_producto": guaya, "cantidad": 0})
    assert resp.status_code == 400
    assert "La cantidad debe ser al menos 1" in resp.get_json()["error"]
    assert stock(cliente, guaya) == 2


# HU-06 ventas


def test_hu06_venta_guarda_el_total_y_baja_el_stock(cliente):
    espejo = crear(cliente, "Espejo retrovisor", 25000, 8)
    resp = vender(cliente, espejo, 2)
    assert resp.status_code == 201
    assert resp.get_json()["total"] == 50000
    assert stock(cliente, espejo) == 6


def test_hu06_venta_mayor_al_stock_no_se_guarda(cliente):
    guaya = crear(cliente, "Guaya de freno", 8000, 1)
    resp = vender(cliente, guaya, 3)
    assert resp.status_code == 409
    assert resp.get_json()["error"] == "Stock insuficiente: solo hay 1 unidad"
    assert stock(cliente, guaya) == 1
    assert reporte(cliente, "2026-11").get_json()["total_vendido"] == 0


def test_hu06_vender_producto_que_no_existe(cliente):
    assert vender(cliente, 99, 1).status_code == 404


# HU-08 corregir una venta


def detalle_de_la_venta(ruta_db, id_venta):
    con = datos.conectar(ruta_db)
    fila = con.execute(
        "SELECT id_detalle FROM detalle_venta WHERE id_venta = ?", (id_venta,)
    ).fetchone()
    con.close()
    return fila["id_detalle"]


def test_hu08_corregir_cantidad_ajusta_total_y_stock(cliente, ruta_db):
    guaya = crear(cliente, "Guaya de freno", 8000, 5)
    id_venta = vender(cliente, guaya, 2).get_json()["id_venta"]
    id_detalle = detalle_de_la_venta(ruta_db, id_venta)
    resp = cliente.patch(
        f"/ventas/{id_venta}/detalles/{id_detalle}", json={"cantidad": 1}
    )
    assert resp.status_code == 200
    assert resp.get_json()["total"] == 8000
    assert stock(cliente, guaya) == 4


def test_hu08_cantidad_cero_deja_la_venta_igual(cliente, ruta_db):
    guaya = crear(cliente, "Guaya de freno", 8000, 5)
    id_venta = vender(cliente, guaya, 2).get_json()["id_venta"]
    id_detalle = detalle_de_la_venta(ruta_db, id_venta)
    resp = cliente.patch(
        f"/ventas/{id_venta}/detalles/{id_detalle}", json={"cantidad": 0}
    )
    assert resp.status_code == 400
    assert "La cantidad debe ser al menos 1" in resp.get_json()["error"]
    assert reporte(cliente, "2026-11").get_json()["total_vendido"] == 16000
    assert stock(cliente, guaya) == 3


def test_hu08_corregir_a_mas_de_lo_que_hay_falla(cliente, ruta_db):
    guaya = crear(cliente, "Guaya de freno", 8000, 3)
    id_venta = vender(cliente, guaya, 2).get_json()["id_venta"]
    id_detalle = detalle_de_la_venta(ruta_db, id_venta)
    resp = cliente.patch(
        f"/ventas/{id_venta}/detalles/{id_detalle}", json={"cantidad": 5}
    )
    assert resp.status_code == 409
    assert stock(cliente, guaya) == 1


# HU-10 reporte mensual


def test_hu10_reporte_de_noviembre(cliente):
    casco = crear(cliente, "Casco integral", 180000, 10)
    guantes = crear(cliente, "Guantes de moto", 40000, 10)
    espejo = crear(cliente, "Espejo retrovisor", 25000, 10)
    vender(cliente, casco, 1, fecha="2026-10-31")
    vender(cliente, casco, 2, fecha="2026-11-01")
    vender(cliente, guantes, 5, fecha="2026-11-03")
    vender(cliente, casco, 1, fecha="2026-11-15")
    vender(cliente, espejo, 2, fecha="2026-11-30")
    vender(cliente, guantes, 1, fecha="2026-12-01")
    resultado = reporte(cliente, "2026-11").get_json()
    assert resultado["total_vendido"] == 790000
    assert {"nombre": "Casco integral", "cantidad": 3, "valor": 540000} in resultado[
        "productos"
    ]
    assert {"nombre": "Guantes de moto", "cantidad": 5, "valor": 200000} in resultado[
        "productos"
    ]
    assert {"nombre": "Espejo retrovisor", "cantidad": 2, "valor": 50000} in resultado[
        "productos"
    ]


def test_hu10_mes_sin_ventas(cliente):
    resultado = reporte(cliente, "2026-12").get_json()
    assert resultado["total_vendido"] == 0
    assert resultado["productos"] == []
    pagina = cliente.get("/reporte?mes=2026-12").get_data(as_text=True)
    assert "No hay ventas en este mes" in pagina
    assert "$0" in pagina


def test_hu10_mes_invalido(cliente):
    assert reporte(cliente, "2026-13").status_code == 400


# Pantallas


@pytest.mark.parametrize("url", ["/", "/ventas", "/reporte"])
def test_las_pantallas_abren(cliente, url):
    assert cliente.get(url).status_code == 200
