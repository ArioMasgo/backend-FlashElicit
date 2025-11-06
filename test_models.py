"""
Script de prueba para verificar la carga y funcionamiento de los modelos BERT
"""
from app.services.bert_classifier_service import BERTClassifier

def test_models():
    """Prueba la carga y clasificación de los modelos"""
    print("="*80)
    print("🧪 PRUEBA DE MODELOS BERT")
    print("="*80)

    try:
        # Cargar clasificador
        print("\n📦 Cargando modelos...")
        classifier = BERTClassifier()

        # Comentarios de prueba
        test_comments = [
            "No puedo iniciar sesión, siempre me sale error de autenticación",
            "La app crashea constantemente",
            "Excelente aplicación, muy rápida",
            "Mis datos no se sincronizan correctamente con el servidor",
            "Me encanta esta app, la mejor",
        ]

        print(f"\n💬 Comentarios de prueba ({len(test_comments)}):")
        for i, comment in enumerate(test_comments, 1):
            print(f"  {i}. {comment}")

        # Paso 1: Clasificación binaria
        print(f"\n{'='*80}")
        print("📊 PASO 1: CLASIFICACIÓN BINARIA")
        print("="*80)
        binary_results = classifier.classify_binary(test_comments)

        for comment, is_relevant in zip(test_comments, binary_results):
            status = "✅ RELEVANTE" if is_relevant else "❌ NO RELEVANTE"
            print(f"{status}: {comment[:60]}...")

        # Filtrar solo relevantes
        relevant_comments = [
            comment for comment, is_relevant in zip(test_comments, binary_results)
            if is_relevant
        ]

        if relevant_comments:
            # Paso 2: Clasificación multiclase
            print(f"\n{'='*80}")
            print("📊 PASO 2: CLASIFICACIÓN MULTICLASE")
            print("="*80)
            multiclass_results = classifier.classify_multiclass(relevant_comments)

            for comment, (category, confidence) in zip(relevant_comments, multiclass_results):
                print(f"\n📌 {category.upper()} (confianza: {confidence:.2%})")
                print(f"   {comment}")

        # Prueba del método completo
        print(f"\n{'='*80}")
        print("📊 PRUEBA DEL FILTRO EN CASCADA COMPLETO")
        print("="*80)

        test_reviews = [
            {
                'id_original': f'test_{i}',
                'comentario': comment,
                'calificacion': 2,
                'fecha': '2025-01-15',
                'usuario': f'Usuario {i}'
            }
            for i, comment in enumerate(test_comments, 1)
        ]

        classified_reviews = classifier.filter_and_classify(test_reviews)

        print(f"\n📈 RESULTADOS:")
        print(f"  Total de comentarios: {len(test_reviews)}")
        print(f"  Comentarios relevantes: {len(classified_reviews)}")
        print(f"  Tasa de relevancia: {len(classified_reviews)/len(test_reviews)*100:.1f}%")

        print(f"\n💬 COMENTARIOS CLASIFICADOS:")
        for review in classified_reviews:
            print(f"\n  🏷️ {review['categoria'].upper()} ({review['confianza']:.2%})")
            print(f"     {review['comentario']}")

        print("\n" + "="*80)
        print("✅ PRUEBA COMPLETADA EXITOSAMENTE")
        print("="*80)

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_models()
