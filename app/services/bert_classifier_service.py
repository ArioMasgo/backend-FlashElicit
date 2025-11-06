import requests
from typing import List, Dict, Tuple, Optional
import os
from dotenv import load_dotenv
from app.core.model_config import (
    get_binary_endpoint,
    get_multiclass_endpoint,
    get_available_multiclass_models,
    get_multiclass_categories,
    DEFAULT_MULTICLASS_MODEL
)

# Cargar variables de entorno
load_dotenv()

class BERTClassifier:
    """
    Servicio de clasificación usando modelos BERT desplegados en Hugging Face.
    Implementa un sistema de filtrado en cascada:
    1. Clasificación binaria (relevante/no relevante)
    2. Clasificación multiclase (categorías ISO 25010) - Soporte para múltiples modelos
    """

    def __init__(self, default_multiclass_model: str = DEFAULT_MULTICLASS_MODEL):
        """
        Inicializa el clasificador configurando los endpoints de Hugging Face.

        Args:
            default_multiclass_model: Modelo multiclase por defecto a usar (beto, robertuito, etc.)
        """
        print(f"🔧 Configurando cliente de Hugging Face")

        # Obtener token de Hugging Face desde variables de entorno
        self.hf_token = os.getenv('HF_TOKEN')
        if not self.hf_token:
            raise ValueError("❌ HF_TOKEN no encontrado en las variables de entorno")

        # Configurar endpoint binario (único modelo)
        self.binary_endpoint = get_binary_endpoint()

        # Configurar modelo multiclase por defecto
        self.default_multiclass_model = default_multiclass_model

        # Obtener categorías ISO 25010
        self.categories = get_multiclass_categories(default_multiclass_model)

        # Obtener modelos disponibles
        self.available_models = get_available_multiclass_models()

        print("✅ Cliente de Hugging Face configurado exitosamente")
        print(f"✅ Modelo multiclase por defecto: {default_multiclass_model}")
        print(f"✅ Modelos multiclase disponibles: {self.available_models}")
        print(f"✅ Categorías ISO 25010 disponibles: {self.categories}")

    def _query_hf_endpoint(self, endpoint_url: str, texts: List[str]) -> List[Dict]:
        """
        Realiza una consulta al endpoint de Hugging Face.

        Args:
            endpoint_url: URL del endpoint de Hugging Face
            texts: Lista de textos a clasificar

        Returns:
            Respuesta del modelo en formato JSON
        """
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.hf_token}",
            "Content-Type": "application/json"
        }

        # Hugging Face espera el input en este formato
        payload = {
            "inputs": texts,
            "parameters": {}
        }

        try:
            response = requests.post(endpoint_url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"❌ Error al consultar endpoint de Hugging Face: {e}")
            raise

    def classify_binary(self, texts: List[str]) -> List[bool]:
        """
        Clasifica textos usando el modelo binario de Hugging Face.

        Args:
            texts: Lista de comentarios a clasificar

        Returns:
            Lista de booleanos indicando si cada comentario es relevante (True) o no (False)
        """
        if not texts:
            return []

        try:
            # Consultar endpoint de Hugging Face
            results = self._query_hf_endpoint(self.binary_endpoint, texts)

            # Procesar respuesta del modelo
            # Formato: [{"label": "relevante", "score": 0.998}] o [{"label": "no_relevante", "score": 0.998}]
            # Hugging Face devuelve solo la predicción principal (mayor score)
            predictions = []

            for result in results:
                # Cada resultado es ya la predicción con mayor score
                label = result['label']

                # Convertir a booleano
                # El modelo devuelve "relevante" o "no_relevante"
                is_relevant = label.lower() == "relevante"
                predictions.append(is_relevant)

            return predictions

        except Exception as e:
            print(f"❌ Error en clasificación binaria: {e}")
            import traceback
            traceback.print_exc()
            return [False] * len(texts)

    def classify_multiclass(
        self,
        texts: List[str],
        model_name: Optional[str] = None
    ) -> List[Tuple[str, float]]:
        """
        Clasifica textos usando el modelo multiclase de Hugging Face.

        Args:
            texts: Lista de comentarios a clasificar
            model_name: Nombre del modelo a usar (beto, robertuito, etc.).
                       Si es None, usa el modelo por defecto.

        Returns:
            Lista de tuplas (categoría, confianza) para cada comentario
        """
        if not texts:
            return []

        try:
            # Determinar qué modelo usar
            if model_name is None:
                model_name = self.default_multiclass_model

            # Obtener endpoint del modelo seleccionado
            endpoint = get_multiclass_endpoint(model_name)

            print(f"📊 Usando modelo multiclase: {model_name}")

            # Consultar endpoint de Hugging Face
            results = self._query_hf_endpoint(endpoint, texts)

            # Procesar respuesta del modelo
            # Formato: [{"label": "autenticidad", "score": 0.994}]
            # Hugging Face devuelve solo la predicción principal (mayor score)
            predictions = []

            for result in results:
                # Cada resultado es ya la predicción con mayor score
                category = result['label']
                score = result['score']

                # El modelo ya devuelve las categorías legibles directamente
                # (autenticidad, confidencialidad, integridad, no_repudio, resistencia, responsabilidad)
                predictions.append((category, score))

            return predictions

        except Exception as e:
            print(f"❌ Error en clasificación multiclase: {e}")
            import traceback
            traceback.print_exc()
            return [("error", 0.0)] * len(texts)

    def filter_and_classify(
        self,
        reviews: List[Dict],
        batch_size: int = 32,
        multiclass_model: Optional[str] = None
    ) -> List[Dict]:
        """
        Aplica el filtrado en cascada:
        1. Filtra comentarios relevantes usando modelo binario
        2. Clasifica comentarios relevantes usando modelo multiclase

        Args:
            reviews: Lista de diccionarios con información de reviews
            batch_size: Tamaño de lote para procesamiento por lotes
            multiclass_model: Nombre del modelo multiclase a usar (beto, robertuito, etc.).
                            Si es None, usa el modelo por defecto.

        Returns:
            Lista de reviews relevantes con su clasificación multiclase
        """
        if not reviews:
            return []

        print(f"\n🔍 Iniciando filtrado en cascada para {len(reviews)} comentarios")

        # Paso 1: Clasificación binaria
        print("📊 Paso 1: Clasificación binaria (relevante/no relevante)")
        all_texts = [review['comentario'] for review in reviews]

        # Procesar en lotes para eficiencia
        binary_results = []
        for i in range(0, len(all_texts), batch_size):
            batch_texts = all_texts[i:i + batch_size]
            batch_results = self.classify_binary(batch_texts)
            binary_results.extend(batch_results)
            print(f"  Procesados {min(i + batch_size, len(all_texts))}/{len(all_texts)} comentarios")

        # Filtrar solo comentarios relevantes
        relevant_reviews = [
            review for review, is_relevant in zip(reviews, binary_results)
            if is_relevant
        ]

        print(f"✅ Comentarios relevantes: {len(relevant_reviews)}/{len(reviews)} "
              f"({len(relevant_reviews)/len(reviews)*100:.1f}%)")

        if not relevant_reviews:
            print("⚠️ No hay comentarios relevantes después del filtro binario")
            return []

        # Paso 2: Clasificación multiclase
        print("📊 Paso 2: Clasificación multiclase (categorías ISO 25010)")
        relevant_texts = [review['comentario'] for review in relevant_reviews]

        # Procesar en lotes
        multiclass_results = []
        for i in range(0, len(relevant_texts), batch_size):
            batch_texts = relevant_texts[i:i + batch_size]
            batch_results = self.classify_multiclass(batch_texts, model_name=multiclass_model)
            multiclass_results.extend(batch_results)
            print(f"  Clasificados {min(i + batch_size, len(relevant_texts))}/{len(relevant_texts)} comentarios")

        # Agregar clasificación a los reviews
        classified_reviews = []
        for review, (category, confidence) in zip(relevant_reviews, multiclass_results):
            review_with_classification = review.copy()
            review_with_classification['categoria'] = category
            review_with_classification['confianza'] = round(confidence, 4)
            classified_reviews.append(review_with_classification)

        # Estadísticas de categorías
        category_counts = {}
        for review in classified_reviews:
            cat = review['categoria']
            category_counts[cat] = category_counts.get(cat, 0) + 1

        print("✅ Clasificación completada")
        print("📈 Distribución por categorías:")
        for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = count / len(classified_reviews) * 100
            print(f"  {cat}: {count} ({percentage:.1f}%)")

        return classified_reviews


# Singleton para evitar cargar los modelos múltiples veces
_classifier_instance = None

def get_bert_classifier() -> BERTClassifier:
    """
    Obtiene la instancia singleton del clasificador BERT.
    Los modelos se cargan solo una vez durante el ciclo de vida de la aplicación.
    """
    global _classifier_instance
    if _classifier_instance is None:
        print("🚀 Inicializando BERTClassifier (primera vez)...")
        _classifier_instance = BERTClassifier()
    return _classifier_instance
