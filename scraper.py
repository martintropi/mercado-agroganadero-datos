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
                'CAMIONES': None,
                'CABEZAS': None,
                'CAB.SEMANA': None,
                'OP': None,
                'INMAG': None,
                'IGMAG': None,
                'ÍNDICE ARREND.': None,
                'DTe a MAG': None
            }
            
            # Buscar todos los enlaces con javascript:void(0)
            links = soup.find_all('a', href='javascript:void(0);')
            
            for link in links:
                text = link.get_text(strip=True)
                
                # Separar el numero del label
                parts = text.split('\n')
                if len(parts) >= 2:
                    numero = parts[0].strip()
                    label = parts[1].strip().upper()
                    
                    if 'CAMIONES' in label:
                        datos['CAMIONES'] = self.clean_number(numero)
                    elif 'CABEZAS' in label and 'SEMANA' not in label:
                        datos['CABEZAS'] = self.clean_number(numero)
                    elif 'CAB.SEMANA' in label or 'SEMANA' in label:
                        datos['CAB.SEMANA'] = self.clean_number(numero)
                    elif label == 'OP':
                        datos['OP'] = self.clean_number(numero)
                    elif 'INMAG' in label:
                        datos['INMAG'] = self.clean_number(numero)
                    elif 'IGMAG' in label:
                        datos['IGMAG'] = self.clean_number(numero)
                    elif 'ARREND' in label:
                        datos['ÍNDICE ARREND.'] = self.clean_number(numero)
                    elif 'DTE' in label or 'MAG' in label:
                        datos['DTe a MAG'] = self.clean_number(numero)
            
            # Validar que obtuvimos datos
            valores_obtenidos = sum(1 for v in datos.values() if v is not None)
            print(f"\nDatos obtenidos: {valores_obtenidos}/8")
            
            if valores_obtenidos == 0:
                print("ERROR: No se obtuvieron datos")
                return None
            
            # Mostrar datos obtenidos
            print("\nResumen:")
            print(f"  CAMIONES: {datos['CAMIONES']}")
            print(f"  CABEZAS: {datos['CABEZAS']}")
            print(f"  CAB.SEMANA: {datos['CAB.SEMANA']}")
            print(f"  OP: {datos['OP']}")
            print(f"  INMAG: {datos['INMAG']}")
            print(f"  IGMAG: {datos['IGMAG']}")
            print(f"  ÍNDICE ARREND.: {datos['ÍNDICE ARREND.']}")
            print(f"  DTe a MAG: {datos['DTe a MAG']}")
            
            return datos
            
        except Exception as e:
            print(f"Error al obtener datos: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def save_to_json(self, data, filename='mercado_agroganadero.json'):
        """Guarda los datos en formato JSON compatible con el frontend"""
        try:
            # Formato adaptado para el frontend React
            output = {
                'CAMIONES': data['CAMIONES'],
                'CABEZAS': data['CABEZAS'],
                'CAB.SEMANA': data['CAB.SEMANA'],
                'OP': data['OP'],
                'INMAG': data['INMAG'],
                'IGMAG': data['IGMAG'],
                'ÍNDICE ARREND.': data['ÍNDICE ARREND.'],
                'DTe a MAG': data['DTe a MAG'],
                'fecha_reporte': datetime.now().strftime('%d/%m/%Y %H:%M'),
                'metadata': {
                    'fecha_actualizacion': datetime.now().isoformat(),
                    'fuente': self.URL,
                    'descripcion': 'Datos del dashboard principal del Mercado Agroganadero'
                }
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
