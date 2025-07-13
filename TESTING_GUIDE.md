# 🧪 Guía de Testing del API de Ítems Similares

## 📋 Resumen

Esta guía te ayudará a probar el API de Ítems Similares que está desplegado en AWS Lambda. El API permite comparar títulos de productos y determinar si son similares.

## 🚀 URLs del API

- **API Base**: `https://omdl9zog0a.execute-api.us-east-1.amazonaws.com/prod`
- **Health Check**: `https://omdl9zog0a.execute-api.us-east-1.amazonaws.com/prod/health`

## 📦 Instalación de Dependencias

```bash
pip install -r requirements_test.txt
```

## 🧪 Scripts de Testing Disponibles

### 1. **quick_test.py** - Prueba Rápida
```bash
python quick_test.py
```
**Qué hace:**
- ✅ Health check del API
- ✅ Compara ítems similares
- ✅ Compara ítems diferentes
- ✅ Crea un par de ítems
- ✅ Lista todos los pares existentes

**Ideal para:** Verificar que el API funciona correctamente

### 2. **test_api.py** - Testing Completo
```bash
python test_api.py
```
**Qué hace:**
- 📊 Carga datos desde CSV (`data_matches - dataset.csv`)
- 🔄 Procesa todos los pares del dataset
- 📈 Genera análisis detallado de resultados
- 💾 Guarda resultados en CSV
- 📋 Muestra estadísticas completas

**Ideal para:** Análisis completo del dataset

### 3. **s3_data_processor.py** - Procesamiento con S3
```bash
python s3_data_processor.py
```
**Qué hace:**
- ☁️ Sube archivos CSV a S3
- 🔄 Procesa datos en lotes
- 📊 Analiza resultados
- 💾 Guarda resultados en S3 (JSON + CSV)

**Ideal para:** Procesamiento de grandes volúmenes de datos

## 📊 Endpoints del API

### Health Check
```bash
GET /health
```
**Respuesta:**
```json
{
  "status": "success",
  "message": "API de Ítems Similares funcionando correctamente en AWS Lambda",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "environment": "aws-lambda",
  "dynamodb_status": "connected",
  "similarity_method": "basic"
}
```

### Comparar Ítems
```bash
POST /items/compare
```
**Payload:**
```json
{
  "item_a": {
    "item_id": 1,
    "title": "Telefono Samsung Galaxy"
  },
  "item_b": {
    "item_id": 2,
    "title": "Telefono celular Samsung Galaxy"
  }
}
```
**Respuesta:**
```json
{
  "status": "success",
  "message": "Comparación completada exitosamente",
  "similarity_score": 0.857,
  "are_equal": false,
  "are_similar": true,
  "pair_exists": false,
  "pair_id": "1_2"
}
```

### Crear Par de Ítems
```bash
POST /items/pairs
```
**Payload:** Igual que comparar
**Respuesta:**
```json
{
  "status": "success",
  "message": "Par de ítems creado exitosamente",
  "pair_id": "1_2",
  "similarity_score": 0.857,
  "are_equal": false,
  "are_similar": true,
  "action": "created"
}
```

### Obtener Todos los Pares
```bash
GET /items/pairs
```
**Respuesta:**
```json
{
  "status": "success",
  "message": "Se encontraron 5 pares de ítems",
  "pairs": [...],
  "count": 5
}
```

### Obtener Par Específico
```bash
GET /items/pairs/{pair_id}
```
**Respuesta:**
```json
{
  "status": "success",
  "message": "Par de ítems encontrado",
  "pair": {...}
}
```

## 📈 Análisis de Resultados

### Métricas Clave
- **Similarity Score**: 0.0 - 1.0 (Jaccard similarity)
- **Are Similar**: `true` si score ≥ 0.7
- **Are Equal**: `true` si títulos son idénticos
- **Pair Exists**: `true` si el par ya existe en DB

### Interpretación
- **Score 1.0**: Títulos idénticos
- **Score 0.7-0.99**: Títulos muy similares
- **Score 0.3-0.69**: Títulos moderadamente similares
- **Score 0.0-0.29**: Títulos diferentes

## 🔧 Configuración

### Cambiar URL del API
En cada script, modifica la variable `api_url`:
```python
api_url = "https://tu-api-gateway-url.amazonaws.com/prod"
```

### Configurar S3 (para s3_data_processor.py)
```python
bucket_name = "tu-bucket-name"
```

## 📁 Archivos de Salida

### test_api.py
- `api_test_results_YYYYMMDD_HHMMSS.csv`

### s3_data_processor.py
- `s3://bucket/results/api_results_YYYYMMDD_HHMMSS.json`
- `s3://bucket/results/api_results_YYYYMMDD_HHMMSS.csv`

## 🐛 Troubleshooting

### Error 502
- El Lambda function no está respondiendo
- Verificar logs en CloudWatch

### Error 403
- Problemas de permisos IAM
- Verificar DynamoDB permissions

### Error de Timeout
- Lambda function tardando mucho
- Reducir batch_size en s3_data_processor.py

### Error de Conexión
- Verificar URL del API
- Verificar conectividad de red

## 📞 Comandos Útiles

### Verificar Health del API
```bash
curl https://omdl9zog0a.execute-api.us-east-1.amazonaws.com/prod/health
```

### Probar Comparación
```bash
curl -X POST https://omdl9zog0a.execute-api.us-east-1.amazonaws.com/prod/items/compare \
  -H "Content-Type: application/json" \
  -d '{
    "item_a": {"item_id": 1, "title": "Telefono Samsung"},
    "item_b": {"item_id": 2, "title": "Telefono celular Samsung"}
  }'
```

### Listar Pares
```bash
curl https://omdl9zog0a.execute-api.us-east-1.amazonaws.com/prod/items/pairs
```

## 🎯 Próximos Pasos

1. **Ejecutar quick_test.py** para verificar funcionamiento básico
2. **Ejecutar test_api.py** para análisis completo del dataset
3. **Revisar resultados** en los archivos CSV generados
4. **Analizar métricas** de similitud y precisión
5. **Optimizar umbrales** según los resultados

¡Happy Testing! 🚀 