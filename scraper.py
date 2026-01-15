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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-AR,es;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def clean_number(self, text):
        """Limpia y convierte texto a numero"""
        if not text:
            return None
        # Remover todo excepto dígitos, puntos, comas y signos
        cleaned = re.sub(r'[^\d.,\-]', '', text.strip())
        cleaned = cleaned.replace('.', '').replace(',', '.')
        try:
            if '.' in cleaned:
                return float(cleaned)
            return int(cleaned)
        except (ValueError, AttributeError):
            return None
    
    def scrape_dashboard(self):
        """Obtiene los datos del dashboard principal"""
        try:
            print(f"Conectando a {self.URL}...")
            
            response = self.session.get(self.URL, timeout=30)
            response.raise_for_status()
            
            print(f"Status code: {response.status_code}")
            print(f"Content length: {len(response.content)} bytes")
            
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
            
            # Estrategia 1: Buscar en enlaces con javascript:void(0)
            print("\nEstrategia 1: Enlaces javascript...")
            links = soup.find_all('a', href='javascript:void(0);')
            print(f"Enlaces encontrados: {len(links)}")
            
            for link in links:
                text = link.get_text(strip=True)
                if not text:
                    continue
                    
                text_upper = text.upper()
                
                # Buscar patrones: "NUMERO\nLABEL"
                lines = [l.strip() for l in text.split('\n') if l.strip()]
                
                if len(lines) >= 2:
                    numero_text = lines[0]
                    label = lines[1].upper()
                    numero = self.clean_number(numero_text)
                    
                    if numero is not None:
                        if 'CAMIONES' in label:
                            datos['CAMIONES'] = numero
                            print(f"  ✓ CAMIONES: {numero}")
                        elif 'CABEZAS' in label and 'SEMANA' not in label:
                            datos['CABEZAS'] = numero
                            print(f"  ✓ CABEZAS: {numero}")
                        elif 'SEMANA' in label:
                            datos['CAB.SEMANA'] = numero
                            print(f"  ✓ CAB.SEMANA: {numero}")
                        elif label == 'OP':
                            datos['OP'] = numero
                            print(f"  ✓ OP: {numero}")
                        elif 'INMAG' in label and 'IGMAG' not in label:
                            datos['INMAG'] = numero
                            print(f"  ✓ INMAG: {numero}")
                        elif 'IGMAG' in label:
                            datos['IGMAG'] = numero
                            print(f"  ✓ IGMAG: {numero}")
                        elif 'ARREND' in label:
                            datos['ÍNDICE ARREND.'] = numero
                            print(f"  ✓ ÍNDICE ARREND.: {numero}")
                        elif 'DTE' in label and 'MAG' in label:
                            datos['DTe a MAG'] = numero
                            print(f"  ✓ DTe a MAG: {numero}")
            
            # Estrategia 2: Buscar en todo el texto si faltan datos
            valores_obtenidos = sum(1 for v in datos.values() if v is not None)
            
            if valores_obtenidos < 4:
                print("\nEstrategia 2: Búsqueda en texto completo...")
                all_text = soup.get_text()
                
                # Patrones para buscar
                patterns = {
                    'CAMIONES': r'(\d+)\s*CAMIONES',
                    'CABEZAS': r'(\d+)\s*CABEZAS',
                    'CAB.SEMANA': r'([\d.]+)\s*CAB[.\s]*SEMANA',
                    'OP': r'(\d+)%?\s*OP',
                    'INMAG': r'INMAG\s*([\d,]+)',
                    'IGMAG': r'IGMAG\s*([\d,]+)',
                    'ÍNDICE ARREND.': r'[ÍI]NDICE\s+ARREND[.\s]*([\d,]+)',
                    'DTe a MAG': r'DTe\s+a\s+MAG\s*([\d.]+)'
                }
                
                for key, pattern in patterns.items():
                    if datos[key] is None:
                        match = re.search(pattern, all_text, re.IGNORECASE)
                        if match:
                            numero = self.clean_number(match.group(1))
                            if numero is not None:
                                datos[key] = numero
                                print(f"  ✓ {key}: {numero}")
            
            # Validar resultados
            valores_obtenidos = sum(1 for v in datos.values() if v is not None)
            print(f"\n{'='*70}")
            print(f"Datos obtenidos: {valores_obtenidos}/8")
            
            if valores_obtenidos == 0:
                print("\nERROR: No se obtuvieron datos")
                print("\nGuardando HTML para debug...")
                with open('debug_page.html', 'w', encoding='utf-8') as f:
                    f.write(str(soup.prettify()))
                print("HTML guardado en debug_page.html")
                return None
            
            # Mostrar resumen final
            print("\nResumen final:")
            for key, value in datos.items():
                status = "✓" if value is not None else "✗"
                print(f"  {status} {key}: {value}")
            
            return datos
            
        except Exception as e:
            print(f"\nError al obtener datos: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def save_to_json(self, data, filename='mercado_agroganadero.json'):
        """Guarda los datos en formato JSON compatible con el frontend"""
        try:
            # Asegurar que todos los valores sean números o 0
            safe_data = {}
            for key, value in data.items():
                if value is None:
                    safe_data[key] = 0
                else:
                    safe_data[key] = value
            
            # Formato adaptado para el frontend React
            output = {
                'CAMIONES': safe_data['CAMIONES'],
                'CABEZAS': safe_data['CABEZAS'],
                'CAB.SEMANA': safe_data['CAB.SEMANA'],
                'OP': safe_data['OP'],
                'INMAG': safe_data['INMAG'],
                'IGMAG': safe_data['IGMAG'],
                'ÍNDICE ARREND.': safe_data['ÍNDICE ARREND.'],
                'DTe a MAG': safe_data['DTe a MAG'],
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
            
            # Mostrar contenido del JSON
            print("\nContenido del JSON:")
            print(json.dumps(output, indent=2, ensure_ascii=False))
            
            return True
        except Exception as e:
            print(f"Error al guardar archivo: {e}")
            import traceback
            traceback.print_exc()
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
            print("\n" + "=" * 70)
            print("Scraping completado exitosamente")
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
