"""
scraper.py - Extrae información del sitio web de FIME-UANL usando Selenium.
Usa Selenium Manager (Selenium 4.6+) para gestionar el driver automáticamente.
Ejecutar: python scraper.py
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Configuración ---
DOCS_DIR = "docs"
DELAY = 2  # segundos de espera entre páginas

# Lista de URLs principales de FIME (sin noticias)
URLS = [
    "https://www.fime.uanl.mx/",
    "https://www.fime.uanl.mx/la-fime/",
    "https://www.fime.uanl.mx/politica-y-objetivos-de-calidad-del-sistema-de-gestion-integral/",
    "https://www.fime.uanl.mx/mensaje-del-director/",
    "https://www.fime.uanl.mx/reconocimientos-premios-y-distinciones/",
    "https://www.fime.uanl.mx/desarrollo-institucional/",
    "https://www.fime.uanl.mx/subdireccion-de-desarrollo-sostenible-y-responsabilidad-social/",
    "https://www.fime.uanl.mx/mapa-de-la-fime/",
    "https://www.fime.uanl.mx/contacto/",
    "https://www.fime.uanl.mx/programas-educativos/",
    "https://www.fime.uanl.mx/oferta-educativa-para-posgrado/",
    "https://www.fime.uanl.mx/educacion_continua_y_caadi/",
    "https://www.fime.uanl.mx/sevicios-escolares/",
    "https://www.fime.uanl.mx/tramites/",
    "https://www.fime.uanl.mx/calendario-academico/",
    "https://www.fime.uanl.mx/afis/",
    "https://www.fime.uanl.mx/asuntos-estudiantiles/",
    "https://www.fime.uanl.mx/cultura/",
    "https://www.fime.uanl.mx/coordinacion-de-deportes/",
    "https://www.fime.uanl.mx/bibliotecas/",
    "https://www.fime.uanl.mx/grupos-estudiantiles/",
    "https://www.fime.uanl.mx/material-clase/",
    "https://www.fime.uanl.mx/merito-academico/",
    "https://www.fime.uanl.mx/comitedelamujer/",
    "https://www.fime.uanl.mx/cuerpos-academicos/",
    "https://www.fime.uanl.mx/centros-de-investigacion/",
    "https://www.fime.uanl.mx/proyectos-de-investigacion-4/",
    "https://www.fime.uanl.mx/publicaciones/",
    "https://www.fime.uanl.mx/revistas/",
    "https://www.fime.uanl.mx/estrategias-vinculacion/",
    "https://www.fime.uanl.mx/conocer/",
    "https://www.fime.uanl.mx/centros-de-computo-2/",
    "https://www.fime.uanl.mx/laboratorios/",
    "https://www.fime.uanl.mx/servicios-tecnologicos/",
    "https://www.fime.uanl.mx/estrategias-de-vinculacion/",
    "https://www.fime.uanl.mx/becas/",
]


def configurar_driver():
    """Configura Chrome en modo headless. Selenium Manager descarga el driver solo."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--log-level=3")  # silenciar logs de Chrome
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    # Selenium Manager (Selenium 4.6+) resuelve el driver automáticamente
    return webdriver.Chrome(options=options)


def extraer_texto(driver, url):
    """Carga la URL, espera a que cargue el JS y extrae el texto visible."""
    try:
        driver.get(url)
        # Esperar a que el body esté presente
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        # Margen adicional para que cargue contenido dinámico
        time.sleep(2)

        # Intentar extraer solo el contenido principal (menos ruido)
        candidatos = [
            "main",
            "article",
            "div.entry-content",
            "div.site-content",
            "div#content",
            "div.content",
        ]
        texto = ""
        for selector in candidatos:
            try:
                elem = driver.find_element(By.CSS_SELECTOR, selector)
                t = elem.text.strip()
                if len(t) > len(texto):
                    texto = t
            except Exception:
                continue

        # Si no encontramos contenedor, extraer todo el body
        if not texto:
            texto = driver.find_element(By.TAG_NAME, "body").text

        # Limpiar líneas vacías
        lineas = [l.strip() for l in texto.splitlines() if l.strip()]
        return "\n".join(lineas)

    except Exception as e:
        print(f"  ⚠ Error en {url}: {e}")
        return ""


def guardar_documento(url, texto, contador):
    """Guarda el texto extraído en un archivo .txt."""
    os.makedirs(DOCS_DIR, exist_ok=True)
    nombre = f"doc_{contador:03d}.txt"
    ruta = os.path.join(DOCS_DIR, nombre)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(f"URL: {url}\n\n{texto}")
    return ruta


def main():
    print("=" * 60)
    print("SCRAPER FIME-UANL (SELENIUM + JAVASCRIPT)")
    print("=" * 60)

    # Limpiar docs anteriores
    if os.path.exists(DOCS_DIR):
        import shutil
        shutil.rmtree(DOCS_DIR)
        print(f"🗑  Carpeta '{DOCS_DIR}/' limpiada")

    print("\n🚀 Iniciando Chrome en modo headless...")
    driver = configurar_driver()
    print("  ✅ Driver listo")

    contador = 0
    try:
        for i, url in enumerate(URLS, 1):
            print(f"\n[{i}/{len(URLS)}] {url}")
            texto = extraer_texto(driver, url)
            if texto and len(texto) > 200:
                contador += 1
                ruta = guardar_documento(url, texto, contador)
                print(f"  ✅ Guardado ({len(texto)} caracteres)")
            else:
                print(f"  ⏭ Texto insuficiente ({len(texto)} caracteres), omitido")
            time.sleep(DELAY)
    finally:
        driver.quit()

    print("\n" + "=" * 60)
    print(f"✅ Proceso completado. {contador} documentos en '{DOCS_DIR}/'")
    print("💡 Ahora ejecuta: python vectorizar.py")
    print("=" * 60)


if __name__ == "__main__":
    main()