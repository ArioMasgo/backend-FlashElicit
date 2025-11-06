"""
Redis client configuration and management for caching.
"""
import os
import redis
from typing import Optional
import json
import hashlib
from dotenv import load_dotenv

load_dotenv()


class RedisClient:
    """
    Singleton Redis client manager for caching operations.
    """
    _instance: Optional['RedisClient'] = None
    _client: Optional[redis.Redis] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            self._connect()

    def _connect(self):
        """Connect to Redis using URL from environment variables."""
        redis_url = os.getenv('REDIS_URL')

        if not redis_url:
            print("WARNING: REDIS_URL not configured. Caching disabled.")
            self._client = None
            return

        try:
            # Crear cliente Redis con configuración optimizada
            self._client = redis.from_url(
                redis_url,
                decode_responses=True,  # Decodificar respuestas automáticamente
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )

            # Verificar conexión
            self._client.ping()
            print("[OK] Redis connected successfully")

        except Exception as e:
            print(f"[ERROR] Error connecting to Redis: {str(e)}")
            print("WARNING: Caching disabled. Application will continue without cache.")
            self._client = None

    def is_available(self) -> bool:
        """Check if Redis is available."""
        if self._client is None:
            return False

        try:
            self._client.ping()
            return True
        except:
            return False

    def generate_cache_key(self, prefix: str, data: dict) -> str:
        """
        Generate a deterministic cache key from data.

        Args:
            prefix: Cache key prefix (e.g., 'scrape', 'classify')
            data: Dictionary with request data

        Returns:
            Cache key string
        """
        # Convertir dict a JSON ordenado para consistencia
        json_str = json.dumps(data, sort_keys=True)
        # Generar hash SHA256
        hash_obj = hashlib.sha256(json_str.encode())
        hash_hex = hash_obj.hexdigest()[:16]  # Primeros 16 caracteres

        return f"{prefix}:{hash_hex}"

    def get_cached(self, key: str) -> Optional[dict]:
        """
        Get cached data by key.

        Args:
            key: Cache key

        Returns:
            Cached data as dict or None if not found
        """
        if not self.is_available():
            return None

        try:
            cached = self._client.get(key)
            if cached:
                print(f"[CACHE HIT] {key}")
                return json.loads(cached)
            print(f"[CACHE MISS] {key}")
            return None
        except Exception as e:
            print(f"[WARNING] Error reading from cache: {str(e)}")
            return None

    def set_cached(self, key: str, data: dict, ttl: int = 3600) -> bool:
        """
        Store data in cache with TTL.

        Args:
            key: Cache key
            data: Data to cache
            ttl: Time to live in seconds (default: 1 hour)

        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            return False

        try:
            json_data = json.dumps(data)
            self._client.setex(key, ttl, json_data)
            print(f"[CACHED] {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            print(f"[WARNING] Error writing to cache: {str(e)}")
            return False

    def delete_cached(self, key: str) -> bool:
        """
        Delete cached data by key.

        Args:
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            return False

        try:
            self._client.delete(key)
            print(f"[DELETED] {key}")
            return True
        except Exception as e:
            print(f"[WARNING] Error deleting from cache: {str(e)}")
            return False

    def clear_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a pattern.

        Args:
            pattern: Redis pattern (e.g., 'scrape:*')

        Returns:
            Number of keys deleted
        """
        if not self.is_available():
            return 0

        try:
            keys = self._client.keys(pattern)
            if keys:
                deleted = self._client.delete(*keys)
                print(f"[DELETED] {deleted} keys matching pattern: {pattern}")
                return deleted
            return 0
        except Exception as e:
            print(f"[WARNING] Error clearing cache pattern: {str(e)}")
            return 0

    def get_stats(self) -> dict:
        """
        Get Redis cache statistics.

        Returns:
            Dictionary with cache stats
        """
        if not self.is_available():
            return {
                "available": False,
                "message": "Redis not available"
            }

        try:
            info = self._client.info('stats')
            return {
                "available": True,
                "total_connections_received": info.get('total_connections_received', 0),
                "total_commands_processed": info.get('total_commands_processed', 0),
                "keyspace_hits": info.get('keyspace_hits', 0),
                "keyspace_misses": info.get('keyspace_misses', 0),
                "hit_rate": round(
                    info.get('keyspace_hits', 0) /
                    max(info.get('keyspace_hits', 0) + info.get('keyspace_misses', 0), 1) * 100,
                    2
                )
            }
        except Exception as e:
            return {
                "available": False,
                "error": str(e)
            }


# Singleton instance
_redis_client = None

def get_redis_client() -> RedisClient:
    """Get or create Redis client singleton instance."""
    global _redis_client
    if _redis_client is None:
        _redis_client = RedisClient()
    return _redis_client
