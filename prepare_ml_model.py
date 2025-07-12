"""
Script para preparar el modelo de ML para despliegue
"""

import os
import shutil
import sys

def check_dependencies():
    """Verificar que las dependencias de ML estén instaladas"""
    required_packages = ['pandas', 'xgboost', 'joblib', 'sklearn']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Faltan dependencias: {', '.join(missing_packages)}")
        print("💡 Ejecuta: pip install pandas xgboost joblib scikit-learn")
        return False
    
    print("✅ Todas las dependencias están instaladas")
    return True

try:
    from train_ml_model import main as train_model
except ImportError as e:
    print(f"❌ Error importando train_ml_model: {e}")
    print("💡 Asegúrate de que todas las dependencias estén instaladas")
    sys.exit(1)

def prepare_model_for_deployment():
    """Preparar el modelo para despliegue"""
    print("🚀 Preparando modelo de ML para despliegue...")
    
    # Crear directorio de modelos si no existe
    os.makedirs("models", exist_ok=True)
    
    # Entrenar modelo con datos sintéticos
    print("📊 Entrenando modelo con datos sintéticos...")
    train_model()
    
    # Verificar que el modelo se creó
    model_path = "models/similarity_model.pkl"
    if os.path.exists(model_path):
        print(f"✅ Modelo creado exitosamente en {model_path}")
        
        # Mostrar tamaño del archivo
        size_mb = os.path.getsize(model_path) / (1024 * 1024)
        print(f"📦 Tamaño del modelo: {size_mb:.2f} MB")
        
        return True
    else:
        print("❌ Error: No se pudo crear el modelo")
        return False

def copy_model_to_lambda():
    """Copiar modelo al directorio de Lambda"""
    print("📋 Copiando modelo al directorio de Lambda...")
    
    # Crear directorio si no existe
    os.makedirs("lambda_models", exist_ok=True)
    
    # Copiar modelo
    source = "models/similarity_model.pkl"
    destination = "lambda_models/similarity_model.pkl"
    
    if os.path.exists(source):
        shutil.copy2(source, destination)
        print(f"✅ Modelo copiado a {destination}")
        return True
    else:
        print("❌ Error: Modelo fuente no encontrado")
        return False

if __name__ == "__main__":
    print("🎯 Preparando modelo de Machine Learning...")
    
    # Verificar dependencias primero
    if not check_dependencies():
        print("💥 No se pueden preparar las dependencias")
        sys.exit(1)
    
    # Preparar modelo
    if prepare_model_for_deployment():
        # Copiar para Lambda
        copy_model_to_lambda()
        print("🎉 Modelo preparado exitosamente para despliegue!")
    else:
        print("💥 Error preparando modelo")
        sys.exit(1) 