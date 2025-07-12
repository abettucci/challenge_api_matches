# API de Ítems Similares - Meli Data Engineering Challenge

API RESTful serverless para gestionar pares de ítems similares con validaciones, detección de duplicados y cálculo de similitud automático.

## 🚀 Características

- **Comparación de ítems**: Determina si dos ítems son iguales, similares o si ya existe el par
- **Prevención de duplicados**: No permite crear pares duplicados
- **Cálculo de similitud**: Usa TF-IDF y cosine similarity para calcular similitud entre títulos
- **Validaciones**: Valida estructura de datos y campos requeridos
- **Mensajes informativos**: Respuestas claras en español
- **Serverless**: AWS Lambda + API Gateway (sin servidores que administrar)
- **Container Images**: Docker + ECR para manejar dependencias pesadas
- **CI/CD**: Despliegue automático con GitHub Actions
- **Base de datos**: DynamoDB (NoSQL) serverless
- **Pruebas unitarias**: Cobertura completa con pytest

## 🏗️ Arquitectura

### Infraestructura AWS

- **AWS Lambda**: Función serverless con container image
- **ECR**: Repositorio de imágenes Docker
- **API Gateway**: Endpoints REST y routing
- **DynamoDB**: Base de datos NoSQL serverless
- **CloudWatch**: Logs automáticos
- **IAM**: Roles y políticas de seguridad

### Estructura del Proyecto

```
challenge_meli/
├── lambda_app.py           # Aplicación Lambda principal
├── test_app.py            # Pruebas unitarias
├── load_initial_data.py   # Script de carga de datos
├── requirements.txt       # Dependencias Python
├── Dockerfile.lambda      # Dockerfile para Lambda
├── terraform-simple/      # Infraestructura como código
│   ├── main.tf
│   └── variables.tf
├── .github/workflows/     # GitHub Actions
│   └── deploy.yml
└── README.md             # Documentación
```

## 📋 Requisitos

- Python 3.9+
- AWS CLI configurado (para desarrollo local)
- GitHub repository (para CI/CD)

## 🛠️ Instalación y Desarrollo Local

### 1. Clonar el repositorio
```bash
git clone <repository-url>
cd challenge_meli
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar AWS (para desarrollo local)
```bash
aws configure
```

### 4. Ejecutar pruebas
```bash
pytest test_app.py -v
```

## 🚀 Despliegue Automatizado con GitHub Actions

### Configuración de Secrets

En tu repositorio de GitHub, ve a **Settings > Secrets and variables > Actions** y agrega:

- `AWS_ACCESS_KEY_ID`: Tu AWS Access Key
- `AWS_SECRET_ACCESS_KEY`: Tu AWS Secret Key

### Despliegue Automático

1. **Push a main**: El workflow se ejecuta automáticamente
2. **Pull Request**: Se ejecutan las pruebas
3. **Merge a main**: Se despliega automáticamente

### Workflow de GitHub Actions

El workflow `.github/workflows/deploy.yml` automatiza:

- ✅ **Pruebas**: Ejecuta todas las pruebas unitarias
- ✅ **Infraestructura**: Despliega con Terraform
- ✅ **Docker**: Construye imagen con dependencias
- ✅ **ECR**: Sube imagen al repositorio
- ✅ **Lambda**: Actualiza función con nueva imagen
- ✅ **Testing**: Verifica que la API funcione
- ✅ **Comentarios**: Informa URLs en PRs

## 📚 Documentación de la API

### Endpoints Disponibles

#### 1. **Health Check**
```http
GET /health
```

**Respuesta:**
```json
{
  "status": "success",
  "message": "API de Ítems Similares funcionando correctamente en AWS Lambda",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "environment": "aws-lambda"
}
```

#### 2. **Comparar Ítems**
```http
POST /items/compare
```

**Cuerpo de la petición:**
```json
{
  "item_a": {
    "item_id": 123,
    "title": "Telefono movil"
  },
  "item_b": {
    "item_id": 456,
    "title": "Telefono celular"
  }
}
```

**Respuesta exitosa:**
```json
{
  "status": "success",
  "message": "Comparación completada exitosamente",
  "similarity_score": 0.85,
  "are_equal": false,
  "are_similar": true,
  "pair_exists": false,
  "pair_id": "123_456"
}
```

#### 3. **Crear Par de Ítems**
```http
POST /items/pairs
```

**Cuerpo de la petición:**
```json
{
  "item_a": {
    "item_id": 123,
    "title": "Telefono movil"
  },
  "item_b": {
    "item_id": 456,
    "title": "Telefono celular"
  }
}
```

**Respuesta exitosa (nuevo par):**
```json
{
  "status": "success",
  "message": "Par de ítems creado exitosamente",
  "pair_id": "123_456",
  "action": "created"
}
```

**Respuesta (par existente):**
```json
{
  "status": "success",
  "message": "El par de ítems ya existe en la base de datos",
  "pair_id": "123_456",
  "action": "existing"
}
```

#### 4. **Obtener Todos los Pares**
```http
GET /items/pairs
```

**Respuesta:**
```json
{
  "status": "success",
  "message": "Se encontraron 5 pares de ítems",
  "pairs": [
    {
      "pair_id": "123_456",
      "item_a_id": 123,
      "item_a_title": "Telefono movil",
      "item_b_id": 456,
      "item_b_title": "Telefono celular",
      "similarity_score": 0.85,
      "created_at": "2024-01-15T10:30:00.000Z"
    }
  ]
}
```

#### 5. **Obtener Par Específico**
```http
GET /items/pairs/{pair_id}
```

**Respuesta:**
```json
{
  "status": "success",
  "message": "Par de ítems encontrado exitosamente",
  "pair": {
    "pair_id": "123_456",
    "item_a_id": 123,
    "item_a_title": "Telefono movil",
    "item_b_id": 456,
    "item_b_title": "Telefono celular",
    "similarity_score": 0.85,
    "created_at": "2024-01-15T10:30:00.000Z"
  }
}
```

### Códigos de Estado HTTP

- `200`: Operación exitosa
- `201`: Recurso creado exitosamente
- `400`: Datos de entrada inválidos
- `404`: Recurso no encontrado
- `500`: Error interno del servidor

## 🧪 Pruebas

### Ejecutar pruebas localmente
```bash
pytest test_app.py -v
```

### Ejecutar pruebas específicas
```bash
pytest test_app.py::TestCompareItems -v
pytest test_app.py::TestCreateItemPair -v
```

## 📊 Estructura de la Base de Datos

### Tabla: `item_pairs`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| pair_id | String (PK) | ID único del par (formato: "item1_item2") |
| item_a_id | Number | ID del primer ítem |
| item_a_title | String | Título del primer ítem |
| item_b_id | Number | ID del segundo ítem |
| item_b_title | String | Título del segundo ítem |
| similarity_score | Decimal | Puntuación de similitud (0-1) |
| created_at | String | Timestamp de creación |

## 🔍 Algoritmo de Similitud

La API utiliza **TF-IDF + Cosine Similarity** para calcular la similitud entre títulos:

1. **Normalización**: Convertir a minúsculas y eliminar espacios extra
2. **Vectorización**: TF-IDF con n-grams (1-2 palabras)
3. **Cálculo**: Cosine similarity entre vectores
4. **Umbral**: 0.7 para considerar ítems similares

## 🛡️ Validaciones

- **Estructura de datos**: Verifica que `item_a` e `item_b` contengan `item_id` y `title`
- **Tipos de datos**: Valida que `item_id` sea numérico
- **Campos requeridos**: Asegura que todos los campos necesarios estén presentes
- **Duplicados**: Previene la creación de pares duplicados

## 💰 Costos Estimados

Con el free tier de AWS (por mes):
- **Lambda**: 1M requests gratuitos
- **API Gateway**: 1M requests gratuitos
- **DynamoDB**: 25GB + 25WCU/25RCU gratuitos
- **ECR**: 500MB de almacenamiento gratuito
- **CloudWatch**: 5GB de logs gratuitos

**Total**: Prácticamente gratis para desarrollo y pruebas

## 📈 Monitoreo y Logs

- **CloudWatch Logs**: Logs automáticos de Lambda
- **Métricas**: Latencia, errores, requests por minuto
- **Alertas**: Configurables para errores o latencia alta

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto es parte del challenge de Data Engineering de Mercado Libre.

## 📞 Soporte

Para soporte técnico o preguntas sobre el challenge, contactar al equipo de reclutamiento de Mercado Libre. 