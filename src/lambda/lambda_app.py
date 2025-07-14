import json
import boto3
import os
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
PAIRS_TABLE = 'item_pairs'

def calculate_similarity(title1: str, title2: str) -> float:
    """Calcular similitud entre dos títulos usando ML model o fallback a TF-IDF"""
    try:
        # Intentar usar el modelo ML si está disponible
        from ml_similarity import get_ml_similarity
        result = get_ml_similarity(title1, title2)
        return result['similarity_score']
    except Exception as e:
        logger.warning(f"ML model not available, using fallback: {e}")
        # Fallback a similitud básica usando TF-IDF
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        
        # Normalizar títulos
        title1_norm = title1.lower().strip()
        title2_norm = title2.lower().strip()
        
        # Si son exactamente iguales
        if title1_norm == title2_norm:
            return 1.0
        
        # Calcular similitud usando TF-IDF y cosine similarity
        vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1, 2), stop_words=None)
        tfidf_matrix = vectorizer.fit_transform([title1_norm, title2_norm])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        return float(similarity)

def generate_pair_id(item_a: int, item_b: int) -> str:
    """Generar ID único para un par de ítems"""
    return f"{min(item_a, item_b)}_{max(item_a, item_b)}"

def create_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """Crear respuesta estándar para API Gateway"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
        },
        'body': json.dumps(body, default=str)
    }

def lambda_handler(event, context):
    """Handler principal para AWS Lambda"""
    
    # Manejar preflight CORS
    if event.get('httpMethod') == 'OPTIONS':
        return create_response(200, {'message': 'OK'})
    
    # Obtener información de la petición
    http_method = event.get('httpMethod', 'GET')
    path = event.get('path', '/')
    
    try:
        # Routing basado en método y path
        if http_method == 'GET' and path == '/health':
            return health_check()
        elif http_method == 'POST' and path == '/items/compare':
            return compare_items(event)
        elif http_method == 'POST' and path == '/items/pairs':
            return create_item_pair(event)
        elif http_method == 'GET' and path == '/items/pairs':
            return get_all_pairs()
        elif http_method == 'GET' and path.startswith('/items/pairs/'):
            pair_id = path.split('/')[-1]
            return get_pair(pair_id)
        elif http_method == 'PUT' and path.startswith('/items/pairs/'):
            return update_pair(event)
        elif http_method == 'DELETE' and path.startswith('/items/pairs/'):
            return delete_pair(event)
        else:
            return create_response(404, {
                'status': 'error',
                'message': 'Endpoint no encontrado'
            })
            
    except Exception as e:
        logger.error(f"Error en lambda_handler: {e}")
        return create_response(500, {
            'status': 'error',
            'message': f'Error interno del servidor: {str(e)}'
        })

def health_check():
    """Endpoint de salud de la API"""
    try:
        # Verificar que DynamoDB está accesible
        pairs_table = dynamodb.Table(PAIRS_TABLE)
        pairs_table.table_status
        
        # Verificar que las dependencias de ML están disponibles
        try:
            import sklearn
            import xgboost
            import pandas
            ml_status = "available"
        except ImportError as e:
            ml_status = f"missing: {str(e)}"
        
        return create_response(200, {
            'status': 'success',
            'message': 'API de Ítems Similares funcionando correctamente en AWS Lambda',
            'timestamp': datetime.now().isoformat(),
            'environment': 'aws-lambda',
            'dynamodb_status': 'connected',
            'ml_dependencies': ml_status
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return create_response(500, {
            'status': 'error',
            'message': f'Health check failed: {str(e)}',
            'timestamp': datetime.now().isoformat(),
            'environment': 'aws-lambda'
        })

def compare_items(event):
    """Comparar dos ítems y determinar si son iguales, similares o si ya existe el par"""
    try:
        body = json.loads(event.get('body', '{}'))
        
        if not body or 'item_a' not in body or 'item_b' not in body:
            return create_response(400, {
                'status': 'error',
                'message': 'Se requieren item_a e item_b en el cuerpo de la petición'
            })
        
        item_a = body['item_a']
        item_b = body['item_b']
        
        # Validar estructura de datos
        if not all(key in item_a for key in ['item_id', 'title']):
            return create_response(400, {
                'status': 'error',
                'message': 'item_a debe contener item_id y title'
            })
        
        if not all(key in item_b for key in ['item_id', 'title']):
            return create_response(400, {
                'status': 'error',
                'message': 'item_b debe contener item_id y title'
            })
        
        # Calcular similitud
        similarity_score = calculate_similarity(item_a['title'], item_b['title'])
        are_equal = similarity_score == 1.0
        are_similar = similarity_score >= 0.7  # Umbral de similitud
        
        # Verificar si el par ya existe
        pair_id = generate_pair_id(item_a['item_id'], item_b['item_id'])
        pairs_table = dynamodb.Table(PAIRS_TABLE)
        
        try:
            response = pairs_table.get_item(Key={'id': pair_id})
            pair_exists = 'Item' in response
        except Exception as e:
            logger.error(f"Error verificando par existente: {e}")
            pair_exists = False
        
        return create_response(200, {
            'status': 'success',
            'message': 'Comparación completada exitosamente',
            'similarity_score': similarity_score,
            'are_similar': are_similar,
            'pair_exists': pair_exists,
            'pair_id': pair_id
        })
        
    except Exception as e:
        logger.error(f"Error en compare_items: {e}")
        return create_response(500, {
            'status': 'error',
            'message': f'Error interno del servidor: {str(e)}'
        })

def create_item_pair(event):
    """Crear o actualizar un par de ítems según la lógica de la consigna"""
    try:
        body = json.loads(event.get('body', '{}'))
        
        if not body or 'item_a' not in body or 'item_b' not in body:
            return create_response(400, {
                'status': 'error',
                'message': 'Se requieren item_a e item_b en el cuerpo de la petición'
            })
        
        item_a = body['item_a']
        item_b = body['item_b']
        
        # Validar estructura de datos
        if not all(key in item_a for key in ['item_id', 'title']):
            return create_response(400, {
                'status': 'error',
                'message': 'item_a debe contener item_id y title'
            })
        
        if not all(key in item_b for key in ['item_id', 'title']):
            return create_response(400, {
                'status': 'error',
                'message': 'item_b debe contener item_id y title'
            })
        
        # Verificar si el par ya existe
        pair_id = generate_pair_id(item_a['item_id'], item_b['item_id'])
        pairs_table = dynamodb.Table(PAIRS_TABLE)
        
        try:
            response = pairs_table.get_item(Key={'id': pair_id})
            pair_exists = 'Item' in response
            existing_item = response.get('Item', {}) if pair_exists else {}
            existing_status = existing_item.get('status', '') if pair_exists else ''
        except Exception as e:
            logger.error(f"Error verificando par existente: {e}")
            pair_exists = False
            existing_status = ''
            existing_item = {}
        
        # Calcular similitud
        similarity_score = calculate_similarity(item_a['title'], item_b['title'])
        are_equal = similarity_score == 1.0
        are_similar = similarity_score >= 0.7
        
        # Determinar el status según la consigna
        if are_similar or are_equal:
            new_status = "positivo"
        else:
            new_status = "negativo"
        
        # Lógica de regeneración
        action_message = ""
        should_update = False
        now = datetime.now().isoformat()
        
        if pair_exists:
            if existing_status == "positivo":
                action_message = "No se regenera porque ya existe ese par en la base de datos con status positivo"
                should_update = False
            elif existing_status == "negativo":
                if new_status == "positivo":
                    action_message = "Se regenera porque el par existente era negativo y ahora es positivo"
                    should_update = True
                else:
                    action_message = "No se regenera porque sigue siendo negativo (solo se actualiza updated_at)"
                    should_update = True  # Para actualizar updated_at aunque siga negativo
            else:
                # Para otros status, siempre actualiza
                action_message = "Se regenera porque el par existente tiene status diferente"
                should_update = True
        else:
            action_message = "Se crea nuevo par en la base de datos"
            should_update = True
        
        if should_update:
            pair_data = {
                'id': pair_id,
                'item_a_id': item_a['item_id'],
                'item_a_title': item_a['title'],
                'item_b_id': item_b['item_id'],
                'item_b_title': item_b['title'],
                'similarity_score': Decimal(str(similarity_score)),
                'are_equal': are_equal,
                'are_similar': are_similar,
                'status': new_status,
                'created_at': existing_item.get('created_at', now),
                'updated_at': now
            }
            pairs_table.put_item(Item=pair_data)
            return create_response(201, {
                'status': 'success',
                'message': f'Par de ítems procesado: {action_message}',
                'pair_id': pair_id,
                'similarity_score': similarity_score,
                'are_equal': are_equal,
                'are_similar': are_similar,
                'new_status': new_status,
                'action': 'created_or_updated'
            })
        else:
            return create_response(200, {
                'status': 'success',
                'message': action_message,
                'pair_id': pair_id,
                'existing_status': existing_status,
                'similarity_score': float(existing_item.get('similarity_score', 0)),
                'are_equal': existing_item.get('are_equal', False),
                'are_similar': existing_item.get('are_similar', False),
                'action': 'skipped'
            })
    except Exception as e:
        logger.error(f"Error en create_item_pair: {e}")
        return create_response(500, {
            'status': 'error',
            'message': f'Error interno del servidor: {str(e)}'
        })

def get_all_pairs():
    """Obtener todos los pares de ítems"""
    try:
        pairs_table = dynamodb.Table(PAIRS_TABLE)
        response = pairs_table.scan()
        pairs = response.get('Items', [])
        
        return create_response(200, {
            'status': 'success',
            'message': f'Se encontraron {len(pairs)} pares de ítems',
            'pairs': pairs
        })
        
    except Exception as e:
        logger.error(f"Error en get_all_pairs: {e}")
        return create_response(500, {
            'status': 'error',
            'message': f'Error interno del servidor: {str(e)}'
        })

def get_pair(pair_id):
    """Obtener un par específico por ID"""
    try:
        pairs_table = dynamodb.Table(PAIRS_TABLE)
        response = pairs_table.get_item(Key={'id': pair_id})
        
        if 'Item' not in response:
            return create_response(404, {
                'status': 'error',
                'message': 'Par de ítems no encontrado'
            })
        
        return create_response(200, {
            'status': 'success',
            'message': 'Par de ítems encontrado exitosamente',
            'pair': response['Item']
        })
        
    except Exception as e:
        logger.error(f"Error en get_pair: {e}")
        return create_response(500, {
            'status': 'error',
            'message': f'Error interno del servidor: {str(e)}'
        }) 

def update_pair(event, context=None):
    """Actualizar campos de un par existente por id"""
    pair_id = event.get('pathParameters', {}).get('pair_id')
    body = json.loads(event.get('body', '{}'))
    if not pair_id or not body:
        return create_response(400, {'status': 'error', 'message': 'Faltan datos para actualizar'})
    try:
        pairs_table = dynamodb.Table(PAIRS_TABLE)
        update_expr = []
        expr_attr_vals = {}
        for k, v in body.items():
            update_expr.append(f"{k} = :{k}")
            expr_attr_vals[f":{k}"] = v
        update_expression = "set " + ", ".join(update_expr)
        pairs_table.update_item(
            Key={'id': pair_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expr_attr_vals
        )
        return create_response(200, {'status': 'success', 'message': f'Par con id {pair_id} actualizado exitosamente'})
    except Exception as e:
        logger.error(f"Error actualizando par: {e}")
        return create_response(500, {'status': 'error', 'message': f'Error actualizando par: {str(e)}'})

def delete_pair(event, context=None):
    """Eliminar un par por id"""
    pair_id = event.get('pathParameters', {}).get('pair_id')
    if not pair_id:
        return create_response(400, {'status': 'error', 'message': 'Falta el id del par'})
    try:
        pairs_table = dynamodb.Table(PAIRS_TABLE)
        pairs_table.delete_item(Key={'id': pair_id})
        return create_response(200, {'status': 'success', 'message': f'Par con id {pair_id} eliminado exitosamente'})
    except Exception as e:
        logger.error(f"Error eliminando par: {e}")
        return create_response(500, {'status': 'error', 'message': f'Error eliminando par: {str(e)}'}) 