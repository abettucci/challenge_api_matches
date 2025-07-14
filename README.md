# 🚀 API de Ítems Similares - Meli Data Engineering Challenge

## 📋 Descripción

API RESTful serverless para gestionar pares de ítems similares con validaciones, detección de duplicados y cálculo de similitud automático. El proyecto implementa dos fases de desarrollo: una API Flask para desarrollo local y una API Lambda para producción en AWS.

## 🏗️ Estructura del Proyecto

```
challenge_api_matches/
├── 📁 src/                          # Código fuente principal
│   ├── 🐍 flask/                    # Fase 1: API Flask (Desarrollo Local)
│   ├── ☁️ lambda/                   # Fase 2: API Lambda (Producción AWS)
│   ├── 🤖 ml/                       # Módulo de Machine Learning
│   └── 🛠️ utils/                    # Utilidades compartidas
├── 🏗️ infrastructure/               # Infraestructura como código
├── 📊 data/                         # Datasets y archivos de datos
├── 📚 docs/                         # Documentación completa
└── 🔄 .github/                      # CI/CD Pipeline
```

## 🚀 Características Principales

- **Comparación de ítems**: Determina si dos ítems son iguales, similares o si ya existe el par
- **Prevención de duplicados**: No permite crear pares duplicados
- **Machine Learning**: Modelo XGBoost para mejorar la detección de similitudes
- **Serverless**: AWS Lambda + API Gateway + DynamoDB
- **CI/CD**: Despliegue automático con GitHub Actions
- **Testing**: Cobertura completa con pytest

## 📚 Documentación Completa

Para obtener información detallada sobre:

- **Instalación y configuración**
- **Uso de la API**
- **Desarrollo local**
- **Despliegue en AWS**
- **Testing y validación**
- **Arquitectura y diseño**
- **Machine Learning**
- **Troubleshooting**

👉 **[Ver documentación completa en `docs/README.md`](docs/README.md)**

## 🧪 Testing Rápido

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


## 🚀 Despliegue

El proyecto se despliega automáticamente en AWS mediante GitHub Actions. Solo necesitas:

1. Configurar los secrets de AWS en GitHub
2. Hacer push a la rama main