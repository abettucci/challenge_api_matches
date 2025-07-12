#!/bin/bash

# Script para crear una imagen dummy temporal para Lambda
set -e

AWS_REGION="us-east-1"
PROJECT_NAME="meli-challenge"
REPO_NAME="${PROJECT_NAME}-lambda"

echo "🚀 Creando imagen dummy temporal para Lambda..."

# Obtener la URL del repositorio ECR
ECR_REPO_URL=$(terraform -chdir=./terraform-simple output -raw ecr_repository_url)
echo "📦 Repositorio ECR: $ECR_REPO_URL"

# Crear un Dockerfile temporal simple
cat > Dockerfile.dummy << 'EOF'
FROM public.ecr.aws/lambda/python:3.9

# Función dummy simple
COPY <<EOF /var/task/lambda_function.py
def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'body': '{"message": "Dummy function - will be replaced"}'
    }
EOF

CMD ["lambda_function.lambda_handler"]
EOF

# Autenticarse con ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REPO_URL

# Construir y subir imagen dummy
docker build -f Dockerfile.dummy -t $ECR_REPO_URL:dummy .
docker push $ECR_REPO_URL:dummy

# Taggear como latest también
docker tag $ECR_REPO_URL:dummy $ECR_REPO_URL:latest
docker push $ECR_REPO_URL:latest

echo "✅ Imagen dummy creada y subida exitosamente"
echo "🔄 Ahora puedes ejecutar: terraform apply"

# Limpiar
rm -f Dockerfile.dummy 