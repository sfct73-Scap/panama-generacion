import time
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from datetime import datetime
from zoneinfo import ZoneInfo

URL = "https://sitr.cnd.com.pa/m/pub/gen.html"
OUTPUT_FILE = "generacion_panama.csv"
LOG_FILE = "scraper_log.csv"

# Medir tiempo de inicio
t0 = time.time()
status = "OK"

try:
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = "/usr/bin/chromium-browser"  # GitHub Actions

    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(URL)
    time.sleep(5)

    contenido = driver.find_element(By.TAG_NAME, "body").text
    driver.quit()

    lineas = contenido.split("\n")
    patron = re.compile(r"^(.*?)\s+(-?\d+\.\d+|-?\d+)$")

    # Hora local de Guatemala
    ahora = datetime.now(ZoneInfo("America/Guatemala"))
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

except Exception as e:
    status = f"ERROR: {e}"

finally:
    # Medir duración y registrar en log
    t1 = time.time()
    duracion = round(t1 - t0, 2)

    ahora = datetime.now(ZoneInfo("America/Guatemala"))
    log_entry = pd.DataFrame([[ahora.strftime("%Y-%m-%d"), 
                               ahora.strftime("%H:%M:%S"),
                               duracion, status]],
                             columns=["Fecha","Hora","Duración_seg","Status"])

    try:
        old_log = pd.read_csv(LOG_FILE)
        log_entry = pd.concat([old_log, log_entry], ignore_index=True)
    except FileNotFoundError:
        pass

    log_entry.to_csv(LOG_FILE, index=False)

    print(f"✅ Datos guardados en {OUTPUT_FILE}")
    print(f"📝 Log actualizado en {LOG_FILE} (duración {duracion}s, estado {status})")
