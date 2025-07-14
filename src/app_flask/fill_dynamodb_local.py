import boto3
import os
from datetime import datetime
import pandas as pd
from decimal import Decimal
import time

def generate_pair_id(item_a, item_b):
    return f"{min(item_a, item_b)}_{max(item_a, item_b)}"

def convert_floats(obj):
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: convert_floats(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_floats(i) for i in obj]
    else:
        return obj

def main():
    start = time.time()
    # Configuración para DynamoDB local
    dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000', region_name='us-east-1', aws_access_key_id='dummy', aws_secret_access_key='dummy')
    table = dynamodb.Table('item_pairs')
    # Ruta robusta al CSV (ajustada a la estructura actual)
    csv_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'data_matches - dataset.csv')
    df = pd.read_csv(csv_path)
    for _, row in df.iterrows():
        a_id = int(row['ITEM_A'])
        a_title = str(row['TITLE_A']).strip()
        b_id = int(row['ITEM_B'])
        b_title = str(row['TITLE_B']).strip()
        pair_id = generate_pair_id(a_id, b_id)
        item = {
            'id': pair_id,
            'item_a_id': a_id,
            'item_a_title': a_title,
            'item_b_id': b_id,
            'item_b_title': b_title,
            'similarity_score': 0.0,
            'created_at': datetime.now().isoformat(),
            'status': 'manual_load'
        }
        item = convert_floats(item)
        table.put_item(Item=item)
        print(f"Par agregado: {pair_id}")
    print("Tiempo en cargar datos:", time.time() - start)

if __name__ == "__main__":
    main() 