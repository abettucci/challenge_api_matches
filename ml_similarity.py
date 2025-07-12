"""
Módulo de Machine Learning para detección de similitudes
Fase 1: XGBoost para similitud de títulos
"""

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import joblib
import os
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class MLSimilarityDetector:
    """Detector de similitudes usando Machine Learning"""
    
    def __init__(self, model_path: str = "models/similarity_model.pkl"):
        self.model_path = model_path
        self.model = None
        self.tfidf_vectorizer = None
        self.scaler = None
        self.is_trained = False
        
        # Crear directorio de modelos si no existe
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # Cargar modelo si existe
        self.load_model()
    
    def extract_text_features(self, title1: str, title2: str) -> Dict[str, float]:
        """Extraer características de texto para comparación"""
        # Normalizar títulos
        title1_norm = title1.lower().strip()
        title2_norm = title2.lower().strip()
        
        # Características básicas de texto
        features = {
            'length_diff': abs(len(title1_norm) - len(title2_norm)),
            'length_ratio': min(len(title1_norm), len(title2_norm)) / max(len(title1_norm), len(title2_norm)) if max(len(title1_norm), len(title2_norm)) > 0 else 0,
            'word_count_diff': abs(len(title1_norm.split()) - len(title2_norm.split())),
            'word_count_ratio': min(len(title1_norm.split()), len(title2_norm.split())) / max(len(title1_norm.split()), len(title2_norm.split())) if max(len(title1_norm.split()), len(title2_norm.split())) > 0 else 0,
            'exact_match': 1.0 if title1_norm == title2_norm else 0.0,
            'contains_same_words': len(set(title1_norm.split()) & set(title2_norm.split())) / len(set(title1_norm.split()) | set(title2_norm.split())) if len(set(title1_norm.split()) | set(title2_norm.split())) > 0 else 0.0,
        }
        
        # TF-IDF similitud
        if self.tfidf_vectorizer:
            try:
                tfidf_matrix = self.tfidf_vectorizer.transform([title1_norm, title2_norm])
                tfidf_similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
                features['tfidf_similarity'] = float(tfidf_similarity)
            except Exception as e:
                logger.warning(f"Error calculating TF-IDF similarity: {e}")
                features['tfidf_similarity'] = 0.0
        else:
            features['tfidf_similarity'] = 0.0
        
        return features
    
    def prepare_training_data(self, item_pairs: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """Preparar datos de entrenamiento desde pares de items"""
        features_list = []
        labels = []
        
        for pair in item_pairs:
            title1 = pair.get('item_a_title', '')
            title2 = pair.get('item_b_title', '')
            is_similar = pair.get('is_similar', 0)  # 0 o 1
            
            features = self.extract_text_features(title1, title2)
            features_list.append(list(features.values()))
            labels.append(is_similar)
        
        return np.array(features_list), np.array(labels)
    
    def train_model(self, training_data: List[Dict], validation_data: Optional[List[Dict]] = None):
        """Entrenar el modelo XGBoost"""
        logger.info("Iniciando entrenamiento del modelo XGBoost...")
        
        # Preparar datos de entrenamiento
        X_train, y_train = self.prepare_training_data(training_data)
        
        # Inicializar y entrenar TF-IDF vectorizer
        all_titles = []
        for pair in training_data:
            all_titles.extend([pair.get('item_a_title', ''), pair.get('item_b_title', '')])
        
        # Verificar que tenemos títulos válidos
        valid_titles = [title for title in all_titles if title and title.strip()]
        if not valid_titles:
            raise ValueError("No hay títulos válidos para entrenar el vectorizer TF-IDF")
        
        logger.info(f"Entrenando TF-IDF con {len(valid_titles)} títulos únicos")
        logger.info(f"Ejemplos de títulos: {valid_titles[:3]}")
        
        self.tfidf_vectorizer = TfidfVectorizer(
            analyzer='word',
            ngram_range=(1, 2),
            max_features=1000,
            min_df=1,  # Cambiar de 2 a 1 para permitir palabras que aparecen solo una vez
            stop_words=None  # No usar stop words para evitar vocabulario vacío
        )
        
        try:
            self.tfidf_vectorizer.fit(valid_titles)
            logger.info(f"TF-IDF vectorizer entrenado con vocabulario de {len(self.tfidf_vectorizer.vocabulary_)} palabras")
        except Exception as e:
            logger.error(f"Error entrenando TF-IDF vectorizer: {e}")
            logger.error(f"Títulos de ejemplo: {valid_titles[:5]}")
            raise
        
        # Recalcular características con TF-IDF entrenado
        X_train, y_train = self.prepare_training_data(training_data)
        
        # Normalizar características
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        # Configurar y entrenar XGBoost
        self.model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            eval_metric='logloss'
        )
        
        # Entrenar modelo
        if validation_data:
            X_val, y_val = self.prepare_training_data(validation_data)
            X_val_scaled = self.scaler.transform(X_val)
            
            self.model.fit(
                X_train_scaled, y_train,
                eval_set=[(X_val_scaled, y_val)],
                early_stopping_rounds=10,
                verbose=False
            )
        else:
            self.model.fit(X_train_scaled, y_train)
        
        self.is_trained = True
        logger.info("Modelo entrenado exitosamente")
        
        # Guardar modelo
        self.save_model()
    
    def predict_similarity(self, title1: str, title2: str) -> Dict[str, float]:
        """Predecir similitud entre dos títulos"""
        if not self.is_trained:
            logger.warning("Modelo no entrenado, usando similitud básica")
            return self._basic_similarity(title1, title2)
        
        # Extraer características
        features = self.extract_text_features(title1, title2)
        features_array = np.array(list(features.values())).reshape(1, -1)
        
        # Normalizar características
        features_scaled = self.scaler.transform(features_array)
        
        # Predecir
        similarity_score = self.model.predict_proba(features_scaled)[0][1]  # Probabilidad de ser similar
        
        return {
            'similarity_score': float(similarity_score),
            'are_equal': title1.lower().strip() == title2.lower().strip(),
            'are_similar': similarity_score >= 0.7,  # Umbral configurable
            'confidence': float(max(self.model.predict_proba(features_scaled)[0]))
        }
    
    def _basic_similarity(self, title1: str, title2: str) -> Dict[str, float]:
        """Similitud básica como fallback"""
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        
        title1_norm = title1.lower().strip()
        title2_norm = title2.lower().strip()
        
        if title1_norm == title2_norm:
            return {
                'similarity_score': 1.0,
                'are_equal': True,
                'are_similar': True,
                'confidence': 1.0
            }
        
        vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1, 2), stop_words=None)
        tfidf_matrix = vectorizer.fit_transform([title1_norm, title2_norm])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        return {
            'similarity_score': float(similarity),
            'are_equal': False,
            'are_similar': similarity >= 0.7,
            'confidence': 0.8
        }
    
    def save_model(self):
        """Guardar modelo entrenado"""
        if self.is_trained:
            model_data = {
                'model': self.model,
                'tfidf_vectorizer': self.tfidf_vectorizer,
                'scaler': self.scaler,
                'feature_names': list(self.extract_text_features('', '').keys())
            }
            joblib.dump(model_data, self.model_path)
            logger.info(f"Modelo guardado en {self.model_path}")
    
    def load_model(self):
        """Cargar modelo entrenado"""
        try:
            if os.path.exists(self.model_path):
                model_data = joblib.load(self.model_path)
                self.model = model_data['model']
                self.tfidf_vectorizer = model_data['tfidf_vectorizer']
                self.scaler = model_data['scaler']
                self.is_trained = True
                logger.info(f"Modelo cargado desde {self.model_path}")
        except Exception as e:
            logger.warning(f"No se pudo cargar el modelo: {e}")
            self.is_trained = False

# Instancia global del detector
ml_detector = MLSimilarityDetector()

def get_ml_similarity(title1: str, title2: str) -> Dict[str, float]:
    """Función de conveniencia para obtener similitud ML"""
    return ml_detector.predict_similarity(title1, title2)

def train_ml_model(training_data: List[Dict], validation_data: Optional[List[Dict]] = None):
    """Función de conveniencia para entrenar el modelo"""
    ml_detector.train_model(training_data, validation_data) 