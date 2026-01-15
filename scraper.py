import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta, timezone
import os

def scrape_mag():
    url = "https://www.mercadoagroganadero.com.ar/dll/inicio.dll"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        data = {}
        
        # Buscar el contenedor de datos
        container = soup.find('div', class_='container-xl data')
        if not container:
            print("No se encontró el contenedor de datos")
            return None
            
        # Extraer la fecha (está justo antes del contenedor)
        date_el = container.find_previous('div')
        if date_el:
            data['fecha_reporte'] = date_el.get_text(strip=True)
        
        # Extraer los items de forma más precisa
        items = container.find_all('div', class_='item')
        for item in items:
            # Buscar los spans específicos si existen
            spans = item.find_all('span', class_=['home-data', 'home-data-2'])
            if len(spans) >= 2:
                value = spans[0].get_text(strip=True)
                label = spans[1].get_text(strip=True)
                data[label] = value
            else:
                # Fallback al método anterior si la estructura cambia
                text_parts = [p.strip() for p in item.get_text(separator='\n').split('\n') if p.strip()]
                if len(text_parts) >= 2:
                    value = text_parts[0]
                    label = text_parts[1]
                    data[label] = value
        
        # Configurar horario de Argentina (GMT-3)
        tz_ar = timezone(timedelta(hours=-3))
        now_ar = datetime.now(tz_ar)
        data['ultima_actualizacion'] = now_ar.strftime("%Y-%m-%d %H:%M:%S ART")
        
        return data

    except Exception as e:
        print(f"Error durante el scraping: {e}")
        return None

if __name__ == "__main__":
    result = scrape_mag()
    if result:
        with open('mercado_agroganadero.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)
        print("Datos guardados exitosamente en mercado_agroganadero.json")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("No se pudieron obtener los datos.")
