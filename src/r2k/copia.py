import sqlite3
import sys
from datetime import date
from pathlib import Path

from r2k.datos import RUTA_DB


def copiar(ruta_db, destino, hoy=None):
    ruta_db = Path(ruta_db)
    if not ruta_db.exists():
        raise FileNotFoundError(f"No se encontró la base de datos en {ruta_db}")
    destino = Path(destino)
    if not destino.exists():
        raise FileNotFoundError(f"No se encontró {destino}. ¿Está conectada la USB?")

    carpeta = destino / "R2K_copias"
    carpeta.mkdir(exist_ok=True)
    archivo = carpeta / f"r2k_{hoy or date.today().isoformat()}.db"

    origen = sqlite3.connect(ruta_db)
    copia = sqlite3.connect(archivo)
    origen.backup(copia)
    origen.close()
    copia.close()
    return archivo


def main():
    if len(sys.argv) > 1:
        letra = sys.argv[1]
    else:
        letra = input("Letra de la memoria USB (por ejemplo E): ")
    destino = letra.strip()[:1].upper() + ":\\"
    try:
        archivo = copiar(RUTA_DB, destino)
    except FileNotFoundError as error:
        print(error)
        return 1
    print(f"Copia guardada en {archivo}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
