#!/usr/bin/env python3
"""
Scraper para Mercado Agroganadero
Extrae datos diarios de precios de hacienda
"""

import requests
import json
from datetime import datetime
import sys
import time
from typing import Dict, List, Optional

class MercadoAgroganaderoScraper:
    """Scraper para extraer datos del Mercado Agroganadero"""
    
    BASE_URL = "https://www.mercadoagroganadero.com.ar"
    
    # Mapeo de categorías
    CATEGORIAS = {
        'NOVILLOS': 1,
        'NOVILLITOS': 2,
        'VACAS': 3,
        'VAQUILLONAS': 5,
        'TOROS': 6
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'es-AR,es;q=0.9',
            'Referer': 'https://www.mercadoagroganadero.com.ar/'
        })
        
    def get_date_range(self, days_back: int = 15) -> tuple:
        """Obtiene el rango de fechas para la consulta"""
        from datetime import date, timedelta
        
        fecha_fin = date.today()
        fecha_ini = fecha_fin - timedelta(days=days_back)
        
        return (
            fecha_ini.strftime('%d/%m/%Y'),
            fecha_fin.strftime('%d/%m/%Y')
        )
    
    def fetch_categoria_data(self, categoria: str, clase: int, retries: int = 3) -> Optional[Dict]:
        """
        Obtiene datos de una categoría específica con reintentos
        
        Args:
            categoria: Nombre de la categoría
            clase: ID de la clase en el sistema
            retries: Número de reintentos en caso de fallo
            
        Returns:
            Diccionario con los datos o None si falla
        """
        fecha_ini, fecha_fin = self.get_date_range()
        
        url = (
            f"{self.BASE_URL}/php/hacigraf000110.chartjs.php"
            f"?txtFECHAINI={fecha_ini}"
            f"&txtFECHAFIN={fecha_fin}"
            f"&txtCLASE={clase}"
        )
        
        for attempt in range(retries):
            try:
                print(f"📡 Obteniendo datos de {categoria} (intento {attempt + 1}/{retries})...")
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                
                # Validar que los datos sean correctos
                if not data.get('labels') or not data.get('data'):
                    print(f"⚠️  Datos incompletos para {categoria}")
                    if attempt < retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                    return None
                
                print(f"✅ Datos de {categoria} obtenidos correctamente")
                return {
                    'categoria': categoria,
                    'labels': data['labels'],
                    'precios': data['data'][0]['vals'] if len(data['data']) > 0 else [],
                    'cabezas': data['data'][1]['vals'] if len(data['data']) > 1 else []
                }
                
            except requests.exceptions.RequestException as e:
                print(f"❌ Error en petición para {categoria}: {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    return None
            except json.JSONDecodeError as e:
                print(f"❌ Error al parsear JSON para {categoria}: {e}")
                return None
            except Exception as e:
                print(f"❌ Error inesperado para {categoria}: {e}")
                return None
        
        return None
    
    def scrape_all(self) -> Dict:
        """
        Obtiene datos de todas las categorías
        
        Returns:
            Diccionario con todos los datos estructurados
        """
        print(f"\n🚀 Iniciando scraping - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        datos = {
            'metadata': {
                'fecha_actualizacion': datetime.now().isoformat(),
                'fecha_actualizacion_legible': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                'fuente': self.BASE_URL,
                'descripcion': 'Datos diarios del Mercado Agroganadero de Argentina'
            },
            'categorias': {}
        }
        
        # Obtener datos de cada categoría
        for categoria, clase in self.CATEGORIAS.items():
            categoria_data = self.fetch_categoria_data(categoria, clase)
            
            if categoria_data:
                datos['categorias'][categoria] = categoria_data
                time.sleep(1)
            else:
                print(f"⚠️  No se pudieron obtener datos de {categoria}")
        
        # Estadísticas finales
        categorias_exitosas = len(datos['categorias'])
        total_categorias = len(self.CATEGORIAS)
        
        print("\n" + "=" * 70)
        print(f"📊 Resumen: {categorias_exitosas}/{total_categorias} categorías obtenidas")
        
        if categorias_exitosas == 0:
            print("❌ ERROR: No se obtuvieron datos de ninguna categoría")
            sys.exit(1)
        elif categorias_exitosas < total_categorias:
            print(f"⚠️  ADVERTENCIA: Faltan {total_categorias - categorias_exitosas} categorías")
        else:
            print("✅ Todos los datos obtenidos exitosamente")
        
        return datos
    
    def save_to_json(self, data: Dict, filename: str = 'mercado_agroganadero.json'):
        """
        Guarda los datos en un archivo JSON
        
        Args:
            data: Diccionario con los datos
            filename: Nombre del archivo de salida
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"\n💾 Datos guardados en '{filename}'")
            return True
        except Exception as e:
            print(f"\n❌ Error al guardar archivo: {e}")
            return False


def main():
    """Función principal"""
    try:
        scraper = MercadoAgroganaderoScraper()
        datos = scraper.scrape_all()
        
        if scraper.save_to_json(datos):
            print("\n🎉 Scraping completado exitosamente\n")
            sys.exit(0)
        else:
            print("\n❌ Error al guardar los datos\n")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
```

6. Click en **Commit changes**
7. Agrega el mensaje: "Update scraper.py - nueva versión"
8. Click en **Commit changes**

---

## Paso 2: Actualizar requirements.txt

1. Click en `requirements.txt`
2. Click en ✏️ Edit
3. Reemplaza el contenido con solo esto:
```
requests>=2.31.0
