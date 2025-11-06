"""
Script de prueba para el endpoint de scraping con clasificación BERT
"""
import requests
import json

# Configuración
API_URL = "http://localhost:8000/api/scraping/scrape"

# Ejemplo de request payload
payload = {
    "playstore_url": "https://play.google.com/store/apps/details?id=com.bcp.bank.bcp",
    "max_reviews": 100,  # Empezar con pocos comentarios para prueba
    "max_rating": 3,
    "criterios_busqueda": "recientes"  # Opciones: "recientes" o "relevantes"
}

def test_scraping_endpoint():
    """Prueba el endpoint de scraping con clasificación"""
    print("="*80)
    print("🧪 PRUEBA DEL ENDPOINT DE SCRAPING CON CLASIFICACIÓN BERT")
    print("="*80)
    print(f"\n📋 Payload de prueba:")
    print(json.dumps(payload, indent=2))
    print(f"\n🌐 Enviando request a: {API_URL}")
    print("-"*80)

    try:
        # Realizar la petición
        response = requests.post(API_URL, json=payload, timeout=300)  # 5 min timeout

        # Verificar respuesta
        if response.status_code == 200:
            data = response.json()

            print("\n✅ RESPUESTA EXITOSA")
            print("="*80)
            print(f"\n📊 ESTADÍSTICAS GENERALES:")
            print(f"  App ID: {data['app_id']}")
            print(f"  Total de reviews clasificadas: {data['total_reviews']}")
            print(f"  Success: {data['success']}")

            print(f"\n📈 ESTADÍSTICAS DEL PROCESO:")
            stats = data['stats']
            for key, value in stats.items():
                if key == 'distribucion_categorias':
                    print(f"  {key}:")
                    for cat, count in value.items():
                        print(f"    - {cat}: {count}")
                else:
                    print(f"  {key}: {value}")

            print(f"\n💬 PRIMEROS 5 COMENTARIOS CLASIFICADOS:")
            print("-"*80)
            for i, review in enumerate(data['reviews'][:5], 1):
                print(f"\n{i}. {review['categoria'].upper()} (confianza: {review['confianza']:.2%})")
                print(f"   ⭐ {review['calificacion']} - {review['fecha']}")
                print(f"   👤 {review['usuario']}")
                print(f"   💬 {review['comentario'][:150]}{'...' if len(review['comentario']) > 150 else ''}")

            print("\n" + "="*80)
            print("✅ PRUEBA COMPLETADA EXITOSAMENTE")
            print("="*80)

            # Guardar respuesta completa para análisis
            with open('test_response.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print("\n💾 Respuesta completa guardada en: test_response.json")

        else:
            print(f"\n❌ ERROR: Status code {response.status_code}")
            print(f"Response: {response.text}")

    except requests.exceptions.Timeout:
        print("\n⏱️ ERROR: La petición tardó demasiado (timeout)")
    except requests.exceptions.ConnectionError:
        print("\n🔌 ERROR: No se pudo conectar al servidor")
        print("   Asegúrate de que el servidor esté corriendo con: python main.py")
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {str(e)}")

if __name__ == "__main__":
    test_scraping_endpoint()
