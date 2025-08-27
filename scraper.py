import requests
import re
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup

URL = "https://sitr.cnd.com.pa/m/pub/gen.html"
OUTPUT_FILE = "generacion_panama.csv"

# Descargar HTML de la página
res = requests.get(URL, timeout=30)
res.encoding = "utf-8"
soup = BeautifulSoup(res.text, "html.parser")

# Extraer todo el texto plano con saltos de línea
contenido = soup.get_text("\n")
lineas = contenido.split("\n")

# Patrón para detectar centrales con valor MW al final
patron = re.compile(r"^(.*?)\s+(-?\d+\.\d+|-?\d+)$")

# Fecha y hora actuales
ahora = datetime.now()
fecha = ahora.strftime("%Y-%m-%d")
hora = ahora.strftime("%H:%M:%S")

datos = []
categoria = None

for linea in lineas:
    linea_strip = linea.strip()

    # Detectar categorías
    if "Hidroeléctricas" in linea_strip:
        categoria = "Hidroeléctricas"; continue
    elif "Térmicas" in linea_strip:
        categoria = "Térmicas"; continue
    elif "Solares" in linea_strip:
        categoria = "Solares"; continue
    elif "Eólicas" in linea_strip:
        categoria = "Eólicas"; continue

    # Detectar central con MW
    match = patron.match(linea_strip)
    if match and categoria:
        central = match.group(1).strip()
        valor = float(match.group(2))
        datos.append([fecha, hora, categoria, central, valor])

# Crear DataFrame
df = pd.DataFrame(datos, columns=["Fecha", "Hora", "Categoría", "Central", "MW"])

# Guardar en CSV acumulando (no sobrescribe)
try:
    old = pd.read_csv(OUTPUT_FILE)
    df = pd.concat([old, df], ignore_index=True)
except FileNotFoundError:
    pass

df.to_csv(OUTPUT_FILE, index=False)
print(f"✅ Datos guardados en {OUTPUT_FILE}")

