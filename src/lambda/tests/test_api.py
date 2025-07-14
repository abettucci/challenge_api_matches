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
    
    print("\n" + "="*80)
    print("📊 ANÁLISIS DE RESULTADOS")
    print("="*80)
    
    # Estadísticas generales
    total_pairs = len(results)
    similar_pairs = sum(1 for r in results if r.get('are_similar', False))
    equal_pairs = sum(1 for r in results if r.get('are_equal', False))
    existing_pairs = sum(1 for r in results if r.get('pair_exists', False))
    positive_pairs = sum(1 for r in results if r.get('new_status') == 'positivo' or r.get('existing_status') == 'positivo')
    negative_pairs = sum(1 for r in results if r.get('new_status') == 'negativo' or r.get('existing_status') == 'negativo')
    
    # Contar acciones
    created_updated = sum(1 for r in results if r.get('action') == 'created_or_updated')
    skipped = sum(1 for r in results if r.get('action') == 'skipped')
    
    print(f"📈 Estadísticas Generales:")
    print(f"   • Total de pares analizados: {total_pairs}")
    print(f"   • Pares similares: {similar_pairs} ({similar_pairs/total_pairs*100:.1f}%)")
    print(f"   • Pares iguales: {equal_pairs} ({equal_pairs/total_pairs*100:.1f}%)")
    print(f"   • Pares ya existentes: {existing_pairs} ({existing_pairs/total_pairs*100:.1f}%)")
    print(f"   • Pares con status positivo: {positive_pairs} ({positive_pairs/total_pairs*100:.1f}%)")
    print(f"   • Pares con status negativo: {negative_pairs} ({negative_pairs/total_pairs*100:.1f}%)")
    print(f"   • Pares creados/actualizados: {created_updated}")
    print(f"   • Pares omitidos (ya positivos): {skipped}")
    
    # Análisis detallado
    print(f"\n🔍 Análisis Detallado:")
    for i, result in enumerate(results, 1):
        item_a_title = result.get('item_a_title', 'N/A')
        item_b_title = result.get('item_b_title', 'N/A')
        similarity = result.get('similarity_score', 0)
        are_similar = result.get('are_similar', False)
        are_equal = result.get('are_equal', False)
        pair_exists = result.get('pair_exists', False)
        existing_status = result.get('existing_status', '')
        new_status = result.get('new_status', '')
        action = result.get('action', '')
        message = result.get('message', '')
        
        # Determinar el status final
        final_status = new_status if new_status else existing_status
        
        # Determinar el icono según el status
        if final_status == 'positivo':
            status_icon = "✅ POSITIVO"
        elif final_status == 'negativo':
            status_icon = "❌ NEGATIVO"
        else:
            status_icon = "❓ DESCONOCIDO"
        
        # Determinar el icono de acción
        if action == 'created_or_updated':
            action_icon = "🔄 REGENERADO/CREADO"
        elif action == 'skipped':
            action_icon = "⏭️ OMITIDO"
        else:
            action_icon = "❓ DESCONOCIDO"
        
        print(f"   {i}. {status_icon} - {action_icon}")
        print(f"      A: {item_a_title}")
        print(f"      B: {item_b_title}")
        print(f"      Similitud: {similarity:.3f}")
        
        if pair_exists and existing_status:
            print(f"      Status existente: {existing_status}")
        
        if new_status:
            print(f"      Nuevo status: {new_status}")
        
        if message:
            print(f"      Nota: {message}")
        
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
                'existing_status', 'new_status', 'action', 'message',
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
                    'existing_status': result.get('existing_status', ''),
                    'new_status': result.get('new_status', ''),
                    'action': result.get('action', ''),
                    'message': result.get('message', ''),
                    'pair_id': result.get('pair_id', ''),
                    'timestamp': datetime.now().isoformat()
                })
        
        print(f"✅ Resultados guardados en: {filename}")
    except Exception as e:
        print(f"❌ Error guardando resultados: {e}")

def main():
    """Función principal"""
    print("🚀 Iniciando pruebas del API de Ítems Similares")
    print("="*60)
    
    # Configuración
    API_BASE_URL = "https://xqubgjprk1.execute-api.us-east-1.amazonaws.com/prod"  # URL actual del API
    
    # Crear instancia del tester
    tester = APITester(API_BASE_URL)
    
    # Health check
    print("🔍 Verificando salud del API...")
    health_result = tester.health_check()
    if not health_result:
        print("❌ El API no está disponible. Verifica la URL y el estado del servicio.")
        return
    
    print(f"✅ API funcionando: {health_result.get('message', 'OK')}")
    
    # Cargar datos de prueba
    print("\n📊 Cargando datos de prueba...")
    
    # Intentar cargar desde CSV primero
    csv_path = "data_matches - dataset.csv"  # Archivo CSV del dataset
    test_data = load_test_data_from_csv(csv_path)
    
    # Si no hay datos CSV, usar datos de muestra
    if not test_data:
        print("📝 Usando datos de muestra...")
        test_data = create_sample_data()
    
    if not test_data:
        print("❌ No se pudieron cargar datos de prueba")
        return
    
    # Procesar cada par
    print(f"\n🔄 Procesando {len(test_data)} pares de ítems...")
    results = []
    
    for i, pair_data in enumerate(test_data, 1):
        item_a = pair_data['item_a']
        item_b = pair_data['item_b']
        
        print(f"   Procesando par {i}/{len(test_data)}: {item_a['item_id']} vs {item_b['item_id']}")
        
        # Crear el par
        result = tester.create_pair(item_a, item_b)
        
        if result:
            # Agregar información adicional para el análisis
            result['item_a_id'] = item_a['item_id']
            result['item_a_title'] = item_a['title']
            result['item_b_id'] = item_b['item_id']
            result['item_b_title'] = item_b['title']
            results.append(result)
            
            # Mostrar resultado inmediato
            action = result.get('action', 'unknown')
            if action == 'created_or_updated':
                print(f"      ✅ {result.get('message', 'Procesado')}")
            elif action == 'skipped':
                print(f"      ⏭️ {result.get('message', 'Omitido')}")
            else:
                print(f"      ❓ {result.get('message', 'Resultado desconocido')}")
        else:
            print(f"      ❌ Error procesando par")
        
        # Pequeña pausa para no sobrecargar el API
        time.sleep(0.1)
    
    # Analizar resultados
    analyze_results(results)
    
    # Guardar resultados
    save_results_to_csv(results)
    
    # Mostrar resumen final
    print("\n" + "="*60)
    print("🎉 PRUEBAS COMPLETADAS")
    print("="*60)
    print(f"✅ Total de pares procesados: {len(results)}")
    print(f"✅ Resultados guardados en CSV")
    print(f"✅ Análisis completado")
    
    # Mostrar algunos pares de la base de datos
    print(f"\n📋 Mostrando pares en la base de datos...")
    all_pairs = tester.get_all_pairs()
    if all_pairs and 'pairs' in all_pairs:
        pairs = all_pairs['pairs']
        print(f"   Total en BD: {len(pairs)} pares")
        
        # Mostrar los primeros 5 pares
        for i, pair in enumerate(pairs[:5], 1):
            pair_id = pair.get('id', 'N/A')
            title = pair.get('title', 'N/A')
            status = pair.get('status', 'N/A')
            similarity = pair.get('similarity_score', 0)
            
            print(f"   {i}. ID: {pair_id}")
            print(f"      Título: {title}")
            print(f"      Status: {status}")
            print(f"      Similitud: {similarity:.3f}")
            print()

if __name__ == "__main__":
    main() 