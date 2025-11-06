"""
Script de prueba para verificar la integración con Hugging Face endpoints.
"""
import sys
import io

# Configurar codificación UTF-8 para Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app.services.bert_classifier_service import get_bert_classifier

def test_binary_classification():
    """Prueba el modelo de clasificación binaria"""
    print("\n" + "=" * 60)
    print("PRUEBA DE CLASIFICACION BINARIA")
    print("=" * 60)

    classifier = get_bert_classifier()

    # Comentarios de prueba
    test_comments = [
        "No puedo iniciar sesión con mi huella digital",  # Debería ser relevante
        "Me gusta mucho la app, es muy bonita",  # No debería ser relevante
        "La aplicación se cierra cuando intento hacer pagos",  # Debería ser relevante
        "Excelente interfaz de usuario",  # No debería ser relevante
    ]

    print("\nComentarios de prueba:")
    for i, comment in enumerate(test_comments, 1):
        print(f"  {i}. {comment}")

    print("\nClasificando...")
    results = classifier.classify_binary(test_comments)

    print("\nResultados:")
    for comment, is_relevant in zip(test_comments, results):
        relevance = "[RELEVANTE]" if is_relevant else "[NO RELEVANTE]"
        print(f"  {relevance}: {comment}")

    return results

def test_multiclass_classification():
    """Prueba el modelo de clasificación multiclase"""
    print("\n" + "=" * 60)
    print("PRUEBA DE CLASIFICACION MULTICLASE")
    print("=" * 60)

    classifier = get_bert_classifier()

    # Comentarios relevantes para clasificar en categorías ISO 25010
    test_comments = [
        "No puedo iniciar sesión con mi huella digital",  # Autenticidad
        "La app solicita permisos innecesarios",  # Confidencialidad
        "Se pierden los datos guardados",  # Integridad
        "La aplicación se cae constantemente",  # Resistencia
    ]

    print("\nComentarios de prueba:")
    for i, comment in enumerate(test_comments, 1):
        print(f"  {i}. {comment}")

    print("\nClasificando...")
    results = classifier.classify_multiclass(test_comments)

    print("\nResultados:")
    for comment, (category, confidence) in zip(test_comments, results):
        print(f"  [{category.upper()}] ({confidence:.2%}): {comment}")

    return results

def test_full_pipeline():
    """Prueba el pipeline completo (binario + multiclase)"""
    print("\n" + "=" * 60)
    print("PRUEBA DE PIPELINE COMPLETO")
    print("=" * 60)

    classifier = get_bert_classifier()

    # Reviews de prueba con diferentes características
    test_reviews = [
        {"comentario": "No puedo iniciar sesión con mi huella digital", "calificacion": 1},
        {"comentario": "Me encanta la app, muy linda", "calificacion": 5},
        {"comentario": "La aplicación se cierra cuando intento hacer pagos", "calificacion": 2},
        {"comentario": "Excelente diseño y colores", "calificacion": 5},
        {"comentario": "Solicita permisos de ubicación sin razón", "calificacion": 1},
    ]

    print("\nReviews de prueba:")
    for i, review in enumerate(test_reviews, 1):
        print(f"  {i}. [{review['calificacion']} estrellas] {review['comentario']}")

    print("\nProcesando pipeline completo...")
    results = classifier.filter_and_classify(test_reviews)

    print(f"\nTotal de reviews: {len(test_reviews)}")
    print(f"Reviews relevantes: {len(results)}")

    if results:
        print("\nReviews clasificados:")
        for review in results:
            print(f"  [{review['categoria'].upper()}] ({review['confianza']:.2%})")
            print(f"    {review['comentario']}")
            print()

    return results

def main():
    """Ejecuta todas las pruebas"""
    try:
        print("\n" + "=" * 60)
        print("INICIANDO PRUEBAS DE INTEGRACION CON HUGGING FACE")
        print("=" * 60)

        # Prueba 1: Clasificación binaria
        binary_results = test_binary_classification()

        # Prueba 2: Clasificación multiclase
        multiclass_results = test_multiclass_classification()

        # Prueba 3: Pipeline completo
        pipeline_results = test_full_pipeline()

        print("\n" + "=" * 60)
        print("TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("=" * 60)

        return {
            "binary": binary_results,
            "multiclass": multiclass_results,
            "pipeline": pipeline_results
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
