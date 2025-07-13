#!/usr/bin/env python3
"""
Script de pruebas para el API de Ítems Similares
Permite cargar datos, hacer comparaciones y analizar resultados
"""

import requests
import json
import csv
import time
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime

class APITester:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
    def health_check(self) -> Dict[str, Any]:
        """Verificar que el API está funcionando"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Error en health check: {e}")
            return None
    
    def compare_items(self, item_a: Dict, item_b: Dict) -> Dict[str, Any]:
        """Comparar dos ítems"""
        try:
            payload = {
                "item_a": item_a,
                "item_b": item_b
            }
            response = self.session.post(f"{self.base_url}/items/compare", json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Error comparando ítems: {e}")
            return None
    
    def create_pair(self, item_a: Dict, item_b: Dict) -> Dict[str, Any]:
        """Crear un par de ítems"""
        try:
            payload = {
                "item_a": item_a,
                "item_b": item_b
            }
            response = self.session.post(f"{self.base_url}/items/pairs", json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Error creando par: {e}")
            return None
    
    def get_all_pairs(self) -> Dict[str, Any]:
        """Obtener todos los pares"""
        try:
            response = self.session.get(f"{self.base_url}/items/pairs")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Error obteniendo pares: {e}")
            return None
    
    def get_pair(self, pair_id: str) -> Dict[str, Any]:
        """Obtener un par específico"""
        try:
            response = self.session.get(f"{self.base_url}/items/pairs/{pair_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Error obteniendo par {pair_id}: {e}")
            return None

def load_test_data_from_csv(csv_path: str) -> List[Dict]:
    """Cargar datos de prueba desde CSV"""
    test_data = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Asumimos que el CSV tiene columnas: ITEM_A, TITLE_A, ITEM_B, TITLE_B
                test_data.append({
                    'item_a': {
                        'item_id': int(row.get('ITEM_A', 0)),
                        'title': row.get('TITLE_A', '').strip()
                    },
                    'item_b': {
                        'item_id': int(row.get('ITEM_B', 0)),
                        'title': row.get('TITLE_B', '').strip()
                    }
                })
        print(f"✅ Cargados {len(test_data)} pares de datos de prueba")
        return test_data
    except Exception as e:
        print(f"❌ Error cargando datos: {e}")
        return []

def create_sample_data() -> List[Dict]:
    """Crear datos de muestra para pruebas"""
    sample_data = [
        {
            'item_a': {'item_id': 1, 'title': 'Telefono Samsung Galaxy'},
            'item_b': {'item_id': 2, 'title': 'Telefono celular Samsung Galaxy'}
        },
        {
            'item_a': {'item_id': 3, 'title': 'Laptop HP 15 pulgadas'},
            'item_b': {'item_id': 4, 'title': 'Notebook HP 15 inch'}
        },
        {
            'item_a': {'item_id': 5, 'title': 'Auriculares bluetooth Sony'},
            'item_b': {'item_id': 6, 'title': 'Audifonos bluetooth Sony'}
        },
        {
            'item_a': {'item_id': 7, 'title': 'Telefono Samsung Galaxy'},
            'item_b': {'item_id': 8, 'title': 'Laptop HP 15 pulgadas'}
        },
        {
            'item_a': {'item_id': 9, 'title': 'Camara digital Canon'},
            'item_b': {'item_id': 10, 'title': 'Camara fotografica Canon'}
        }
    ]
    print(f"✅ Creados {len(sample_data)} pares de datos de muestra")
    return sample_data

def analyze_results(results: List[Dict]) -> None:
    """Analizar y mostrar resultados de las comparaciones"""
    if not results:
        print("❌ No hay resultados para analizar")
        return
    
    print("\n" + "="*60)
    print("📊 ANÁLISIS DE RESULTADOS")
    print("="*60)
    
    # Estadísticas generales
    total_pairs = len(results)
    similar_pairs = sum(1 for r in results if r.get('are_similar', False))
    equal_pairs = sum(1 for r in results if r.get('are_equal', False))
    existing_pairs = sum(1 for r in results if r.get('pair_exists', False))
    
    print(f"📈 Estadísticas Generales:")
    print(f"   • Total de pares analizados: {total_pairs}")
    print(f"   • Pares similares: {similar_pairs} ({similar_pairs/total_pairs*100:.1f}%)")
    print(f"   • Pares iguales: {equal_pairs} ({equal_pairs/total_pairs*100:.1f}%)")
    print(f"   • Pares ya existentes: {existing_pairs} ({existing_pairs/total_pairs*100:.1f}%)")
    
    # Análisis detallado
    print(f"\n🔍 Análisis Detallado:")
    for i, result in enumerate(results, 1):
        item_a_title = result.get('item_a_title', 'N/A')
        item_b_title = result.get('item_b_title', 'N/A')
        similarity = result.get('similarity_score', 0)
        are_similar = result.get('are_similar', False)
        are_equal = result.get('are_equal', False)
        
        status = "✅ IGUAL" if are_equal else "🔄 SIMILAR" if are_similar else "❌ DIFERENTE"
        
        print(f"   {i}. {status}")
        print(f"      A: {item_a_title}")
        print(f"      B: {item_b_title}")
        print(f"      Similitud: {similarity:.3f}")
        print()

def save_results_to_csv(results: List[Dict], filename: str = None) -> None:
    """Guardar resultados en CSV"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"api_test_results_{timestamp}.csv"
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            fieldnames = [
                'item_a_id', 'item_a_title', 'item_b_id', 'item_b_title',
                'similarity_score', 'are_similar', 'are_equal', 'pair_exists',
                'pair_id', 'timestamp'
            ]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in results:
                writer.writerow({
                    'item_a_id': result.get('item_a_id', ''),
                    'item_a_title': result.get('item_a_title', ''),
                    'item_b_id': result.get('item_b_id', ''),
                    'item_b_title': result.get('item_b_title', ''),
                    'similarity_score': result.get('similarity_score', 0),
                    'are_similar': result.get('are_similar', False),
                    'are_equal': result.get('are_equal', False),
                    'pair_exists': result.get('pair_exists', False),
                    'pair_id': result.get('pair_id', ''),
                    'timestamp': datetime.now().isoformat()
                })
        
        print(f"✅ Resultados guardados en: {filename}")
    except Exception as e:
        print(f"❌ Error guardando resultados: {e}")

def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas del API de Ítems Similares")
    print("="*60)
    
    # Configurar URL del API (cambiar según tu deployment)
    api_url = "https://omdl9zog0a.execute-api.us-east-1.amazonaws.com/prod"
    
    # Crear tester
    tester = APITester(api_url)
    
    # 1. Health Check
    print("1️⃣ Verificando salud del API...")
    health = tester.health_check()
    if health:
        print(f"✅ API funcionando: {health.get('message', 'OK')}")
        print(f"   DynamoDB: {health.get('dynamodb_status', 'Unknown')}")
        print(f"   Método de similitud: {health.get('similarity_method', 'Unknown')}")
    else:
        print("❌ API no está funcionando")
        return
    
    # 2. Cargar datos de prueba
    print("\n2️⃣ Cargando datos de prueba...")
    
    # Intentar cargar desde CSV, si no existe usar datos de muestra
    test_data = load_test_data_from_csv('data_matches - dataset.csv')
    if not test_data:
        print("📝 Usando datos de muestra...")
        test_data = create_sample_data()
    
    if not test_data:
        print("❌ No se pudieron cargar datos de prueba")
        return
    
    # 3. Ejecutar comparaciones
    print(f"\n3️⃣ Ejecutando {len(test_data)} comparaciones...")
    results = []
    
    for i, data in enumerate(test_data, 1):
        print(f"   Procesando par {i}/{len(test_data)}...")
        
        # Comparar ítems
        comparison = tester.compare_items(data['item_a'], data['item_b'])
        if comparison:
            # Agregar información de los ítems al resultado
            comparison['item_a_id'] = data['item_a']['item_id']
            comparison['item_a_title'] = data['item_a']['title']
            comparison['item_b_id'] = data['item_b']['item_id']
            comparison['item_b_title'] = data['item_b']['title']
            results.append(comparison)
        
        # Pequeña pausa para no sobrecargar el API
        time.sleep(0.1)
    
    # 4. Analizar resultados
    print(f"\n4️⃣ Analizando resultados...")
    analyze_results(results)
    
    # 5. Guardar resultados
    print(f"\n5️⃣ Guardando resultados...")
    save_results_to_csv(results)
    
    # 6. Mostrar todos los pares en la base de datos
    print(f"\n6️⃣ Consultando todos los pares en la base de datos...")
    all_pairs = tester.get_all_pairs()
    if all_pairs:
        pairs = all_pairs.get('pairs', [])
        print(f"   Total de pares en DB: {len(pairs)}")
        if pairs:
            print("   Últimos 5 pares:")
            for pair in pairs[-5:]:
                print(f"   • {pair.get('pair_id', 'N/A')}: {pair.get('item_a_title', 'N/A')} vs {pair.get('item_b_title', 'N/A')}")
    
    print(f"\n🎉 Pruebas completadas exitosamente!")

if __name__ == "__main__":
    main() 