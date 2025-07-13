#!/usr/bin/env python3
"""
Script para cargar datos a S3 y procesarlos a través del API
"""

import boto3
import json
import csv
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
import requests
import time

class S3DataProcessor:
    def __init__(self, bucket_name: str, api_url: str):
        self.s3_client = boto3.client('s3')
        self.bucket_name = bucket_name
        self.api_url = api_url.rstrip('/')
        self.session = requests.Session()
    
    def upload_csv_to_s3(self, csv_path: str, s3_key: str = None) -> str:
        """Subir archivo CSV a S3"""
        if not s3_key:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            s3_key = f"data/items_{timestamp}.csv"
        
        try:
            self.s3_client.upload_file(csv_path, self.bucket_name, s3_key)
            s3_url = f"s3://{self.bucket_name}/{s3_key}"
            print(f"✅ Archivo subido a S3: {s3_url}")
            return s3_key
        except Exception as e:
            print(f"❌ Error subiendo archivo a S3: {e}")
            return None
    
    def download_csv_from_s3(self, s3_key: str, local_path: str) -> bool:
        """Descargar archivo CSV desde S3"""
        try:
            self.s3_client.download_file(self.bucket_name, s3_key, local_path)
            print(f"✅ Archivo descargado: {local_path}")
            return True
        except Exception as e:
            print(f"❌ Error descargando archivo: {e}")
            return False
    
    def list_s3_files(self, prefix: str = "data/") -> List[str]:
        """Listar archivos en S3"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            files = [obj['Key'] for obj in response.get('Contents', [])]
            return files
        except Exception as e:
            print(f"❌ Error listando archivos: {e}")
            return []
    
    def process_csv_through_api(self, csv_path: str, batch_size: int = 10) -> List[Dict]:
        """Procesar CSV a través del API"""
        results = []
        
        try:
            # Cargar datos del CSV
            df = pd.read_csv(csv_path)
            print(f"📊 Cargados {len(df)} registros del CSV")
            
            # Procesar en lotes
            for i in range(0, len(df), batch_size):
                batch = df.iloc[i:i+batch_size]
                print(f"🔄 Procesando lote {i//batch_size + 1}/{(len(df)-1)//batch_size + 1}")
                
                for _, row in batch.iterrows():
                    # Preparar datos para el API
                    item_a = {
                        'item_id': int(row.get('ITEM_A', 0)),
                        'title': str(row.get('TITLE_A', '')).strip()
                    }
                    item_b = {
                        'item_id': int(row.get('ITEM_B', 0)),
                        'title': str(row.get('TITLE_B', '')).strip()
                    }
                    
                    # Llamar al API
                    try:
                        payload = {
                            "item_a": item_a,
                            "item_b": item_b
                        }
                        response = self.session.post(
                            f"{self.api_url}/items/compare",
                            json=payload,
                            timeout=30
                        )
                        response.raise_for_status()
                        result = response.json()
                        
                        # Agregar información adicional
                        result['item_a_id'] = item_a['item_id']
                        result['item_a_title'] = item_a['title']
                        result['item_b_id'] = item_b['item_id']
                        result['item_b_title'] = item_b['title']
                        result['processed_at'] = datetime.now().isoformat()
                        
                        results.append(result)
                        
                    except Exception as e:
                        print(f"❌ Error procesando par {item_a['item_id']}-{item_b['item_id']}: {e}")
                        # Agregar resultado de error
                        error_result = {
                            'item_a_id': item_a['item_id'],
                            'item_a_title': item_a['title'],
                            'item_b_id': item_b['item_id'],
                            'item_b_title': item_b['title'],
                            'similarity_score': 0.0,
                            'are_similar': False,
                            'are_equal': False,
                            'pair_exists': False,
                            'error': str(e),
                            'processed_at': datetime.now().isoformat()
                        }
                        results.append(error_result)
                
                # Pausa entre lotes
                time.sleep(1)
            
            print(f"✅ Procesamiento completado: {len(results)} resultados")
            return results
            
        except Exception as e:
            print(f"❌ Error procesando CSV: {e}")
            return []
    
    def save_results_to_s3(self, results: List[Dict], s3_key: str = None) -> str:
        """Guardar resultados en S3"""
        if not s3_key:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            s3_key = f"results/api_results_{timestamp}.json"
        
        try:
            # Guardar como JSON
            json_data = json.dumps(results, indent=2, ensure_ascii=False)
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=json_data.encode('utf-8'),
                ContentType='application/json'
            )
            
            # También guardar como CSV
            csv_key = s3_key.replace('.json', '.csv')
            df = pd.DataFrame(results)
            csv_data = df.to_csv(index=False, encoding='utf-8')
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=csv_key,
                Body=csv_data.encode('utf-8'),
                ContentType='text/csv'
            )
            
            print(f"✅ Resultados guardados en S3:")
            print(f"   JSON: s3://{self.bucket_name}/{s3_key}")
            print(f"   CSV: s3://{self.bucket_name}/{csv_key}")
            
            return s3_key
            
        except Exception as e:
            print(f"❌ Error guardando resultados: {e}")
            return None
    
    def analyze_results(self, results: List[Dict]) -> Dict[str, Any]:
        """Analizar resultados y generar estadísticas"""
        if not results:
            return {}
        
        # Filtrar resultados con errores
        valid_results = [r for r in results if 'error' not in r]
        error_results = [r for r in results if 'error' in r]
        
        analysis = {
            'total_processed': len(results),
            'successful': len(valid_results),
            'errors': len(error_results),
            'success_rate': len(valid_results) / len(results) * 100 if results else 0
        }
        
        if valid_results:
            # Estadísticas de similitud
            similar_pairs = sum(1 for r in valid_results if r.get('are_similar', False))
            equal_pairs = sum(1 for r in valid_results if r.get('are_equal', False))
            existing_pairs = sum(1 for r in valid_results if r.get('pair_exists', False))
            
            # Calcular estadísticas de similitud
            similarity_scores = [r.get('similarity_score', 0) for r in valid_results]
            
            analysis.update({
                'similar_pairs': similar_pairs,
                'equal_pairs': equal_pairs,
                'existing_pairs': existing_pairs,
                'similarity_rate': similar_pairs / len(valid_results) * 100,
                'equal_rate': equal_pairs / len(valid_results) * 100,
                'avg_similarity': sum(similarity_scores) / len(similarity_scores),
                'min_similarity': min(similarity_scores),
                'max_similarity': max(similarity_scores)
            })
        
        return analysis

def main():
    """Función principal"""
    print("🚀 Procesador de Datos S3 + API")
    print("="*50)
    
    # Configuración
    bucket_name = "meli-challenge-data"  # Cambiar por tu bucket
    api_url = "https://omdl9zog0a.execute-api.us-east-1.amazonaws.com/prod"
    
    # Crear procesador
    processor = S3DataProcessor(bucket_name, api_url)
    
    # 1. Verificar archivos en S3
    print("1️⃣ Verificando archivos en S3...")
    s3_files = processor.list_s3_files()
    if s3_files:
        print(f"   Archivos encontrados: {len(s3_files)}")
        for file in s3_files[:5]:  # Mostrar solo los primeros 5
            print(f"   • {file}")
    else:
        print("   No se encontraron archivos en S3")
    
    # 2. Subir CSV local a S3 (si existe)
    csv_path = "data_matches - dataset.csv"
    print(f"\n2️⃣ Subiendo archivo local a S3...")
    if csv_path:
        s3_key = processor.upload_csv_to_s3(csv_path)
        if s3_key:
            print(f"   Archivo subido como: {s3_key}")
        else:
            print("   ❌ Error subiendo archivo")
            return
    else:
        print("   No se encontró archivo CSV local")
        return
    
    # 3. Procesar datos a través del API
    print(f"\n3️⃣ Procesando datos a través del API...")
    results = processor.process_csv_through_api(csv_path, batch_size=5)
    
    if not results:
        print("❌ No se obtuvieron resultados")
        return
    
    # 4. Analizar resultados
    print(f"\n4️⃣ Analizando resultados...")
    analysis = processor.analyze_results(results)
    
    print(f"📊 Análisis de Resultados:")
    print(f"   • Total procesados: {analysis.get('total_processed', 0)}")
    print(f"   • Exitosos: {analysis.get('successful', 0)}")
    print(f"   • Errores: {analysis.get('errors', 0)}")
    print(f"   • Tasa de éxito: {analysis.get('success_rate', 0):.1f}%")
    
    if analysis.get('successful', 0) > 0:
        print(f"   • Pares similares: {analysis.get('similar_pairs', 0)} ({analysis.get('similarity_rate', 0):.1f}%)")
        print(f"   • Pares iguales: {analysis.get('equal_pairs', 0)} ({analysis.get('equal_rate', 0):.1f}%)")
        print(f"   • Similitud promedio: {analysis.get('avg_similarity', 0):.3f}")
        print(f"   • Rango de similitud: {analysis.get('min_similarity', 0):.3f} - {analysis.get('max_similarity', 0):.3f}")
    
    # 5. Guardar resultados en S3
    print(f"\n5️⃣ Guardando resultados en S3...")
    results_key = processor.save_results_to_s3(results)
    
    # 6. Mostrar algunos ejemplos
    print(f"\n6️⃣ Ejemplos de resultados:")
    for i, result in enumerate(results[:3], 1):
        if 'error' in result:
            print(f"   {i}. ❌ ERROR: {result.get('error', 'Unknown error')}")
        else:
            status = "✅ IGUAL" if result.get('are_equal') else "🔄 SIMILAR" if result.get('are_similar') else "❌ DIFERENTE"
            print(f"   {i}. {status}")
            print(f"      A: {result.get('item_a_title', 'N/A')}")
            print(f"      B: {result.get('item_b_title', 'N/A')}")
            print(f"      Similitud: {result.get('similarity_score', 0):.3f}")
        print()
    
    print("🎉 Procesamiento completado!")

if __name__ == "__main__":
    main() 