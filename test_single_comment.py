"""
Script de prueba para el endpoint /api/scraping/classify-single

Este script prueba el nuevo endpoint que clasifica comentarios individuales
y genera requisitos No Funcionales si son relevantes.
"""

import requests
import json

BASE_URL = "http://localhost:8000"
ENDPOINT = f"{BASE_URL}/api/scraping/classify-single"


def test_comment(comentario: str, calificacion: int = 1):
    """Prueba el endpoint con un comentario específico"""
    print(f"\n{'='*80}")
    print(f"PROBANDO COMENTARIO (Rating: {calificacion}★)")
    print(f"{'='*80}")
    print(f"Texto: \"{comentario}\"")
    print(f"{'='*80}\n")

    payload = {
        "comentario": comentario,
        "calificacion": calificacion
    }

    try:
        response = requests.post(ENDPOINT, json=payload, timeout=60)

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            print(f"\n{'='*80}")
            print("RESULTADO:")
            print(f"{'='*80}")
            print(f"✅ Success: {data['success']}")
            print(f"🔍 Es Relevante: {data['es_relevante']}")
            print(f"💬 Mensaje: {data['mensaje']}")

            if data['es_relevante']:
                print(f"\n📊 CLASIFICACIÓN:")
                print(f"   Categoría: {data['categoria']}")
                print(f"   Confianza: {data['confianza']:.2%}")

                if data.get('requisito'):
                    requisito = data['requisito']
                    print(f"\n📝 REQUISITO GENERADO:")
                    print(f"   ID: {requisito['id']}")
                    print(f"   Prioridad: {requisito['prioridad']}")
                    print(f"   Requisito: {requisito['requisito']}")
                    print(f"   Justificación: {requisito['justificacion']}")
                    print(f"\n   Criterios de Aceptación:")
                    for i, criterio in enumerate(requisito['criterios_aceptacion'], 1):
                        print(f"      {i}. {criterio}")
                else:
                    print(f"\n⚠️  No se generó requisito")
                    if data.get('error'):
                        print(f"   Error: {data['error']}")

            print(f"{'='*80}\n")

            # Guardar respuesta completa
            filename = f"test_single_response_{data['es_relevante']}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✅ Respuesta completa guardada en: {filename}\n")

        else:
            print(f"\n❌ Error: {response.status_code}")
            print(response.text)

    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: No se pudo conectar al servidor.")
        print("Asegúrate de que el servidor esté ejecutándose con: python main.py")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("PRUEBA DE ENDPOINT: /api/scraping/classify-single")
    print("="*80)

    # Comentarios de prueba
    print("\n🧪 Ejecutando pruebas...\n")

    # Test 1: Comentario RELEVANTE sobre autenticación
    test_comment(
        comentario="No puedo iniciar sesión con mi huella digital, siempre me pide la contraseña y es muy frustrante",
        calificacion=2
    )

    # Test 2: Comentario RELEVANTE sobre privacidad
    test_comment(
        comentario="La aplicación solicita demasiados permisos que no son necesarios para su funcionamiento, me preocupa mi privacidad",
        calificacion=1
    )

    # Test 3: Comentario RELEVANTE sobre disponibilidad
    test_comment(
        comentario="La app se cae constantemente cuando intento hacer una transferencia, pierdo tiempo y es muy insegura",
        calificacion=1
    )

    # Test 4: Comentario NO RELEVANTE (general)
    test_comment(
        comentario="Me gusta mucho la interfaz, es muy bonita y fácil de usar",
        calificacion=5
    )

    # Test 5: Comentario NO RELEVANTE (problema de UI)
    test_comment(
        comentario="El botón de enviar está muy pequeño y no puedo hacer click fácilmente",
        calificacion=3
    )

    print("\n" + "="*80)
    print("✅ PRUEBAS COMPLETADAS")
    print("="*80)
    print("\nRevisa los archivos generados:")
    print("  - test_single_response_True.json  (comentarios relevantes)")
    print("  - test_single_response_False.json (comentarios no relevantes)")
    print("="*80 + "\n")
