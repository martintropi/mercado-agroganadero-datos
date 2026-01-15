#!/usr/bin/env python3
"""
Scraper para Mercado Agroganadero - Dashboard Principal
Extrae datos de la pagina de inicio cada hora
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import sys
import re

class MAGDashboardScraper:
    """Scraper para el dashboard principal del MAG"""
    
    URL = "https://www.mercadoagroganadero.com.ar/dll/inicio.dll"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-AR,es;q=0.9'
        })
    
    def clean_number(self, text):
        """Limpia y convierte texto a numero"""
        if not text:
            return None
        cleaned = text.strip().replace('.', '').replace(',', '.').replace('%', '')
        try:
            if '.' in cleaned:
                return float(cleaned)
            return int(cleaned)
        except ValueError:
            return text.strip()
    
    def scrape_dashboard(self):
        """Obtiene los datos del dashboard principal"""
        try:
            print(f"Conectando a {self.URL}...")
            
            response = self.session.get(self.URL, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            datos = {
                'camiones': None,
                'cabezas': None,
                'cab_semana': None,
                'op': None,
                'inmag': None,
                'igmag': None,
                'indice_arrend': None,
                'dte_a_mag': None
            }
            
            # Buscar todos los enlaces con javascript:void(0)
            # Estos contienen los datos del dashboard
            links = soup.find_all('a', href='javascript:void(0);')
            
            for link in links:
                text = link.get_text(strip=True)
                text_upper = text.upper()
                
                # Separar el numero del label
                parts = text.split('\n')
                if len(parts) >= 2:
                    numero = parts[0].strip()
                    label = parts[1].strip().upper()
                    
                    if 'CAMIONES' in label:
                        datos['camiones'] = self.clean_number(numero)
                    elif 'CABEZAS' in label and 'SEMANA' not in label:
                        datos['cabezas'] = self.clean_number(numero)
                    elif 'CAB.SEMANA' in label or 'SEMANA' in label:
                        datos['cab_semana'] = self.clean_number(numero)
                    elif label == 'OP':
                        datos['op'] = self.clean_number(numero)
                    elif 'INMAG' in label:
                        datos['inmag'] = self.clean_number(numero)
                    elif 'IGMAG' in label:
                        datos['igmag'] = self.clean_number(numero)
                    elif 'ARREND' in label:
                        datos['indice_arrend'] = self.clean_number(numero)
                    elif 'DTE' in label or 'MAG' in label:
                        datos['dte_a_mag'] = self.clean_number(numero)
            
            # Validar que obtuvimos datos
            valores_obtenidos = sum(1 for v in datos.values() if v is not None)
            print(f"\nDatos obtenidos: {valores_obtenidos}/8")
            
            if valores_obtenidos == 0:
                print("ERROR: No se obtuvieron datos")
                return None
            
            # Mostrar datos obtenidos
            print("\nResumen:")
            print(f"  Camiones: {datos['camiones']}")
            print(f"  Cabezas: {datos['cabezas']}")
            print(f"  Cab/Semana: {datos['cab_semana']}")
            print(f"  OP: {datos['op']}")
            print(f"  INMAG: {datos['inmag']}")
            print(f"  IGMAG: {datos['igmag']}")
            print(f"  Indice Arrend: {datos['indice_arrend']}")
            print(f"  DTe a MAG: {datos['dte_a_mag']}")
            
            return datos
            
        except Exception as e:
            print(f"Error al obtener datos: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def save_to_json(self, data, filename='mercado_agroganadero.json'):
        """Guarda los datos en formato JSON"""
        try:
            output = {
                'metadata': {
                    'fecha_actualizacion': datetime.now().isoformat(),
                    'fecha_actualizacion_legible': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                    'fuente': self.URL,
                    'descripcion': 'Datos del dashboard principal del Mercado Agroganadero'
                },
                'dashboard': data
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
            
            print(f"\nDatos guardados en '{filename}'")
            return True
        except Exception as e:
            print(f"Error al guardar archivo: {e}")
            return False


def main():
    """Funcion principal"""
    try:
        print("\n" + "=" * 70)
        print(f"Scraping MAG Dashboard - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        scraper = MAGDashboardScraper()
        datos = scraper.scrape_dashboard()
        
        if datos is None:
            print("\nERROR: No se pudieron obtener los datos")
            sys.exit(1)
        
        if scraper.save_to_json(datos):
            print("\nScraping completado exitosamente")
            print("=" * 70 + "\n")
            sys.exit(0)
        else:
            print("\nError al guardar los datos")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\nProceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\nError fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
