import pandas as pd
import requests
from datetime import datetime

URL = "https://sitr.cnd.com.pa/m/pub/gen.html"
OUTPUT_FILE = "generacion_panama.csv"

# Descargar todas las tablas de la página
tables = pd.read_html(URL)

# Fecha y hora actuales
ahora = datetime.now()
fecha = ahora.strftime("%Y-%m-%d")
hora = ahora.strftime("%H:%M:%S")

dfs = []
categorias = ["Hidroeléctricas", "Térmicas", "Solares", "Eólicas"]

for cat, tbl in zip(categorias, tables[3:7]):  # ojo: en esa web las tablas de centrales empiezan más adelante
    df = tbl.copy()
    df.columns = ["Central", "MW"]  # renombrar columnas
    df["Fecha"] = fecha
    df["Hora"] = hora
    df["Categoría"] = cat
    dfs.append(df)

# Unir todas las tablas
final_df = pd.concat(dfs, ignore_index=True)

# Ordenar columnas
final_df = final_df[["Fecha", "Hora", "Categoría", "Central", "MW"]]

# Guardar acumulando
try:
    old = pd.read_csv(OUTPUT_FILE)
    final_df = pd.concat([old, final_df], ignore_index=True)
except FileNotFoundError:
    pass

final_df.to_csv(OUTPUT_FILE, index=False)

print(f"✅ Datos guardados en {OUTPUT_FILE}")
