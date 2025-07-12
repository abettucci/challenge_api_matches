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
        # Pares similares (is_similar = 1) - Más diversidad de vocabulario
        {'item_a_title': 'Telefono movil Samsung Galaxy', 'item_b_title': 'Telefono celular Samsung Galaxy', 'is_similar': 1},
        {'item_a_title': 'Laptop HP Pavilion 15 pulgadas', 'item_b_title': 'Notebook HP Pavilion 15 inch', 'is_similar': 1},
        {'item_a_title': 'Auriculares bluetooth Sony WH1000', 'item_b_title': 'Audifonos bluetooth Sony WH1000', 'is_similar': 1},
        {'item_a_title': 'Camara digital Canon EOS Rebel', 'item_b_title': 'Camara fotografica Canon EOS Rebel', 'is_similar': 1},
        {'item_a_title': 'Tablet iPad Pro 10 pulgadas', 'item_b_title': 'iPad Pro 10 inch tablet', 'is_similar': 1},
        {'item_a_title': 'Smartwatch Apple Watch Series', 'item_b_title': 'Reloj inteligente Apple Watch Series', 'is_similar': 1},
        {'item_a_title': 'Teclado mecanico RGB Corsair', 'item_b_title': 'Teclado gaming RGB Corsair', 'is_similar': 1},
        {'item_a_title': 'Mouse inalambrico Logitech MX', 'item_b_title': 'Mouse wireless Logitech MX', 'is_similar': 1},
        {'item_a_title': 'Monitor LG 27 pulgadas 4K', 'item_b_title': 'Pantalla LG 27 inch 4K', 'is_similar': 1},
        {'item_a_title': 'Impresora HP LaserJet Pro', 'item_b_title': 'Impresora laser HP LaserJet Pro', 'is_similar': 1},
        {'item_a_title': 'Disco duro externo Seagate 1TB', 'item_b_title': 'HDD externo Seagate 1TB', 'is_similar': 1},
        {'item_a_title': 'Memoria RAM DDR4 16GB', 'item_b_title': 'RAM DDR4 16GB memoria', 'is_similar': 1},
        
        # Pares diferentes (is_similar = 0) - Más diversidad
        {'item_a_title': 'Telefono movil Samsung Galaxy', 'item_b_title': 'Laptop HP Pavilion 15 pulgadas', 'is_similar': 0},
        {'item_a_title': 'Auriculares bluetooth Sony WH1000', 'item_b_title': 'Camara digital Canon EOS Rebel', 'is_similar': 0},
        {'item_a_title': 'Tablet iPad Pro 10 pulgadas', 'item_b_title': 'Teclado mecanico RGB Corsair', 'is_similar': 0},
        {'item_a_title': 'Smartwatch Apple Watch Series', 'item_b_title': 'Mouse inalambrico Logitech MX', 'is_similar': 0},
        {'item_a_title': 'Monitor LG 27 pulgadas 4K', 'item_b_title': 'Impresora HP LaserJet Pro', 'is_similar': 0},
        {'item_a_title': 'Disco duro externo Seagate 1TB', 'item_b_title': 'Memoria RAM DDR4 16GB', 'is_similar': 0},
        {'item_a_title': 'Telefono movil Samsung Galaxy', 'item_b_title': 'Auriculares bluetooth Sony WH1000', 'is_similar': 0},
        {'item_a_title': 'Laptop HP Pavilion 15 pulgadas', 'item_b_title': 'Tablet iPad Pro 10 pulgadas', 'is_similar': 0},
        {'item_a_title': 'Camara digital Canon EOS Rebel', 'item_b_title': 'Smartwatch Apple Watch Series', 'is_similar': 0},
        {'item_a_title': 'Teclado mecanico RGB Corsair', 'item_b_title': 'Mouse inalambrico Logitech MX', 'is_similar': 0},
        {'item_a_title': 'Monitor LG 27 pulgadas 4K', 'item_b_title': 'Disco duro externo Seagate 1TB', 'is_similar': 0},
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