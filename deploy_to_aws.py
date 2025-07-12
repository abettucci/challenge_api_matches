#!/usr/bin/env python3
"""
Script de despliegue automatizado para AWS Lambda + API Gateway
"""

import os
import sys
import subprocess
import json
import boto3
import zipfile
from botocore.exceptions import ClientError

def run_command(command, description):
    """Ejecutar comando y manejar errores"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completado")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}: {e}")
        print(f"Error output: {e.stderr}")
        sys.exit(1)

def create_deployment_package():
    """Crear paquete de despliegue para Lambda"""
    print("📦 Creando paquete de despliegue...")
    
    # Crear directorio temporal
    if os.path.exists('package'):
        run_command('rm -rf package', 'Limpiando directorio package anterior')
    
    run_command('mkdir package', 'Creando directorio package')
    
    # Instalar dependencias en el directorio package
    run_command('pip install -r requirements.txt -t package/', 'Instalando dependencias')
    
    # Copiar archivos de la aplicación
    run_command('cp app.py package/', 'Copiando app.py')
    run_command('cp lambda_handler.py package/', 'Copiando lambda_handler.py')
    
    # Crear archivo ZIP
    run_command('cd package && zip -r ../lambda_deployment.zip .', 'Creando archivo ZIP')
    
    print("✅ Paquete de despliegue creado: lambda_deployment.zip")

def create_dynamodb_table():
    """Crear tabla DynamoDB"""
    print("🗄️ Creando tabla DynamoDB...")
    
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    
    try:
        table = dynamodb.create_table(
            TableName='item_pairs',
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
        
        # Esperar a que la tabla esté activa
        table.meta.client.get_waiter('table_exists').wait(TableName='item_pairs')
        print("✅ Tabla DynamoDB 'item_pairs' creada exitosamente")
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print("ℹ️ Tabla DynamoDB 'item_pairs' ya existe")
        else:
            print(f"❌ Error creando tabla DynamoDB: {e}")
            sys.exit(1)

def create_lambda_function():
    """Crear función Lambda"""
    print("🔧 Creando función Lambda...")
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    # Verificar si la función ya existe
    try:
        lambda_client.get_function(FunctionName='meli-items-api')
        print("ℹ️ Función Lambda 'meli-items-api' ya existe, actualizando...")
        
        # Actualizar código
        with open('lambda_deployment.zip', 'rb') as zip_file:
            lambda_client.update_function_code(
                FunctionName='meli-items-api',
                ZipFile=zip_file.read()
            )
        
        print("✅ Código de función Lambda actualizado")
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            # Crear nueva función
            try:
                with open('lambda_deployment.zip', 'rb') as zip_file:
                    lambda_client.create_function(
                        FunctionName='meli-items-api',
                        Runtime='python3.9',
                        Role='arn:aws:iam::YOUR_ACCOUNT:role/lambda-dynamodb-role',  # Ajustar
                        Handler='lambda_handler.lambda_handler',
                        Code={'ZipFile': zip_file.read()},
                        Description='API de Ítems Similares para Meli Challenge',
                        Timeout=30,
                        MemorySize=512
                    )
                print("✅ Función Lambda 'meli-items-api' creada exitosamente")
            except ClientError as create_error:
                print(f"❌ Error creando función Lambda: {create_error}")
                print("⚠️ Asegúrate de tener el rol IAM configurado correctamente")
                sys.exit(1)
        else:
            print(f"❌ Error verificando función Lambda: {e}")
            sys.exit(1)

def create_api_gateway():
    """Crear API Gateway"""
    print("🌐 Creando API Gateway...")
    
    api_client = boto3.client('apigateway', region_name='us-east-1')
    
    try:
        # Crear API REST
        api_response = api_client.create_rest_api(
            name='Meli Items API',
            description='API para gestión de ítems similares - Meli Challenge'
        )
        
        api_id = api_response['id']
        root_id = api_response['rootResourceId']
        
        print(f"✅ API Gateway creado con ID: {api_id}")
        
        # Crear recursos y métodos
        create_api_resources(api_client, api_id, root_id)
        
        # Desplegar API
        deployment_response = api_client.create_deployment(
            restApiId=api_id,
            stageName='prod',
            description='Deployment inicial'
        )
        
        api_url = f"https://{api_id}.execute-api.us-east-1.amazonaws.com/prod"
        print(f"✅ API desplegada en: {api_url}")
        
        return api_url
        
    except ClientError as e:
        print(f"❌ Error creando API Gateway: {e}")
        sys.exit(1)

def create_api_resources(api_client, api_id, root_id):
    """Crear recursos y métodos en API Gateway"""
    
    # Crear recurso /health
    health_resource = api_client.create_resource(
        restApiId=api_id,
        parentId=root_id,
        pathPart='health'
    )
    
    # Crear método GET para /health
    api_client.put_method(
        restApiId=api_id,
        resourceId=health_resource['id'],
        httpMethod='GET',
        authorizationType='NONE'
    )
    
    # Integrar con Lambda
    api_client.put_integration(
        restApiId=api_id,
        resourceId=health_resource['id'],
        httpMethod='GET',
        type='AWS_PROXY',
        integrationHttpMethod='POST',
        uri=f'arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:YOUR_ACCOUNT:function:meli-items-api/invocations'
    )
    
    # Crear recurso /items
    items_resource = api_client.create_resource(
        restApiId=api_id,
        parentId=root_id,
        pathPart='items'
    )
    
    # Crear recurso /items/compare
    compare_resource = api_client.create_resource(
        restApiId=api_id,
        parentId=items_resource['id'],
        pathPart='compare'
    )
    
    # Crear método POST para /items/compare
    api_client.put_method(
        restApiId=api_id,
        resourceId=compare_resource['id'],
        httpMethod='POST',
        authorizationType='NONE'
    )
    
    # Integrar con Lambda
    api_client.put_integration(
        restApiId=api_id,
        resourceId=compare_resource['id'],
        httpMethod='POST',
        type='AWS_PROXY',
        integrationHttpMethod='POST',
        uri=f'arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:YOUR_ACCOUNT:function:meli-items-api/invocations'
    )
    
    # Crear recurso /items/pairs
    pairs_resource = api_client.create_resource(
        restApiId=api_id,
        parentId=items_resource['id'],
        pathPart='pairs'
    )
    
    # Crear métodos GET y POST para /items/pairs
    for method in ['GET', 'POST']:
        api_client.put_method(
            restApiId=api_id,
            resourceId=pairs_resource['id'],
            httpMethod=method,
            authorizationType='NONE'
        )
        
        api_client.put_integration(
            restApiId=api_id,
            resourceId=pairs_resource['id'],
            httpMethod=method,
            type='AWS_PROXY',
            integrationHttpMethod='POST',
            uri=f'arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:YOUR_ACCOUNT:function:meli-items-api/invocations'
        )
    
    print("✅ Recursos y métodos de API Gateway creados")

def main():
    """Función principal de despliegue"""
    print("🚀 Iniciando despliegue en AWS...")
    
    # Verificar configuración de AWS
    try:
        boto3.client('sts').get_caller_identity()
        print("✅ Configuración de AWS verificada")
    except Exception as e:
        print("❌ Error en configuración de AWS. Asegúrate de tener AWS CLI configurado")
        print(f"Error: {e}")
        sys.exit(1)
    
    # Pasos de despliegue
    create_deployment_package()
    create_dynamodb_table()
    create_lambda_function()
    api_url = create_api_gateway()
    
    print("\n🎉 ¡Despliegue completado exitosamente!")
    print(f"🌐 URL de la API: {api_url}")
    print(f"📚 Documentación: {api_url}/docs")
    print(f"❤️ Health Check: {api_url}/health")
    
    print("\n📝 Próximos pasos:")
    print("1. Configurar permisos IAM para Lambda")
    print("2. Cargar datos iniciales usando load_initial_data.py")
    print("3. Probar endpoints de la API")

if __name__ == '__main__':
    main() 