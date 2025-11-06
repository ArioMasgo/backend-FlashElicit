# Flash Elicit API

API para extracción, clasificación de comentarios y generación de requisitos No Funcionales basados en ISO 25010.

## Descripción

**Flash Elicit** es una herramienta de elicitación de requisitos que analiza comentarios de usuarios de aplicaciones móviles (Google Play Store) para generar requisitos No Funcionales basados en las categorías de seguridad de ISO 25010.

## Características Principales

- 🔍 **Scraping automatizado** de comentarios negativos de Google Play Store
- 🤖 **Filtrado inteligente** con modelos BERT (binario + multiclase)
- 🏷️ **Clasificación ISO 25010** en 6 categorías de seguridad
- 🧠 **Generación automática de requisitos** usando Mistral (OpenRouter)
- ⚡ **Procesamiento individual** de comentarios con detección de relevancia
- 📄 **Exportación a PDF** con formato profesional y personalizable

## Endpoints Disponibles

### 1. Scraping y Clasificación Masiva

```
POST /api/scraping/scrape
```

Extrae comentarios de Play Store, los clasifica y genera requisitos.

**Documentación**: Ver [README_REQUISITOS.md](README_REQUISITOS.md)

**Ejemplo**:
```bash
curl -X POST http://localhost:8000/api/scraping/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "playstore_url": "https://play.google.com/store/apps/details?id=com.example.app",
    "max_reviews": 1000,
    "max_rating": 3,
    "criterios_busqueda": "recientes"
  }'
```

**Campos del Request:**
- `playstore_url` (✅ requerido): URL de la app en Google Play Store
- `max_reviews` (opcional, default: 9000): Número máximo de comentarios a extraer
- `max_rating` (opcional, default: 3): Calificación máxima (≤ este valor)
- `criterios_busqueda` (✅ requerido): `"recientes"` (más nuevos) o `"relevantes"` (más útiles)

### 2. Clasificación de Comentario Individual

```
POST /api/scraping/classify-single
```

Clasifica un solo comentario y genera un requisito si es relevante.

**Documentación**: Ver [README_SINGLE_COMMENT.md](README_SINGLE_COMMENT.md)

**Ejemplo**:
```bash
curl -X POST http://localhost:8000/api/scraping/classify-single \
  -H "Content-Type: application/json" \
  -d '{
    "comentario": "No puedo iniciar sesión con mi huella digital",
    "calificacion": 2
  }'
```

### 3. Generación de PDF de Requisitos

```
POST /api/scraping/generate-pdf
```

Genera un documento PDF profesional con los requisitos No Funcionales.

**Documentación**: Ver [README_PDF.md](README_PDF.md)

**Ejemplo**:
```bash
curl -X POST http://localhost:8000/api/scraping/generate-pdf \
  -H "Content-Type: application/json" \
  -d @requisitos_data.json \
  --output requisitos.pdf
```

### 4. Health Check

```
GET /api/health
```

Verifica el estado de la API.

**Ejemplo**:
```bash
curl http://localhost:8000/api/health
```

## Instalación y Configuración

### Requisitos

- Python 3.8+
- GPU (opcional, para aceleración)
- Cuenta en [OpenRouter](https://openrouter.ai/)

### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd backend
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar .env y agregar tu API key de OpenRouter
# OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx
```

Para obtener una API key:
1. Ve a [OpenRouter](https://openrouter.ai/)
2. Crea una cuenta
3. Ve a [API Keys](https://openrouter.ai/keys)
4. Genera una nueva key

### 4. Ejecutar el servidor

```bash
python main.py
```

El servidor estará disponible en: http://localhost:8000

## Arquitectura

```
📦 backend/
├── 📂 app/
│   ├── 📂 api/routes/
│   │   ├── health.py                  # Health check endpoint
│   │   └── scraping.py                # Endpoints principales
│   ├── 📂 services/
│   │   ├── scraping_service.py        # Servicio de scraping
│   │   ├── bert_classifier_service.py # Clasificación BERT
│   │   └── openrouter_service.py      # Generación de requisitos
│   ├── 📂 schemas/
│   │   └── scraping_schemas.py        # Schemas Pydantic
│   └── 📂 models/
│       ├── modelo_bert_binario/       # Modelo filtro relevancia
│       └── modelo_bert_multiclase/    # Modelo clasificación ISO
├── 📄 main.py                         # Entry point
├── 📄 requirements.txt                # Dependencias
├── 📄 .env.example                    # Plantilla de configuración
└── 📄 test_*.py                       # Scripts de prueba
```

## Pipeline de Procesamiento

### Endpoint de Scraping (`/scrape`)

```
1. Scraping → Google Play Store
   ↓
2. Filtro Binario → Relevante vs No Relevante
   ↓
3. Clasificación Multiclase → Categorías ISO 25010
   ↓
4. Generación de Requisitos → Mistral (OpenRouter)
   ↓
5. Response → Comentarios + Requisitos
```

### Endpoint Individual (`/classify-single`)

```
1. Recibe Comentario
   ↓
2. Filtro Binario → ¿Es relevante?
   ↓
   ├─ NO → Mensaje "no relevante"
   │
   └─ SÍ → Clasificación Multiclase
      ↓
      Generación de Requisito
      ↓
      Response → Comentario + Requisito
```

## Categorías ISO 25010

| Categoría | Descripción | Ejemplo |
|-----------|-------------|---------|
| `autenticidad` | Verificación de identidad | "No funciona la huella digital" |
| `confidencialidad` | Privacidad de datos | "Solicita permisos innecesarios" |
| `integridad` | Protección contra corrupción | "Se pierden los datos guardados" |
| `no_repudio` | Trazabilidad de acciones | "No puedo ver el historial de movimientos" |
| `resistencia` | Disponibilidad del sistema | "La app se cae constantemente" |
| `responsabilidad` | Auditoría y accountability | "No hay registro de quién modificó mis datos" |

## Modelos Utilizados

### BERT (Local)

- **Modelo base**: `dccuchile/bert-base-spanish-wwm-uncased`
- **Binario**: Clasificación relevante/no relevante (78.5% precisión)
- **Multiclase**: Clasificación en 6 categorías ISO 25010 (74.1% F1-Score)
- **Idioma**: Español
- **Hardware**: CPU/GPU automático

### Mistral (OpenRouter)

- **Modelo**: `mistralai/mistral-small-3.2-24b-instruct:free`
- **Proveedor**: OpenRouter
- **Costo**: Gratuito
- **Uso**: Generación de requisitos No Funcionales

## Testing

### Scripts de Prueba

```bash
# Probar endpoint de scraping
python test_api.py

# Probar endpoint de comentario individual
python test_single_comment.py

# Probar modelos BERT directamente
python test_models.py
```

### Ejemplos de Prueba

**Comentario Relevante**:
```json
{
  "comentario": "No puedo iniciar sesión con mi huella digital",
  "calificacion": 2
}
```

**Comentario No Relevante**:
```json
{
  "comentario": "Me gusta la interfaz de la app",
  "calificacion": 5
}
```

## Documentación de la API

FastAPI genera documentación interactiva automática:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Estructura de Respuesta

### Scraping Response

```json
{
  "success": true,
  "app_id": "com.example.app",
  "total_reviews": 450,
  "reviews": [...],
  "stats": {...},
  "requirements": {
    "requisitos": [
      {
        "id": "NFR-001",
        "categoria": "autenticidad",
        "requisito": "El sistema debe...",
        "prioridad": "Alta",
        "justificacion": "...",
        "criterios_aceptacion": [...]
      }
    ],
    "resumen": {...}
  }
}
```

### Single Comment Response (Relevante)

```json
{
  "success": true,
  "es_relevante": true,
  "mensaje": "Comentario clasificado como relevante...",
  "comentario": "...",
  "calificacion": 2,
  "categoria": "autenticidad",
  "confianza": 0.9523,
  "requisito": {
    "id": "NFR-001",
    "categoria": "autenticidad",
    "requisito": "El sistema debe...",
    "prioridad": "Alta",
    "justificacion": "...",
    "criterios_aceptacion": [...]
  }
}
```

### Single Comment Response (No Relevante)

```json
{
  "success": true,
  "es_relevante": false,
  "mensaje": "El comentario no fue clasificado como relevante...",
  "comentario": "...",
  "calificacion": 5,
  "categoria": null,
  "confianza": null,
  "requisito": null
}
```

## Performance

| Métrica | Valor |
|---------|-------|
| Scraping (1000 reviews) | ~30-60 segundos |
| Clasificación binaria | ~0.1s por comentario |
| Clasificación multiclase | ~0.2s por comentario |
| Generación de requisito | ~2-5 segundos |
| Endpoint individual | ~2-10 segundos total |

## Manejo de Errores

### Graceful Degradation

- Si falla el scraping → Error 500
- Si falla la clasificación → Error 500
- Si falla la generación de requisitos → Continúa sin requisitos
- Si el comentario no es relevante → Mensaje específico (no es error)

### Logs Detallados

El servidor muestra logs en consola con el progreso:

```
============================================================
🚀 INICIANDO PROCESO DE SCRAPING Y CLASIFICACIÓN
============================================================

✅ Scraping completado: 1200 comentarios extraídos

============================================================
🤖 INICIANDO CLASIFICACIÓN CON MODELOS BERT
============================================================

✅ CLASIFICACIÓN COMPLETADA
Total scrapeado: 1200
Total relevante: 450
Tasa de relevancia: 37.5%

============================================================
🧠 GENERANDO REQUISITOS NO FUNCIONALES CON MISTRAL
============================================================

✅ Requisitos generados exitosamente
Total: 8 requisitos

============================================================
✅ PROCESO COMPLETO FINALIZADO
============================================================
```

## Casos de Uso

### 1. Análisis de Competencia

Analiza aplicaciones competidoras para identificar problemas de seguridad:

```python
competitors = ["com.competitor1.app", "com.competitor2.app"]

for app_id in competitors:
    results = scrape_and_classify(app_id)
    analyze_requirements(results)
```

### 2. Monitoreo Continuo

Monitorea tu propia aplicación periódicamente:

```python
# Ejecutar diariamente
schedule.every().day.at("00:00").do(
    lambda: scrape_and_classify("com.myapp.id")
)
```

### 3. Validación de Feedback

Valida feedback de usuarios en tiempo real:

```javascript
async function submitFeedback(comment) {
  const result = await classifySingleComment(comment);
  if (result.es_relevante) {
    alertSecurityTeam(result.requisito);
  }
}
```

## Limitaciones

- Solo soporta Google Play Store (no App Store)
- Scraping limitado por rate limits de Google
- Modelos BERT entrenados solo en español
- Clasificación limitada a 6 categorías de seguridad ISO 25010
- Generación de requisitos depende de disponibilidad de OpenRouter

## Mejoras Futuras

- [ ] Soporte para App Store (iOS)
- [ ] Modelos multilingües (inglés, portugués, etc.)
- [ ] Más categorías ISO 25010 (usabilidad, performance, etc.)
- [ ] Batch processing para múltiples comentarios
- [ ] Cache de requisitos generados
- [ ] Exportación a PDF/DOCX
- [ ] Integración con Jira/Azure DevOps
- [ ] Dashboard web para visualización
- [ ] API de refinamiento de requisitos

## Documentación Adicional

- [README_CLASIFICACION.md](README_CLASIFICACION.md) - Detalles de modelos BERT
- [README_REQUISITOS.md](README_REQUISITOS.md) - Endpoint de scraping masivo
- [README_SINGLE_COMMENT.md](README_SINGLE_COMMENT.md) - Endpoint de comentario individual
- [README_PDF.md](README_PDF.md) - Generación de PDF de requisitos

## Licencia

[Tu licencia aquí]

## Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el repositorio
2. Crea una rama para tu feature
3. Haz commit de tus cambios
4. Abre un Pull Request

## Soporte

Para reportar problemas o sugerencias:
- Abre un issue en el repositorio
- Contacta al equipo de desarrollo

## Créditos

- Modelos BERT: [dccuchile/bert-base-spanish-wwm-uncased](https://huggingface.co/dccuchile/bert-base-spanish-wwm-uncased)
- LLM: [Mistral AI](https://mistral.ai/) via [OpenRouter](https://openrouter.ai/)
- Framework: [FastAPI](https://fastapi.tiangolo.com/)
- Scraping: [google-play-scraper](https://github.com/JoMingyu/google-play-scraper)
