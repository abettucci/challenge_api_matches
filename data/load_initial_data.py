import pandas as pd
import boto3
import os 
from datetime import datetime
from app import calculate_similarity, generate_pair_id

def load_initial_data():
    """Cargar datos iniciales del CSV a DynamoDB"""
    
    # Configuración de DynamoDB
    if os.getenv('AWS_ENDPOINT_URL'):
        # Para desarrollo local con DynamoDB local
        dynamodb = boto3.resource('dynamodb', 
                                 endpoint_url=os.getenv('AWS_ENDPOINT_URL'),
                                 region_name='us-east-1',
                                 aws_access_key_id='dummy',
                                 aws_secret_access_key='dummy')
    else:
        # Para producción en AWS
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    
    # Cargar datos del CSV
    df = pd.read_csv('data_matches - dataset.csv')
    
    print(f"Cargando {len(df)} pares de ítems desde el CSV...")
    
    pairs_table = dynamodb.Table('item_pairs')
    items_table = dynamodb.Table('items')
    
    created_pairs = 0
    existing_pairs = 0
    errors = 0
    
    for index, row in df.iterrows():
        try:
            # Preparar datos del par
            item_a = {
                'item_id': int(row['ITEM_A']),
                'title': str(row['TITLE_A']).strip()
            }
            
            item_b = {
                'item_id': int(row['ITEM_B']),
                'title': str(row['TITLE_B']).strip()
            }
            
            # Generar ID del par
            pair_id = generate_pair_id(item_a['item_id'], item_b['item_id'])
            
            # Verificar si el par ya existe
            try:
                response = pairs_table.get_item(Key={'pair_id': pair_id})
                if 'Item' in response:
                    existing_pairs += 1
                    print(f"Par {pair_id} ya existe, saltando...")
                    continue
            except Exception as e:
                print(f"Error verificando par {pair_id}: {e}")
            
            # Crear el par
            pair_data = {
                'pair_id': pair_id,
                'item_a_id': item_a['item_id'],
                'item_a_title': item_a['title'],
                'item_b_id': item_b['item_id'],
                'item_b_title': item_b['title'],
                'similarity_score': calculate_similarity(item_a['title'], item_b['title']),
                'created_at': datetime.now().isoformat(),
                'source': 'initial_csv_load'
            }
            
            pairs_table.put_item(Item=pair_data)
            created_pairs += 1
            
            print(f"Par {pair_id} creado exitosamente")
            
        except Exception as e:
            errors += 1
            print(f"Error procesando fila {index}: {e}")
    
    print(f"\n=== RESUMEN DE CARGA ===")
    print(f"Pares creados: {created_pairs}")
    print(f"Pares existentes: {existing_pairs}")
    print(f"Errores: {errors}")
    print(f"Total procesados: {len(df)}")

if __name__ == '__main__':
    load_initial_data() 