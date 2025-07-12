import json
import os
import sys
from app import app

def lambda_handler(event, context):
    """Handler para AWS Lambda que adapta Flask a serverless"""
    
    # Configurar variables de entorno para Lambda
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    
    # Obtener información de la petición desde API Gateway
    http_method = event.get('httpMethod', 'GET')
    path = event.get('path', '/')
    headers = event.get('headers', {})
    body = event.get('body', '')
    query_string_parameters = event.get('queryStringParameters', {}) or {}
    
    # Crear contexto de Flask
    with app.test_request_context(
        path=path,
        method=http_method,
        headers=headers,
        data=body,
        query_string=query_string_parameters
    ):
        # Ejecutar la aplicación Flask
        response = app.full_dispatch_request()
        
        # Preparar respuesta para API Gateway
        return {
            'statusCode': response.status_code,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS'
            },
            'body': response.get_data(as_text=True)
        }

def health_check_handler(event, context):
    """Handler específico para health check"""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'status': 'success',
            'message': 'API de Ítems Similares funcionando correctamente en AWS Lambda',
            'timestamp': '2024-01-15T10:30:00.000Z',
            'environment': 'aws-lambda'
        })
    } 