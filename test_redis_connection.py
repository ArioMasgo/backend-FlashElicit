"""
Script para probar la conexión a Redis y las funcionalidades de caché.
"""
from app.core.redis_client import get_redis_client
import json


def test_redis_connection():
    """Prueba la conexión a Redis."""
    print("="*60)
    print("PRUEBA DE CONEXIÓN A REDIS")
    print("="*60)

    redis_client = get_redis_client()

    # 1. Verificar disponibilidad
    if redis_client.is_available():
        print("[OK] Redis esta disponible y conectado")
    else:
        print("[ERROR] Redis NO esta disponible")
        return False

    # 2. Generar cache key de prueba
    test_data = {
        "app_id": "com.test.app",
        "max_reviews": 100,
        "max_rating": 3
    }
    cache_key = redis_client.generate_cache_key("test", test_data)
    print(f"\n[KEY] Cache key generado: {cache_key}")

    # 3. Probar escritura
    test_value = {
        "message": "Hello Redis!",
        "timestamp": "2024-11-06",
        "data": [1, 2, 3, 4, 5]
    }
    print(f"\n[WRITE] Guardando en cache...")
    success = redis_client.set_cached(cache_key, test_value, ttl=60)
    if success:
        print("[OK] Datos guardados exitosamente")
    else:
        print("[ERROR] Error al guardar datos")
        return False

    # 4. Probar lectura
    print(f"\n[READ] Leyendo desde cache...")
    cached_data = redis_client.get_cached(cache_key)
    if cached_data:
        print("[OK] Datos recuperados exitosamente:")
        print(f"   {json.dumps(cached_data, indent=2)}")
    else:
        print("[ERROR] Error al recuperar datos")
        return False

    # 5. Verificar consistencia
    if cached_data == test_value:
        print("\n[OK] Los datos son consistentes")
    else:
        print("\n[ERROR] Los datos NO coinciden")
        return False

    # 6. Obtener estadísticas
    print(f"\n{'='*60}")
    print("ESTADÍSTICAS DE REDIS")
    print("="*60)
    stats = redis_client.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    # 7. Limpiar datos de prueba
    print(f"\n[CLEANUP] Limpiando datos de prueba...")
    redis_client.delete_cached(cache_key)

    print(f"\n{'='*60}")
    print("[SUCCESS] TODAS LAS PRUEBAS PASARON")
    print("="*60)

    return True


def test_cache_key_generation():
    """Prueba la generación de cache keys."""
    print(f"\n{'='*60}")
    print("PRUEBA DE GENERACIÓN DE CACHE KEYS")
    print("="*60)

    redis_client = get_redis_client()

    # Datos iguales deben generar la misma key
    data1 = {"app_id": "com.test", "max_reviews": 100}
    data2 = {"max_reviews": 100, "app_id": "com.test"}  # Orden diferente

    key1 = redis_client.generate_cache_key("scrape", data1)
    key2 = redis_client.generate_cache_key("scrape", data2)

    print(f"Key 1: {key1}")
    print(f"Key 2: {key2}")

    if key1 == key2:
        print("[OK] Las keys son identicas (orden no importa)")
    else:
        print("[ERROR] Las keys son diferentes")

    # Datos diferentes deben generar keys diferentes
    data3 = {"app_id": "com.test", "max_reviews": 200}
    key3 = redis_client.generate_cache_key("scrape", data3)

    print(f"Key 3: {key3}")

    if key1 != key3:
        print("[OK] Keys diferentes para datos diferentes")
    else:
        print("[ERROR] Keys iguales para datos diferentes")


if __name__ == "__main__":
    try:
        # Probar conexión básica
        if test_redis_connection():
            # Probar generación de cache keys
            test_cache_key_generation()
        else:
            print("\n[ERROR] Error en las pruebas de conexion")
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
