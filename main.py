from fastapi import FastAPI
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import pytz
import re
from urllib.parse import urljoin

app = FastAPI()

async def get_seace_data():
    base_url = "https://prod6.seace.gob.pe/buscador-publico/contrataciones"
    tz_peru = pytz.timezone('America/Lima')
    ahora_peru = datetime.now(tz_peru)
    licitaciones_totales = []

    async with async_playwright() as p:
        # Importante: --no-sandbox es vital para Docker/Render
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        try:
            await page.goto(base_url, wait_until="networkidle", timeout=60000)
            pagina = 1
            while len(licitaciones_totales) < 5 and pagina <= 5:
                await page.wait_for_selector("div.bg-fondo-section", timeout=20000)
                content = await page.content()
                soup = BeautifulSoup(content, "html.parser")
                cards = soup.select("div.bg-fondo-section.rounded-md.p-5")

                for card in cards:
                    if len(licitaciones_totales) >= 5: break
                    if "Vigente" not in card.get_text(): continue

                    link_tag = card.find("a", href=re.compile(r"/buscador-publico/contrataciones/\d+"))
                    enlace = urljoin("https://prod6.seace.gob.pe", link_tag["href"]) if link_tag else "N/A"

                    p_tags = card.select("p")
                    entidad = p_tags[1].get_text(strip=True) if len(p_tags) > 1 else "N/A"
                    desc_raw = p_tags[2].get_text(strip=True) if len(p_tags) > 2 else "N/A"
                    desc = re.sub(r"^(Servicio:|Bien:|Obra:|Consultoría:)\s*", "", desc_raw, flags=re.IGNORECASE)

                    cotiz_text = next((p.get_text() for p in p_tags if "Cotizaciones:" in p.get_text()), "")
                    fechas = re.findall(r"(\d{2}/\d{2}/\d{4})", cotiz_text)

                    dias_label = "Cerrando..."
                    if len(fechas) >= 2:
                        diff = (datetime.strptime(fechas[1], "%d/%m/%Y").date() - ahora_peru.date()).days
                        dias_label = f"{diff} días restantes" if diff > 0 else ("Vence HOY" if diff == 0 else "Cerrando...")

                    licitaciones_totales.append({
                        "titulo": desc[:85] + "...",
                        "entidad": entidad,
                        "tiempo": dias_label,
                        "link": enlace
                    })

                if len(licitaciones_totales) < 5:
                    btn_next = await page.query_selector("button.mat-mdc-paginator-navigation-next")
                    if btn_next and await btn_next.is_enabled():
                        await btn_next.click()
                        pagina += 1
                        await page.wait_for_timeout(3000)
                    else: break
            return licitaciones_totales
        finally:
            await browser.close()

@app.get("/licitaciones")
async def read_licitaciones():
    data = await get_seace_data()
    return {"status": "success", "data": data}

@app.get("/")
def home():
    return {"message": "API de Licitaciones SEACE activa"}