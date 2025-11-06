"""
Configuración centralizada de modelos de clasificación.
Este archivo facilita la gestión y adición de nuevos modelos.
"""
from typing import Dict, List
from enum import Enum

class ModelType(str, Enum):
    """Tipos de modelos disponibles"""
    BINARY = "binary"
    MULTICLASS = "multiclass"

class MulticlassModel(str, Enum):
    """Modelos multiclase disponibles"""
    BETO = "beto"
    ROBERTUITO = "robertuito"

# Configuración de modelos
MODEL_REGISTRY = {
    # Modelo binario (único)
    "binary": {
        "endpoint": "https://y2whvh4mzq1gtwcl.us-east-1.aws.endpoints.huggingface.cloud",
        "description": "Modelo BERT para clasificación binaria (relevante/no_relevante)",
        "labels": ["relevante", "no_relevante"]
    },

    # Modelos multiclase (múltiples opciones)
    "multiclass": {
        "beto": {
            "endpoint": "https://ykuu4cwn6pi9tuej.us-east-1.aws.endpoints.huggingface.cloud",
            "description": "Modelo BETO para clasificación multiclase ISO 25010",
            "base_model": "dccuchile/bert-base-spanish-wwm-uncased",
            "labels": [
                "autenticidad",
                "confidencialidad",
                "integridad",
                "no_repudio",
                "resistencia",
                "responsabilidad"
            ]
        },
        "robertuito": {
            "endpoint": "https://ddqh9l52kwsfynev.us-east-1.aws.endpoints.huggingface.cloud",
            "description": "Modelo Robertuito para clasificación multiclase ISO 25010",
            "base_model": "pysentimiento/robertuito-base-uncased",
            "labels": [
                "autenticidad",
                "confidencialidad",
                "integridad",
                "no_repudio",
                "resistencia",
                "responsabilidad"
            ]
        }
    }
}

def get_binary_endpoint() -> str:
    """Obtiene el endpoint del modelo binario"""
    return MODEL_REGISTRY["binary"]["endpoint"]

def get_multiclass_endpoint(model_name: str) -> str:
    """
    Obtiene el endpoint de un modelo multiclase específico.

    Args:
        model_name: Nombre del modelo (beto, robertuito, etc.)

    Returns:
        URL del endpoint del modelo

    Raises:
        ValueError: Si el modelo no existe
    """
    model_name = model_name.lower()
    if model_name not in MODEL_REGISTRY["multiclass"]:
        available_models = list(MODEL_REGISTRY["multiclass"].keys())
        raise ValueError(
            f"Modelo '{model_name}' no encontrado. "
            f"Modelos disponibles: {', '.join(available_models)}"
        )
    return MODEL_REGISTRY["multiclass"][model_name]["endpoint"]

def get_available_multiclass_models() -> List[str]:
    """Obtiene la lista de modelos multiclase disponibles"""
    return list(MODEL_REGISTRY["multiclass"].keys())

def get_multiclass_categories(model_name: str = "beto") -> List[str]:
    """
    Obtiene las categorías ISO 25010 que puede clasificar un modelo.

    Args:
        model_name: Nombre del modelo

    Returns:
        Lista de categorías
    """
    model_name = model_name.lower()
    if model_name not in MODEL_REGISTRY["multiclass"]:
        # Por defecto retorna las categorías de BETO
        return MODEL_REGISTRY["multiclass"]["beto"]["labels"]
    return MODEL_REGISTRY["multiclass"][model_name]["labels"]

def get_model_info(model_name: str) -> Dict:
    """
    Obtiene información completa de un modelo multiclase.

    Args:
        model_name: Nombre del modelo

    Returns:
        Diccionario con información del modelo
    """
    model_name = model_name.lower()
    if model_name not in MODEL_REGISTRY["multiclass"]:
        raise ValueError(f"Modelo '{model_name}' no encontrado")
    return MODEL_REGISTRY["multiclass"][model_name]

# Modelo por defecto
DEFAULT_MULTICLASS_MODEL = "beto"
