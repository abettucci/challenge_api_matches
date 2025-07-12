"""
Script para entrenar el modelo de Machine Learning
"""

import pandas as pd
import json
from ml_similarity import train_ml_model, MLSimilarityDetector
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_training_data_from_csv(csv_path: str) -> List[Dict]:
    """Cargar datos de entrenamiento desde CSV"""
    try:
        df = pd.read_csv(csv_path)
        training_data = []
        
        for _, row in df.iterrows():
            # Asumimos que el CSV tiene columnas item_a_title, item_b_title, is_similar
            training_data.append({
                'item_a_title': str(row.get('item_a_title', '')),
                'item_b_title': str(row.get('item_b_title', '')),
                'is_similar': int(row.get('is_similar', 0))  # 0 o 1
            })
        
        logger.info(f"Cargados {len(training_data)} pares de entrenamiento")
        return training_data
    
    except Exception as e:
        logger.error(f"Error cargando datos de entrenamiento: {e}")
        return []

def create_synthetic_training_data() -> List[Dict]:
    """Crear datos de entrenamiento sintéticos para pruebas"""
    training_data = [
        # Pares similares (is_similar = 1)
        {'item_a_title': 'Telefono movil Samsung', 'item_b_title': 'Telefono celular Samsung', 'is_similar': 1},
        {'item_a_title': 'Laptop HP 15 pulgadas', 'item_b_title': 'Notebook HP 15 inch', 'is_similar': 1},
        {'item_a_title': 'Auriculares bluetooth Sony', 'item_b_title': 'Audifonos bluetooth Sony', 'is_similar': 1},
        {'item_a_title': 'Camara digital Canon', 'item_b_title': 'Camara fotografica Canon', 'is_similar': 1},
        {'item_a_title': 'Tablet iPad 10 pulgadas', 'item_b_title': 'iPad 10 inch tablet', 'is_similar': 1},
        {'item_a_title': 'Smartwatch Apple Watch', 'item_b_title': 'Reloj inteligente Apple', 'is_similar': 1},
        {'item_a_title': 'Teclado mecanico RGB', 'item_b_title': 'Teclado gaming RGB', 'is_similar': 1},
        {'item_a_title': 'Mouse inalambrico Logitech', 'item_b_title': 'Mouse wireless Logitech', 'is_similar': 1},
        
        # Pares diferentes (is_similar = 0)
        {'item_a_title': 'Telefono movil Samsung', 'item_b_title': 'Laptop HP 15 pulgadas', 'is_similar': 0},
        {'item_a_title': 'Auriculares bluetooth Sony', 'item_b_title': 'Camara digital Canon', 'is_similar': 0},
        {'item_a_title': 'Tablet iPad 10 pulgadas', 'item_b_title': 'Teclado mecanico RGB', 'is_similar': 0},
        {'item_a_title': 'Smartwatch Apple Watch', 'item_b_title': 'Mouse inalambrico Logitech', 'is_similar': 0},
        {'item_a_title': 'Telefono movil Samsung', 'item_b_title': 'Auriculares bluetooth Sony', 'is_similar': 0},
        {'item_a_title': 'Laptop HP 15 pulgadas', 'item_b_title': 'Tablet iPad 10 pulgadas', 'is_similar': 0},
        {'item_a_title': 'Camara digital Canon', 'item_b_title': 'Smartwatch Apple Watch', 'is_similar': 0},
        {'item_a_title': 'Teclado mecanico RGB', 'item_b_title': 'Mouse inalambrico Logitech', 'is_similar': 0},
    ]
    
    logger.info(f"Creados {len(training_data)} pares sintéticos de entrenamiento")
    return training_data

def evaluate_model(detector: MLSimilarityDetector, test_data: List[Dict]):
    """Evaluar el modelo entrenado"""
    correct_predictions = 0
    total_predictions = len(test_data)
    
    for pair in test_data:
        title1 = pair['item_a_title']
        title2 = pair['item_b_title']
        expected_similar = bool(pair['is_similar'])
        
        prediction = detector.predict_similarity(title1, title2)
        predicted_similar = prediction['are_similar']
        
        if predicted_similar == expected_similar:
            correct_predictions += 1
        
        logger.info(f"Títulos: '{title1}' vs '{title2}'")
        logger.info(f"  Esperado: {'Similar' if expected_similar else 'Diferente'}")
        logger.info(f"  Predicción: {'Similar' if predicted_similar else 'Diferente'} (score: {prediction['similarity_score']:.3f})")
        logger.info(f"  Confianza: {prediction['confidence']:.3f}")
        logger.info("---")
    
    accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
    logger.info(f"Precisión del modelo: {accuracy:.2%} ({correct_predictions}/{total_predictions})")
    
    return accuracy

def main():
    """Función principal para entrenar el modelo"""
    logger.info("🚀 Iniciando entrenamiento del modelo de similitud...")
    
    # Intentar cargar datos desde CSV
    training_data = load_training_data_from_csv('data_matches - dataset.csv')
    
    # Si no hay datos, usar datos sintéticos
    if not training_data:
        logger.info("No se encontraron datos de entrenamiento, usando datos sintéticos...")
        training_data = create_synthetic_training_data()
    
    # Dividir datos en entrenamiento y validación (80/20)
    split_index = int(len(training_data) * 0.8)
    train_data = training_data[:split_index]
    validation_data = training_data[split_index:]
    
    logger.info(f"Datos de entrenamiento: {len(train_data)} pares")
    logger.info(f"Datos de validación: {len(validation_data)} pares")
    
    # Entrenar modelo
    train_ml_model(train_data, validation_data)
    
    # Evaluar modelo
    detector = MLSimilarityDetector()
    if validation_data:
        logger.info("📊 Evaluando modelo...")
        accuracy = evaluate_model(detector, validation_data)
        
        if accuracy >= 0.8:
            logger.info("✅ Modelo entrenado exitosamente con buena precisión")
        else:
            logger.warning("⚠️ Modelo entrenado pero la precisión es baja")
    
    logger.info("🎉 Entrenamiento completado!")

if __name__ == "__main__":
    main() 