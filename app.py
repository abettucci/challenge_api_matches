from flask import Flask, request, jsonify
from flask_cors import CORS
from flasgger import Swagger, swag_from
import boto3
import os
from datetime import datetime
import json
from typing import Dict, List, Optional
import logging
from decimal import Decimal

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuración de Swagger
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "API de Ítems Similares - Meli Challenge",
        "description": "API para gestionar pares de ítems similares con validaciones y detección de duplicados",
        "version": "1.0.0",
        "contact": {
            "name": "Data Engineer Challenge"
        }
    },
    "schemes": ["http", "https"]
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

# Nombres de las tablas
ITEMS_TABLE = 'items'
PAIRS_TABLE = 'item_pairs'

def get_dynamodb():
    """Obtener cliente de DynamoDB configurado según el entorno"""
    if os.getenv('AWS_ENDPOINT_URL'):
        # Para desarrollo local con DynamoDB local
        return boto3.resource('dynamodb', 
                             endpoint_url=os.getenv('AWS_ENDPOINT_URL'),
                             region_name='us-east-1',
                             aws_access_key_id='dummy',
                             aws_secret_access_key='dummy')
    else:
        # Para producción en AWS
        return boto3.resource('dynamodb', region_name='us-east-1')

# Cliente de DynamoDB por defecto
dynamodb = get_dynamodb()

def create_tables():
    """Crear tablas en DynamoDB si no existen"""
    try:
        # Tabla de ítems individuales
        items_table = dynamodb.create_table(
            TableName=ITEMS_TABLE,
            KeySchema=[
                {'AttributeName': 'item_id', 'KeyType': 'HASH'},
                {'AttributeName': 'title', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'item_id', 'AttributeType': 'N'},
                {'AttributeName': 'title', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        logger.info("Tabla de ítems creada")
    except Exception as e:
        logger.info(f"Tabla de ítems ya existe o error: {e}")

    try:
        # Tabla de pares de ítems
        pairs_table = dynamodb.create_table(
            TableName=PAIRS_TABLE,
            KeySchema=[
                {'AttributeName': 'pair_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'pair_id', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        logger.info("Tabla de pares creada")
    except Exception as e:
        logger.info(f"Tabla de pares ya existe o error: {e}")

def calculate_similarity(title1: str, title2: str) -> float:
    """Calcular similitud entre dos títulos usando ML o fallback básico"""
    try:
        # Intentar usar el modelo de ML
        from ml_similarity import get_ml_similarity
        ml_result = get_ml_similarity(title1, title2)
        return ml_result['similarity_score']
    except Exception as e:
        logger.warning(f"Error usando modelo ML, usando fallback básico: {e}")
        # Fallback a similitud básica
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        
        # Normalizar títulos
        title1_norm = title1.lower().strip()
        title2_norm = title2.lower().strip()
        
        # Si son exactamente iguales
        if title1_norm == title2_norm:
            return 1.0
        
        # Calcular similitud usando TF-IDF y cosine similarity
        vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1, 2))
        tfidf_matrix = vectorizer.fit_transform([title1_norm, title2_norm])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        return float(similarity)

def generate_pair_id(item_a: int, item_b: int) -> str:
    """Generar ID único para un par de ítems"""
    return f"{min(item_a, item_b)}_{max(item_a, item_b)}"

@app.route('/health', methods=['GET'])
@swag_from({
    'responses': {
        200: {
            'description': 'API funcionando correctamente',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string'},
                    'message': {'type': 'string'},
                    'timestamp': {'type': 'string'}
                }
            }
        }
    }
})
def health_check():
    """Endpoint de salud de la API"""
    return jsonify({
        'status': 'success',
        'message': 'API de Ítems Similares funcionando correctamente',
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/items/compare', methods=['POST'])
@swag_from({
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'item_a': {
                        'type': 'object',
                        'properties': {
                            'item_id': {'type': 'integer'},
                            'title': {'type': 'string'}
                        }
                    },
                    'item_b': {
                        'type': 'object',
                        'properties': {
                            'item_id': {'type': 'integer'},
                            'title': {'type': 'string'}
                        }
                    }
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Comparación exitosa',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string'},
                    'message': {'type': 'string'},
                    'similarity_score': {'type': 'number'},
                    'are_equal': {'type': 'boolean'},
                    'are_similar': {'type': 'boolean'},
                    'pair_exists': {'type': 'boolean'}
                }
            }
        },
        400: {
            'description': 'Datos de entrada inválidos'
        }
    }
})
def compare_items():
    """Comparar dos ítems y determinar si son iguales, similares o si ya existe el par"""
    try:
        data = request.get_json()
        
        if not data or 'item_a' not in data or 'item_b' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Se requieren item_a e item_b en el cuerpo de la petición'
            }), 400
        
        item_a = data['item_a']
        item_b = data['item_b']
        
        # Validar estructura de datos
        if not all(key in item_a for key in ['item_id', 'title']):
            return jsonify({
                'status': 'error',
                'message': 'item_a debe contener item_id y title'
            }), 400
        
        if not all(key in item_b for key in ['item_id', 'title']):
            return jsonify({
                'status': 'error',
                'message': 'item_b debe contener item_id y title'
            }), 400
        
        # Calcular similitud
        similarity_score = calculate_similarity(item_a['title'], item_b['title'])
        are_equal = similarity_score == 1.0
        are_similar = similarity_score >= 0.7  # Umbral de similitud
        
        # Verificar si el par ya existe
        pair_id = generate_pair_id(item_a['item_id'], item_b['item_id'])
        pairs_table = dynamodb.Table(PAIRS_TABLE)
        
        try:
            response = pairs_table.get_item(Key={'pair_id': pair_id})
            pair_exists = 'Item' in response
        except Exception as e:
            logger.error(f"Error verificando par existente: {e}")
            pair_exists = False
        
        return jsonify({
            'status': 'success',
            'message': 'Comparación completada exitosamente',
            'similarity_score': similarity_score,
            'are_equal': are_equal,
            'are_similar': are_similar,
            'pair_exists': pair_exists,
            'pair_id': pair_id
        }), 200
        
    except Exception as e:
        logger.error(f"Error en compare_items: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error interno del servidor: {str(e)}'
        }), 500

@app.route('/items/pairs', methods=['POST'])
@swag_from({
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'item_a': {
                        'type': 'object',
                        'properties': {
                            'item_id': {'type': 'integer'},
                            'title': {'type': 'string'}
                        }
                    },
                    'item_b': {
                        'type': 'object',
                        'properties': {
                            'item_id': {'type': 'integer'},
                            'title': {'type': 'string'}
                        }
                    }
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Par creado exitosamente'
        },
        200: {
            'description': 'Par ya existía'
        },
        400: {
            'description': 'Datos de entrada inválidos'
        }
    }
})
def create_item_pair():
    """Crear un nuevo par de ítems si no existe"""
    try:
        data = request.get_json()
        
        if not data or 'item_a' not in data or 'item_b' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Se requieren item_a e item_b en el cuerpo de la petición'
            }), 400
        
        item_a = data['item_a']
        item_b = data['item_b']
        
        # Validar estructura de datos
        if not all(key in item_a for key in ['item_id', 'title']):
            return jsonify({
                'status': 'error',
                'message': 'item_a debe contener item_id y title'
            }), 400
        
        if not all(key in item_b for key in ['item_id', 'title']):
            return jsonify({
                'status': 'error',
                'message': 'item_b debe contener item_id y title'
            }), 400
        
        # Verificar si el par ya existe
        pair_id = generate_pair_id(item_a['item_id'], item_b['item_id'])
        pairs_table = dynamodb.Table(PAIRS_TABLE)
        
        try:
            response = pairs_table.get_item(Key={'pair_id': pair_id})
            if 'Item' in response:
                return jsonify({
                    'status': 'success',
                    'message': 'El par de ítems ya existe en la base de datos',
                    'pair_id': pair_id,
                    'action': 'existing'
                }), 200
        except Exception as e:
            logger.error(f"Error verificando par existente: {e}")
        
        # Crear el nuevo par
        pair_data = {
            'pair_id': pair_id,
            'item_a_id': item_a['item_id'],
            'item_a_title': item_a['title'],
            'item_b_id': item_b['item_id'],
            'item_b_title': item_b['title'],
            'similarity_score': Decimal(str(calculate_similarity(item_a['title'], item_b['title']))),
            'created_at': datetime.now().isoformat()
        }
        
        pairs_table.put_item(Item=pair_data)
        
        return jsonify({
            'status': 'success',
            'message': 'Par de ítems creado exitosamente',
            'pair_id': pair_id,
            'action': 'created'
        }), 201
        
    except Exception as e:
        logger.error(f"Error en create_item_pair: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error interno del servidor: {str(e)}'
        }), 500

@app.route('/items/pairs', methods=['GET'])
@swag_from({
    'responses': {
        200: {
            'description': 'Lista de pares obtenida exitosamente'
        }
    }
})
def get_all_pairs():
    """Obtener todos los pares de ítems"""
    try:
        pairs_table = dynamodb.Table(PAIRS_TABLE)
        response = pairs_table.scan()
        pairs = response.get('Items', [])
        
        return jsonify({
            'status': 'success',
            'message': f'Se encontraron {len(pairs)} pares de ítems',
            'pairs': pairs
        }), 200
        
    except Exception as e:
        logger.error(f"Error en get_all_pairs: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error interno del servidor: {str(e)}'
        }), 500

@app.route('/items/pairs/<pair_id>', methods=['GET'])
@swag_from({
    'parameters': [
        {
            'name': 'pair_id',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'ID del par de ítems'
        }
    ],
    'responses': {
        200: {
            'description': 'Par encontrado exitosamente'
        },
        404: {
            'description': 'Par no encontrado'
        }
    }
})
def get_pair(pair_id):

@app.route('/ml/train', methods=['POST'])
@swag_from({
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'training_data': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'item_a_title': {'type': 'string'},
                                'item_b_title': {'type': 'string'},
                                'is_similar': {'type': 'integer'}
                            }
                        }
                    }
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Modelo entrenado exitosamente'
        },
        400: {
            'description': 'Datos de entrenamiento inválidos'
        }
    }
})
def train_model():
    """Entrenar el modelo de Machine Learning"""
    try:
        data = request.get_json()
        
        if not data or 'training_data' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Se requieren datos de entrenamiento'
            }), 400
        
        training_data = data['training_data']
        
        if not isinstance(training_data, list) or len(training_data) == 0:
            return jsonify({
                'status': 'error',
                'message': 'Los datos de entrenamiento deben ser una lista no vacía'
            }), 400
        
        # Validar estructura de datos
        for item in training_data:
            if not all(key in item for key in ['item_a_title', 'item_b_title', 'is_similar']):
                return jsonify({
                    'status': 'error',
                    'message': 'Cada item debe contener item_a_title, item_b_title e is_similar'
                }), 400
        
        # Entrenar modelo
        from ml_similarity import train_ml_model
        train_ml_model(training_data)
        
        return jsonify({
            'status': 'success',
            'message': f'Modelo entrenado exitosamente con {len(training_data)} pares de datos',
            'training_samples': len(training_data)
        }), 200
        
    except Exception as e:
        logger.error(f"Error entrenando modelo: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error entrenando modelo: {str(e)}'
        }), 500

@app.route('/ml/status', methods=['GET'])
@swag_from({
    'responses': {
        200: {
            'description': 'Estado del modelo obtenido exitosamente'
        }
    }
})
def get_model_status():
    """Obtener el estado del modelo de Machine Learning"""
    try:
        from ml_similarity import ml_detector
        
        return jsonify({
            'status': 'success',
            'model_trained': ml_detector.is_trained,
            'model_path': ml_detector.model_path,
            'message': 'Modelo entrenado y listo' if ml_detector.is_trained else 'Modelo no entrenado'
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo estado del modelo: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error obteniendo estado del modelo: {str(e)}'
        }), 500
    """Obtener un par específico por ID"""
    try:
        pairs_table = dynamodb.Table(PAIRS_TABLE)
        response = pairs_table.get_item(Key={'pair_id': pair_id})
        
        if 'Item' not in response:
            return jsonify({
                'status': 'error',
                'message': 'Par de ítems no encontrado'
            }), 404
        
        return jsonify({
            'status': 'success',
            'message': 'Par de ítems encontrado exitosamente',
            'pair': response['Item']
        }), 200
        
    except Exception as e:
        logger.error(f"Error en get_pair: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error interno del servidor: {str(e)}'
        }), 500

if __name__ == '__main__':
    # Crear tablas al iniciar
    create_tables()
    
    # Ejecutar la aplicación
    app.run(debug=True, host='0.0.0.0', port=5000) 