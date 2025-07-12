# 🤖 Machine Learning para Detección de Similitudes

## 📋 Descripción

Este módulo implementa un sistema de Machine Learning para mejorar la detección de similitudes entre títulos de productos. Utiliza XGBoost para clasificar si dos títulos son similares o no.

## 🚀 Características

### **Fase 1: XGBoost para Similitud de Títulos** ✅
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

### **Fase 2: Atributos Adicionales** 🔄 (Próximamente)
- Categoría del producto
- Precio
- Marca
- Características técnicas
- Ubicación geográfica

### **Fase 3: LLM para Análisis de Imágenes** 🔄 (Futuro)
- Análisis de imágenes con modelos de visión
- Extracción de características visuales
- Comparación de similitud visual

## 🛠️ Instalación y Uso

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Entrenar modelo
```bash
python train_ml_model.py
```

### 3. Preparar para despliegue
```bash
python prepare_ml_model.py
```

## 📊 API Endpoints

### Entrenar Modelo
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

### Verificar Estado del Modelo
```http
GET /ml/status
```

### Comparar Items (ahora con ML)
```http
POST /items/compare
Content-Type: application/json

{
  "item_a": {
    "item_id": 123,
    "title": "Telefono movil Samsung Galaxy"
  },
  "item_b": {
    "item_id": 456,
    "title": "Telefono celular Samsung Galaxy"
  }
}
```

## 🧠 Arquitectura del Modelo

### Características Extraídas
1. **length_diff**: Diferencia absoluta en longitud de títulos
2. **length_ratio**: Ratio entre longitudes (mín/máx)
3. **word_count_diff**: Diferencia en número de palabras
4. **word_count_ratio**: Ratio entre número de palabras
5. **exact_match**: 1 si son exactamente iguales, 0 si no
6. **contains_same_words**: Jaccard similarity de palabras
7. **tfidf_similarity**: Similitud TF-IDF con cosine similarity

### Configuración XGBoost
- **n_estimators**: 100
- **max_depth**: 6
- **learning_rate**: 0.1
- **eval_metric**: logloss
- **early_stopping**: 10 rounds

## 📈 Evaluación del Modelo

El modelo se evalúa con:
- **Precisión**: Porcentaje de predicciones correctas
- **Validación cruzada**: 80% entrenamiento, 20% validación
- **Métricas**: Accuracy, Precision, Recall, F1-Score

## 🔄 Flujo de Trabajo

### Desarrollo Local
1. `python train_ml_model.py` - Entrenar con datos sintéticos
2. `python prepare_ml_model.py` - Preparar para despliegue
3. Probar endpoints localmente

### Despliegue
1. GitHub Actions ejecuta `prepare_ml_model.py`
2. Modelo se incluye en la imagen Docker
3. Lambda se despliega con el modelo pre-entrenado

## 📁 Estructura de Archivos

```
├── ml_similarity.py          # Módulo principal de ML
├── train_ml_model.py         # Script de entrenamiento
├── prepare_ml_model.py       # Preparación para despliegue
├── models/                   # Modelos entrenados
│   └── similarity_model.pkl  # Modelo XGBoost
└── ML_README.md             # Esta documentación
```

## 🔧 Configuración

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

### Modelo no se carga
```bash
# Verificar que el archivo existe
ls -la models/similarity_model.pkl

# Reentrenar modelo
python train_ml_model.py
```

### Error de dependencias
```bash
# Instalar dependencias de ML
pip install xgboost joblib scikit-learn
```

### Modelo muy pesado
```bash
# Optimizar modelo
# Reducir max_features en TF-IDF
# Usar early stopping
# Comprimir modelo con joblib
```

## 📊 Métricas de Rendimiento

### Tiempo de Predicción
- **Local**: ~10ms por predicción
- **Lambda**: ~50ms por predicción (cold start)

### Precisión del Modelo
- **Datos sintéticos**: ~95%
- **Datos reales**: Depende de la calidad de los datos

### Tamaño del Modelo
- **Modelo completo**: ~2-5MB
- **Compatible con Lambda**: ✅

## 🤝 Contribución

Para agregar nuevas características:

1. Modificar `extract_text_features()` en `ml_similarity.py`
2. Actualizar `prepare_training_data()` si es necesario
3. Ajustar hiperparámetros de XGBoost
4. Probar con nuevos datos de entrenamiento
5. Actualizar documentación

## 📚 Referencias

- [XGBoost Documentation](https://xgboost.readthedocs.io/)
- [Scikit-learn TF-IDF](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html)
- [AWS Lambda ML](https://aws.amazon.com/lambda/features/) 