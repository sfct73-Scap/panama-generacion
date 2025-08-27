import time
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from datetime import datetime

URL = "https://sitr.cnd.com.pa/m/pub/gen.html"
OUTPUT_FILE = "generacion_panama.csv"

options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.binary_location = "/usr/bin/chromium-browser"  # en GitHub Actions se instala Chromium

# Usar Service en lugar de executable_path
service = Service("/usr/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=options)

driver.get(URL)
time.sleep(5)

contenido = driver.find_element(By.TAG_NAME, "body").text
driver.quit()

lineas = contenido.split("\n")
patron = re.compile(r"^(.*?)\s+(-?\d+\.\d+|-?\d+)$")

ahora = datetime.now()
fecha = ahora.strftime("%Y-%m-%d")
hora = ahora.strftime("%H:%M:%S")

datos = []
categoria = None
for linea in lineas:
    linea_strip = linea.strip()
    if "Hidroeléctricas" in linea_strip:
        categoria = "Hidroeléctricas"; continue
    elif "Térmicas" in linea_strip:
        categoria = "Térmicas"; continue
    elif "Solares" in linea_strip:
        categoria = "Solares"; continue
    elif "Eólicas" in linea_strip:
        categoria = "Eólicas"; continue

    match = patron.match(linea_strip)
    if match and categoria:
        central = match.group(1).strip()
        valor = float(match.group(2))
        datos.append([fecha, hora, categoria, central, valor])

df = pd.DataFrame(datos, columns=["Fecha","Hora","Categoría","Central","MW"])

# Guardar en CSV acumulando
try:
    old = pd.read_csv(OUTPUT_FILE)
    df = pd.concat([old, df], ignore_index=True)
except FileNotFoundError:
    pass

df.to_csv(OUTPUT_FILE, index=False)
print(f"✅ Datos guardados en {OUTPUT_FILE}")
