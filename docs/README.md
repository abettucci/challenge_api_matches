# 🚀 API de Ítems Similares - Meli Data Engineering Challenge

## 📋 Descripción General

API RESTful serverless para gestionar pares de ítems similares. El proyecto tiene dos formatos: uno en entorno local (Flask) y otro en entorno cloud (API Lambda en AWS).

## 🏗️ Arquitectura del Proyecto

### Estructura de Carpetas

```
challenge_api_matches/
├── 📁 src/                          # Código fuente principal
│   ├── 🐍 flask/                    # Fase 1: API Flask (Desarrollo Local)
│   │   ├── app.py                   # Aplicación Flask principal
│   │   ├── requirements.txt         # Dependencias Flask
│   │   └── tests/                   # Tests unitarios Flask
│   │
│   ├── ☁️ lambda/                   # Fase 2: API Lambda (Producción AWS)
│   │   ├── lambda_app.py            # Lambda con ML integrado
│   │   ├── lambda_app_simple.py     # Lambda simplificado
│   │   ├── Dockerfile.lambda        # Docker para Lambda
│   │   └── tests/                   # Tests de integración
│   │       └── test_api.py          # Tests completos del dataset
│   │
│   └── 🤖 ml/                       # Módulo de Machine Learning
│       ├── ml_similarity.py         # Módulo principal de ML
│       ├── train_ml_model.py        # Script de entrenamiento
│       └── prepare_ml_model.py      # Preparación para despliegue
│
├── 🏗️ infrastructure/               # Infraestructura como código
│   └── terraform-simple/            # Configuración Terraform
│       ├── main.tf                  # Recursos AWS
│       └── variables.tf             # Variables de configuración
│
├── 📊 data/                         # Datasets y archivos de datos
│   └── data_matches - dataset.csv   # Dataset principal (28 pares)
│   ├── s3_data_processor.py         # Procesamiento de datos S3
│   └── load_initial_data.py         # Carga inicial de datos
│
├── 📚 docs/                         # Documentación completa
│   ├── README.md                    # README original
│   └── Challenge Meli Matches.pdf   # Consigna original
│
├── 🔄 .github/                      # CI/CD Pipeline
│   └── workflows/
│       └── deploy.yml               # GitHub Actions
│
└── 📄 Archivos de configuración
    ├── .gitignore                   # Archivos ignorados por Git
    └── .dockerignore                # Archivos ignorados por Docker
```

## 🚀 Características Principales

### ✅ Funcionalidades Implementadas

- **Comparación de ítems**: Determina si dos ítems son iguales, similares o si ya existe el par.
- **Prevención de duplicados**: No permite crear pares duplicados.
- **Cálculo de similitud**: Uso de TF-IDF y cosine similarity para calcular similitud entre títulos.
- **Machine Learning**: uso de modelo XGBoost para mejorar la detección de similitudes.
- **Validaciones**: Valida estructura de datos y campos requeridos.
- **Mensajes informativos**: Respuestas claras en español.
- **Serverless**: AWS Lambda + API Gateway.
- **Container Images**: Docker + ECR para manejar dependencias pesadas.
- **CI/CD**: Despliegue automático con GitHub Actions.
- **Base de datos**: DynamoDB (NoSQL) serverless.
- **Pruebas unitarias**: Cobertura completa con pytest.

### 🎯 Interpretación de la logica de generación

1. **Si los pares ya existen y es positivo** → **NO se regeneran**
   - Mensaje: "No se regenera porque ya existe ese par en la base de datos con status positivo"

2. **Si los pares ya existen y son negativos** → **SÍ se regeneran**
   - Mensaje: "Se regenera porque el par existente tiene status negativo"

3. **Si los pares no existen** → **Se crean nuevos**
   - Mensaje: "Se crea nuevo par en la base de datos"

## 🏗️ Infraestructura AWS

### Componentes Utilizados

- **AWS Lambda**: Función serverless con container image
- **ECR**: Repositorio de imágenes Docker
- **API Gateway**: Endpoints REST y routing
- **DynamoDB**: Base de datos NoSQL serverless
- **CloudWatch**: Logs automáticos
- **IAM**: Roles y políticas de seguridad

### Estructura de Base de Datos (DynamoDB)

La tabla `item_pairs` usa la estructura correcta según la consigna:

```json
{
  "id": "1_2",                    // Identificador único del par (id_a + id_b)
  "title": "Título A | Título B", // Título combinado de ambos ítems
  "status": "positivo",           // Estado: "positivo", "negativo", "en progreso"
  "created_at": "2024-01-01T00:00:00", // Fecha y hora de creación
  "updated_at": "2024-01-01T00:00:00"  // Fecha y hora de última actualización
}
```
## 📖 Endpoints principales de la API (Flask y Lambda)

- El formato de `pair_id` suele ser `itemA_itemB` (por ejemplo, `1_2`).
- Esto funciona igual tanto en Flask local como en Lambda AWS.

| Entorno    | Método | Endpoint                                 | Descripción                        | Ejemplo de uso (curl)                                                        |
|------------|--------|------------------------------------------|------------------------------------|-------------------------------------------------------------------------------|
| **Flask**  | GET    | `/items/pairs`                           | Listar todos los pares             | `curl http://localhost:5000/items/pairs`                                      |
| **Flask**  | GET    | `/items/pairs/<pair_id>`                 | Obtener un par por ID              | `curl http://localhost:5000/items/pairs/1_2`                                  |
| **Flask**  | POST   | `/items/compare`                         | Comparar dos ítems                 | `curl -X POST http://localhost:5000/items/compare -H "Content-Type: application/json" -d '{"item_a": {"item_id": 1, "title": "A"}, "item_b": {"item_id": 2, "title": "B"}}'` |
| **Flask**  | POST   | `/items/pairs`                           | Crear un par de ítems              | `curl -X POST http://localhost:5000/items/pairs -H "Content-Type: application/json" -d '{"item_a": {"item_id": 1, "title": "A"}, "item_b": {"item_id": 2, "title": "B"}}'` |
| **Lambda** | GET    | `/items/pairs`                           | Listar todos los pares             | `curl https://<api-id>.execute-api.<region>.amazonaws.com/prod/items/pairs`   |
| **Lambda** | GET    | `/items/pairs/<pair_id>`                 | Obtener un par por ID              | `curl https://<api-id>.execute-api.<region>.amazonaws.com/prod/items/pairs/1_2` |
| **Lambda** | POST   | `/items/compare`                         | Comparar dos ítems                 | `curl -X POST https://<api-id>.execute-api.<region>.amazonaws.com/prod/items/compare -H "Content-Type: application/json" -d '{"item_a": {"item_id": 1, "title": "A"}, "item_b": {"item_id": 2, "title": "B"}}'` |
| **Lambda** | POST   | `/items/pairs`                           | Crear un par de ítems              | `curl -X POST https://<api-id>.execute-api.<region>.amazonaws.com/prod/items/pairs -H "Content-Type: application/json" -d '{"item_a": {"item_id": 1, "title": "A"}, "item_b": {"item_id": 2, "title": "B"}}'` |

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

## 🤖 Bonus: Módulo de Machine Learning

### Características del Modelo

- **Modelo XGBoost** entrenado con características de texto
- **TF-IDF Vectorization** para capturar similitud semántica
- **Características de texto**:
  - Diferencia de longitud
  - Ratio de longitud
  - Diferencia en número de palabras
  - Ratio de palabras
  - Coincidencia exacta
  - Palabras compartidas
  - Similitud TF-IDF

### Configuración XGBoost (iterar a futuro)
- **n_estimators**: 100
- **max_depth**: 6
- **learning_rate**: 0.1
- **eval_metric**: logloss
- **early_stopping**: 10 rounds

### Endpoints ML

#### Entrenar Modelo (posible mejora a futuro)
```http
POST /ml/train
Content-Type: application/json

{
  "training_data": [
    {
      "item_a_title": "Telefono movil Samsung",
      "item_b_title": "Telefono celular Samsung",
      "is_similar": 1
    },
    {
      "item_a_title": "Telefono movil Samsung",
      "item_b_title": "Laptop HP 15 pulgadas",
      "is_similar": 0
    }
  ]
}
```

## 🤖 Comparar resultados de clasificación con/sin ML

Comparar como cambia la clasificación de pares de ítems usando XG Boost vs. TF-IDF + cosine similarity.

### 1. Probar un par con y sin ML desde la API

A través del parámetro `use_ml` en el body de los endpoints `/items/compare` o `/items/pairs` se determina con que metodo calcular la similitud del par de items:

- Forzar con ML:
```json
{
  "item_a": {"item_id": 1, "title": "Telefono movil"},
  "item_b": {"item_id": 2, "title": "Telefono celular"},
  "use_ml": true
}
```
- Forzar sin ML:
```json
{
  "item_a": {"item_id": 1, "title": "Telefono movil"},
  "item_b": {"item_id": 2, "title": "Telefono celular"},
  "use_ml": false
}
```

### 2. Comparar todo el dataset automáticamente

Ejecuta el script:
```bash
cd src/app_flask
python compare_ml_vs_traditional.py
```

Esto recorrerá el dataset y mostrará para cada par:
- El score de similitud con y sin ML
- Cuáles pares cambian de negativo a positivo (o viceversa)
- Estadísticas de cuántos pares son positivos con cada método

### 3. Interpretar los resultados
- **Total positivos sin ML:** Pares clasificados como similares usando solo el método tradicional.
- **Total positivos con ML:** Pares clasificados como similares usando el modelo de Machine Learning.
- **Diferencia de positivos:** Cuántos pares adicionales (o menos) son considerados similares al usar ML.

Esto te permite demostrar el valor agregado del modelo ML frente al método tradicional.

## 🛠️ Instalación y Desarrollo Local

### Requisitos

- Python 3.9+
- AWS CLI configurado (para desarrollo local)
- GitHub repository (para CI/CD)

### 1. Clonar el repositorio
```bash
git clone <repository-url>
cd challenge_api_matches
```

### 2. Instalar dependencias Flask (Fase 1)
```bash
cd src/flask
pip install -r requirements.txt
```

### 3. Configurar AWS (para desarrollo local)
```bash
aws configure
```

### 4. Ejecutar API Flask localmente
```bash
cd src/flask
python app.py
```

### 5. Ejecutar pruebas
```bash
cd src/lambda/tests
python test_api.py
```

## 🚀 Ejecución Local: Flask + DynamoDB Local (Docker)

Puedes correr toda la solución Flask de forma 100% local, sin depender de AWS, usando DynamoDB Local en Docker.

### 1. Requisitos previos
- **Python 3.8+**
- **Docker** (https://www.docker.com/get-started)
- **pip** (gestor de paquetes de Python)

### 2. Instalar dependencias Python
```bash
cd src/app_flask
pip install -r requirements.txt
```

### 3. Levantar DynamoDB Local con Docker
```bash
docker run -d -p 8000:8000 --name dynamodb-local amazon/dynamodb-local
```
Esto crea un contenedor llamado `dynamodb-local` escuchando en el puerto 8000.

### 4. Configurar variable de entorno para Flask
En Linux/Mac:
```bash
export AWS_ENDPOINT_URL=http://localhost:8000
```
En Windows PowerShell:
```powershell
$env:AWS_ENDPOINT_URL="http://localhost:8000"
```

### 5. Ejecutar la API Flask
```bash
python app.py
```

### 6. (Opcional) Crear las tablas en DynamoDB Local
La app Flask intentará crear las tablas automáticamente al inicio. Si necesitas forzar la creación, revisa la función `create_tables()` en `app.py`.

### 7. Acceder a la API
- Swagger UI: [http://localhost:5000/docs](http://localhost:5000/docs)
- Endpoints: [http://localhost:5000/](http://localhost:5000/)

### 8. Detener DynamoDB Local
```bash
docker stop dynamodb-local && docker rm dynamodb-local
```

### Notas
- No necesitas una cuenta de AWS ni credenciales para correr en modo local.
- Todo el almacenamiento es efímero (se borra al eliminar el contenedor Docker).
- Si quieres persistencia, puedes montar un volumen Docker.

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

### **Forma recomendada (usando working-directory):**

```yaml
- name: Prepare ML Model
  working-directory: ./src/ml
  run: |
    echo "Preparing ML model for deployment..."
    python prepare_ml_model.py
```

Esto asegura que el script se ejecute en la carpeta correcta y que cualquier archivo generado (como el modelo) quede en el lugar esperado.

---

### **Alternativa (usando el path completo):**

Si prefieres no usar `working-directory`, puedes hacer:

```yaml
- name: Prepare ML Model
  run: |
    echo "Preparing ML model for deployment..."
    python src/ml/prepare_ml_model.py
```

Ambas opciones son válidas, pero la primera es más robusta si el script usa rutas relativas.

---

**¡Con este cambio, el error de “No such file or directory” desaparecerá y el modelo ML se preparará correctamente en el pipeline!**

¿Te gustaría que revise si hay otros pasos con problemas de path en tu workflow?

## 🧪 Testing y Validación

### Scripts de Testing Disponibles

#### **Test Completo del Dataset**
```bash
# Test completo del dataset (con solucion cloud)
cd src/lambda/tests
python test_api.py
```

```bash
# Test completo del dataset (con solucion local)
cd src/app_flask
pytest tests/test_flask_api.py
```

**Características:**
- Procesa todos los 28 pares del dataset
- Muestra estadísticas detalladas
- Genera CSV con resultados
- Valida lógica de regeneración

### Ejemplo de Salida del Test Completo

```
📊 ANÁLISIS DE RESULTADOS
================================================================================
📈 Estadísticas Generales:
   • Total de pares analizados: 28
   • Pares similares: 15 (53.6%)
   • Pares iguales: 2 (7.1%)
   • Pares ya existentes: 5 (17.9%)
   • Pares con status positivo: 17 (60.7%)
   • Pares con status negativo: 11 (39.3%)
   • Pares creados/actualizados: 23
   • Pares omitidos (ya positivos): 5

🔍 Análisis Detallado:
   1. ✅ POSITIVO - 🔄 REGENERADO/CREADO
      A: Telefono Samsung Galaxy
      B: Telefono celular Samsung Galaxy
      Similitud: 0.850
      Nuevo status: positivo
      Nota: Se crea nuevo par en la base de datos

   2. ⏭️ OMITIDO
      A: Laptop HP 15 pulgadas
      B: Notebook HP 15 inch
      Similitud: 0.750
      Status existente: positivo
      Nota: No se regenera porque ya existe ese par en la base de datos con status positivo
```

## 📊 Métricas de Calidad

### Cobertura de Testing
- **Total de pares**: 28 pares del dataset original
- **Cobertura**: 100% de los pares procesados
- **Validación**: Lógica de regeneración verificada

### Rendimiento
- **Tiempo de respuesta**: < 100ms por comparación
- **Cold start**: ~2-3 segundos (Lambda)
- **Warm start**: < 100ms

### Precisión del Modelo ML
- **Datos sintéticos**: ~95%
- **Datos reales**: Depende de la calidad de los datos
- **Tamaño del modelo**: ~2-5MB (compatible con Lambda)

## 🔧 Configuración y Personalización

### Umbral de Similitud
```python
# En ml_similarity.py
'are_similar': similarity_score >= 0.7  # Configurable
```

### Características TF-IDF
```python
# Configuración del vectorizer
TfidfVectorizer(
    analyzer='word',
    ngram_range=(1, 2),  # Unigramas y bigramas
    max_features=1000,   # Máximo 1000 características
    min_df=2            # Mínimo 2 documentos
)
```

## 🚀 Próximas Mejoras

### Fase 2: Atributos Adicionales
- [ ] Integrar categorías de productos
- [ ] Análisis de precios
- [ ] Comparación de marcas
- [ ] Características técnicas

### Fase 3: Análisis de Imágenes
- [ ] Integración con modelos de visión (CLIP, ResNet)
- [ ] Extracción de características visuales
- [ ] Comparación de similitud visual
- [ ] Análisis de colores y patrones

## 🐛 Troubleshooting

### Problemas Comunes

#### Modelo no se carga
```bash
# Verificar que el archivo existe
ls -la src/ml/models/similarity_model.pkl

# Reentrenar modelo
cd src/ml
python train_ml_model.py
```

#### Error de dependencias
```bash
# Instalar dependencias de ML
pip install xgboost joblib scikit-learn

# Instalar dependencias básicas
pip install -r requirements_basic.txt
```

#### Error de AWS credentials
```bash
# Configurar AWS CLI
aws configure

# Verificar configuración
aws sts get-caller-identity
```

#### Error de DynamoDB
```bash
# Verificar tabla existe
aws dynamodb describe-table --table-name item_pairs
```

## 🧪 Ejemplos de comparación de ítems en Flask

Puedes probar rápidamente la API Flask con 5 pares de ejemplo (igual que en Lambda) usando el script:

```bash
cd src/app_flask
python test_flask_examples.py
```

Esto mostrará en consola, para cada par:
- Los títulos de los ítems
- El score de similitud
- Si son similares o iguales
- El status y el mensaje de la API

**Ejemplo de salida:**
```
=== Ejemplos de comparación de ítems (Flask) ===

Ejemplo 1:
  A: Telefono Samsung Galaxy
  B: Telefono celular Samsung Galaxy
  Similarity: 0.85
  Are similar: True
  Status: success
  Mensaje: Comparación completada exitosamente

...
```

Esto te permite comparar fácilmente el comportamiento de Flask y Lambda con los mismos pares de ejemplo.