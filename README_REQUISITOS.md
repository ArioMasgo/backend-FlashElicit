# Generación de Requisitos No Funcionales

## Descripción

Esta extensión del endpoint de scraping integra el modelo **Mistral Small** de OpenRouter para generar requisitos No Funcionales (NFR) basados en los comentarios clasificados de usuarios.

## Flujo del Proceso

```
1. Scraping de comentarios negativos (Google Play Store)
   ↓
2. Filtro binario (BERT) → Comentarios relevantes
   ↓
3. Clasificación multiclase (BERT) → Categorías ISO 25010
   ↓
4. Generación de requisitos (Mistral) → Requisitos No Funcionales
   ↓
5. Respuesta con comentarios + requisitos
```

## Configuración

### 1. Obtener API Key de OpenRouter

1. Ve a [OpenRouter](https://openrouter.ai/)
2. Crea una cuenta o inicia sesión
3. Ve a [API Keys](https://openrouter.ai/keys)
4. Genera una nueva API key

### 2. Configurar variables de entorno

Copia el archivo `.env.example` a `.env`:

```bash
cp .env.example .env
```

Edita el archivo `.env` y agrega tu API key:

```bash
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

Nuevas dependencias agregadas:
- `openai>=1.0.0` - Cliente para OpenRouter
- `python-dotenv>=1.0.0` - Manejo de variables de entorno

### 4. Ejecutar el servidor

```bash
python main.py
```

## Uso del Endpoint

### Request

```bash
POST http://localhost:8000/api/scraping/scrape
Content-Type: application/json

{
  "playstore_url": "https://play.google.com/store/apps/details?id=com.example.app",
  "max_reviews": 9000,
  "max_rating": 3,
  "criterios_busqueda": "recientes"
}
```

**Campos del Request:**

| Campo | Tipo | Requerido | Descripción | Valores |
|-------|------|-----------|-------------|---------|
| `playstore_url` | string | ✅ Sí | URL de la app en Google Play Store | Debe comenzar con `https://play.google.com/store/apps/details?id=` |
| `max_reviews` | integer | No (default: 9000) | Número máximo de comentarios a extraer | Entero positivo |
| `max_rating` | integer | No (default: 3) | Calificación máxima a filtrar (≤ este valor) | 1-5 estrellas |
| `criterios_busqueda` | string | ✅ Sí | Criterio de ordenamiento de comentarios | `"recientes"` o `"relevantes"` |

**Criterios de Búsqueda:**
- `"recientes"`: Obtiene los comentarios más nuevos primero (ordenados por fecha)
- `"relevantes"`: Obtiene los comentarios más útiles según Google Play (ordenados por relevancia/utilidad)

### Response

La respuesta ahora incluye un campo adicional `requirements` con los requisitos generados:

```json
{
  "success": true,
  "app_id": "com.example.app",
  "total_reviews": 450,
  "reviews": [
    {
      "id_original": "gp:AOqpTOH...",
      "comentario": "No puedo iniciar sesión con mi huella digital",
      "calificacion": 2,
      "fecha": "2025-01-15",
      "usuario": "Juan Pérez",
      "categoria": "autenticidad",
      "confianza": 0.8523
    }
  ],
  "stats": {
    "total_comentarios_revisados": 1500,
    "comentarios_relevantes": 450,
    "distribucion_categorias": {
      "autenticidad": 180,
      "confidencialidad": 120
    }
  },
  "requirements": {
    "requisitos": [
      {
        "id": "NFR-001",
        "categoria": "autenticidad",
        "requisito": "El sistema debe implementar autenticación biométrica con tasa de error menor al 1%",
        "prioridad": "Alta",
        "justificacion": "Múltiples usuarios reportan problemas con el inicio de sesión por huella digital",
        "criterios_aceptacion": [
          "Soporte para huella digital y reconocimiento facial",
          "Tiempo de respuesta menor a 2 segundos",
          "Fallback a contraseña en caso de fallo biométrico"
        ],
        "comentarios_relacionados": 5
      },
      {
        "id": "NFR-002",
        "categoria": "confidencialidad",
        "requisito": "El sistema debe cifrar todos los datos sensibles usando AES-256",
        "prioridad": "Alta",
        "justificacion": "Usuarios preocupados por la seguridad de sus datos personales",
        "criterios_aceptacion": [
          "Cifrado end-to-end para datos bancarios",
          "Certificación de cumplimiento con GDPR",
          "Auditoría de seguridad trimestral"
        ],
        "comentarios_relacionados": 8
      }
    ],
    "resumen": {
      "total_requisitos": 8,
      "por_categoria": {
        "autenticidad": 2,
        "confidencialidad": 3,
        "integridad": 1,
        "resistencia": 2
      },
      "prioridad_alta": 5,
      "prioridad_media": 2,
      "prioridad_baja": 1
    }
  }
}
```

## Estructura de los Requisitos

### RequirementData

Cada requisito contiene:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | string | Identificador único (ej: NFR-001) |
| `categoria` | string | Categoría ISO 25010 |
| `requisito` | string | Descripción del requisito |
| `prioridad` | string | Alta / Media / Baja |
| `justificacion` | string | Razón basada en comentarios |
| `criterios_aceptacion` | array | Lista de criterios de aceptación |
| `comentarios_relacionados` | int | Cantidad de comentarios que lo motivaron |

### Categorías ISO 25010

- **autenticidad**: Verificación de identidad y autenticación
- **confidencialidad**: Privacidad y protección de datos
- **integridad**: Prevención de corrupción de datos
- **no_repudio**: Trazabilidad y responsabilidad
- **resistencia**: Disponibilidad y robustez del sistema
- **responsabilidad**: Auditoría y rendición de cuentas

## Modelo Utilizado

- **Proveedor**: OpenRouter
- **Modelo**: `mistralai/mistral-small-3.2-24b-instruct:free`
- **Contexto**: 4000 tokens de salida máxima
- **Temperature**: 0.7 (balance entre creatividad y consistencia)

## Manejo de Errores

Si la generación de requisitos falla:

1. El endpoint **NO fallará completamente**
2. Se retornarán los comentarios clasificados normalmente
3. El campo `requirements` será `null`
4. Se mostrará un warning en los logs del servidor

Ejemplo de respuesta con error en requisitos:

```json
{
  "success": true,
  "app_id": "com.example.app",
  "total_reviews": 450,
  "reviews": [...],
  "stats": {...},
  "requirements": {
    "requisitos": [],
    "resumen": {
      "total_requisitos": 0,
      "por_categoria": {},
      "prioridad_alta": 0,
      "prioridad_media": 0,
      "prioridad_baja": 0
    },
    "error": "No se pudo parsear la respuesta del modelo",
    "raw_response": "..."
  }
}
```

## Optimizaciones

### Prompt Engineering

El prompt incluye:
- Contexto de ISO 25010
- Comentarios agrupados por categoría
- Límite de 5 comentarios por categoría (para controlar tokens)
- Instrucciones específicas de formato JSON
- Criterios de calidad para requisitos (específicos, medibles, accionables)

### Performance

- **Singleton Pattern**: El cliente OpenRouter se inicializa una sola vez
- **Reintentos**: 3 intentos automáticos en caso de error
- **Parseo robusto**: Maneja respuestas con o sin bloques de código markdown
- **Graceful degradation**: Si falla, el endpoint continúa sin requisitos

## Testing

Puedes probar el endpoint con curl:

```bash
curl -X POST http://localhost:8000/api/scraping/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "playstore_url": "https://play.google.com/store/apps/details?id=com.bcp.bank.bcp",
    "max_reviews": 100,
    "max_rating": 3
  }'
```

O usar el script de prueba incluido:

```bash
python test_api.py
```

## Costos

El modelo usado es **gratuito** (`mistral-small-3.2-24b-instruct:free`).

Para modelos de pago, verifica los costos en [OpenRouter Pricing](https://openrouter.ai/docs#models).

## Logs del Proceso

El servidor muestra logs detallados:

```
============================================================
🚀 INICIANDO PROCESO DE SCRAPING Y CLASIFICACIÓN
============================================================

✅ Scraping completado: 1200 comentarios extraídos

============================================================
🤖 INICIANDO CLASIFICACIÓN CON MODELOS BERT
============================================================

============================================================
✅ CLASIFICACIÓN COMPLETADA
============================================================
Total scrapeado: 1200
Total relevante: 450
Tasa de relevancia: 37.5%
============================================================

============================================================
🧠 GENERANDO REQUISITOS NO FUNCIONALES CON MISTRAL
============================================================
Total de comentarios a procesar: 450

Intento 1/3...

✅ Respuesta recibida del modelo (3421 caracteres)
✅ Requisitos generados exitosamente
   Total: 8 requisitos

============================================================
✅ PROCESO COMPLETO FINALIZADO
============================================================
```

## Arquitectura de Archivos

```
backend/
├── app/
│   ├── api/routes/
│   │   └── scraping.py           # Endpoint principal (modificado)
│   ├── services/
│   │   ├── scraping_service.py   # Servicio de scraping
│   │   ├── bert_classifier_service.py  # Clasificación BERT
│   │   └── openrouter_service.py # Generación de requisitos (NUEVO)
│   └── schemas/
│       └── scraping_schemas.py   # Schemas Pydantic (ampliados)
├── main.py                       # Entry point (modificado)
├── requirements.txt              # Dependencias (actualizadas)
├── .env.example                  # Ejemplo de configuración (NUEVO)
├── .env                          # Tu configuración (crear)
└── README_REQUISITOS.md          # Esta documentación (NUEVO)
```

## Próximos Pasos

Posibles mejoras:

1. **Cache de requisitos**: Guardar requisitos generados en base de datos
2. **Modelos alternativos**: Permitir elegir diferentes modelos LLM
3. **Refinamiento iterativo**: Permitir regenerar requisitos con feedback
4. **Exportación**: Generar documentos PDF/DOCX con requisitos
5. **Validación**: Validar requisitos contra estándares IEEE/ISO
6. **Trazabilidad**: Vincular requisitos con comentarios específicos

## Soporte

Para reportar problemas o sugerencias, crea un issue en el repositorio.
