"""
Script de prueba para verificar la selección dinámica de modelos multiclase.
"""
import sys
import io

# Configurar codificación UTF-8 para Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app.services.bert_classifier_service import get_bert_classifier
from app.core.model_config import get_available_multiclass_models

def test_model_registry():
    """Prueba que el registro de modelos funciona correctamente"""
    print("\n" + "=" * 60)
    print("PRUEBA DE REGISTRO DE MODELOS")
    print("=" * 60)

    available_models = get_available_multiclass_models()
    print(f"\nModelos disponibles: {available_models}")

    for model_name in available_models:
        print(f"\n  - {model_name}: OK")

    return available_models

def test_beto_model():
    """Prueba el modelo BETO"""
    print("\n" + "=" * 60)
    print("PRUEBA DE MODELO BETO")
    print("=" * 60)

    classifier = get_bert_classifier()

    test_comments = [
        "No puedo iniciar sesión con mi huella digital",
        "La app solicita permisos innecesarios",
    ]

    print("\nComentarios de prueba:")
    for i, comment in enumerate(test_comments, 1):
        print(f"  {i}. {comment}")

    print("\nClasificando con BETO...")
    results = classifier.classify_multiclass(test_comments, model_name="beto")

    print("\nResultados:")
    for comment, (category, confidence) in zip(test_comments, results):
        print(f"  [{category.upper()}] ({confidence:.2%}): {comment}")

    return results

def test_robertuito_model():
    """Prueba el modelo Robertuito"""
    print("\n" + "=" * 60)
    print("PRUEBA DE MODELO ROBERTUITO")
    print("=" * 60)

    classifier = get_bert_classifier()

    test_comments = [
        "No puedo iniciar sesión con mi huella digital",
        "La app solicita permisos innecesarios",
    ]

    print("\nComentarios de prueba:")
    for i, comment in enumerate(test_comments, 1):
        print(f"  {i}. {comment}")

    print("\nClasificando con Robertuito...")
    results = classifier.classify_multiclass(test_comments, model_name="robertuito")

    print("\nResultados:")
    for comment, (category, confidence) in zip(test_comments, results):
        print(f"  [{category.upper()}] ({confidence:.2%}): {comment}")

    return results

def test_model_comparison():
    """Compara resultados de ambos modelos"""
    print("\n" + "=" * 60)
    print("COMPARACION DE MODELOS")
    print("=" * 60)

    classifier = get_bert_classifier()

    test_comment = "No puedo iniciar sesión con mi huella digital"

    print(f"\nComentario de prueba: {test_comment}")

    # Clasificar con BETO
    print("\nClasificando con BETO...")
    beto_result = classifier.classify_multiclass([test_comment], model_name="beto")
    beto_category, beto_confidence = beto_result[0]

    # Clasificar con Robertuito
    print("Clasificando con Robertuito...")
    robertuito_result = classifier.classify_multiclass([test_comment], model_name="robertuito")
    robertuito_category, robertuito_confidence = robertuito_result[0]

    print("\nComparacion de resultados:")
    print(f"  BETO:       [{beto_category.upper()}] ({beto_confidence:.2%})")
    print(f"  Robertuito: [{robertuito_category.upper()}] ({robertuito_confidence:.2%})")

    if beto_category == robertuito_category:
        print(f"\nAmbos modelos coinciden en la categoria: {beto_category.upper()}")
    else:
        print(f"\nLos modelos difieren:")
        print(f"  BETO predice: {beto_category.upper()}")
        print(f"  Robertuito predice: {robertuito_category.upper()}")

    return {
        "beto": (beto_category, beto_confidence),
        "robertuito": (robertuito_category, robertuito_confidence)
    }

def test_default_model():
    """Prueba el modelo por defecto"""
    print("\n" + "=" * 60)
    print("PRUEBA DE MODELO POR DEFECTO")
    print("=" * 60)

    classifier = get_bert_classifier()

    test_comment = "La aplicación se cae constantemente"

    print(f"\nComentario de prueba: {test_comment}")
    print("Clasificando sin especificar modelo (usa el modelo por defecto)...")

    # No especificar modelo (debería usar BETO por defecto)
    result = classifier.classify_multiclass([test_comment])
    category, confidence = result[0]

    print(f"\nResultado: [{category.upper()}] ({confidence:.2%})")
    print(f"Modelo usado: {classifier.default_multiclass_model}")

    return result

def main():
    """Ejecuta todas las pruebas"""
    try:
        print("\n" + "=" * 60)
        print("INICIANDO PRUEBAS DE SELECCION DINAMICA DE MODELOS")
        print("=" * 60)

        # Prueba 1: Registro de modelos
        available_models = test_model_registry()

        # Prueba 2: Modelo BETO
        beto_results = test_beto_model()

        # Prueba 3: Modelo Robertuito
        robertuito_results = test_robertuito_model()

        # Prueba 4: Comparación de modelos
        comparison = test_model_comparison()

        # Prueba 5: Modelo por defecto
        default_result = test_default_model()

        print("\n" + "=" * 60)
        print("TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("=" * 60)

        return {
            "available_models": available_models,
            "beto_results": beto_results,
            "robertuito_results": robertuito_results,
            "comparison": comparison,
            "default_result": default_result
        }

    except Exception as e:
        print("\n" + "=" * 60)
        print(f"ERROR EN LAS PRUEBAS: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()
