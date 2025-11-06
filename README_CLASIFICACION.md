# Sistema de Clasificación BERT para Comentarios de Play Store

## Descripción General

Este sistema implementa un **filtrado en cascada** de comentarios de Google Play Store usando dos modelos BERT entrenados:

1. **Modelo Binario**: Filtra comentarios relevantes vs no relevantes
2. **Modelo Multiclase**: Clasifica los comentarios relevantes en 6 categorías ISO 25010

## Flujo del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                    1. SCRAPING DE COMENTARIOS                   │
│               (Google Play Store - Comentarios Negativos)       │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│              2. FILTRO BINARIO (Modelo BERT #1)                 │
│                   Relevante / No Relevante                      │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           │ Solo comentarios RELEVANTES
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│         3. CLASIFICACIÓN MULTICLASE (Modelo BERT #2)            │
│                    Categorías ISO 25010:                        │
│  • Autenticidad      • Integridad      • Resistencia            │
│  • Confidencialidad  • No repudio      • Responsabilidad        │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│              4. RESPUESTA CON COMENTARIOS CLASIFICADOS          │
│         (Solo relevantes + Categoría + Nivel de confianza)      │
└─────────────────────────────────────────────────────────────────┘
```

## Categorías ISO 25010

Los comentarios clasificados como relevantes se asignan a una de estas categorías de seguridad:

- **Autenticidad**: Problemas con verificación de identidad y autenticación
- **Confidencialidad**: Problemas con privacidad y protección de datos
- **Integridad**: Problemas con corrupción o modificación de datos
- **No repudio**: Problemas con trazabilidad y responsabilidad de acciones
- **Resistencia**: Problemas con disponibilidad y robustez del sistema
- **Responsabilidad**: Problemas con rendición de cuentas y auditoría

## Instalación

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

**Dependencias principales**:
- `transformers==4.56.1` - Para los modelos BERT
- `torch>=2.0.0` - Framework de deep learning
- `safetensors>=0.4.0` - Para cargar pesos del modelo
- `fastapi==0.118.0` - Framework web
- `google-play-scraper==1.2.5` - Para scraping de Play Store

### 2. Verificar modelos

Los modelos deben estar en:
```
app/
├── models/
│   ├── modelo_bert_binario/
│   │   ├── config.json
│   │   ├── model.safetensors
│   │   ├── tokenizer.json
│   │   └── ...
│   └── modelo_bert_multiclase/
│       ├── config.json
│       ├── model.safetensors
│       ├── model_metadata.json
│       ├── tokenizer.json
│       └── ...
```

## Uso

### Opción 1: Probar solo los modelos

```bash
python test_models.py
```

Este script carga los modelos y los prueba con comentarios de ejemplo.

**Salida esperada**:
```
🧪 PRUEBA DE MODELOS BERT
📦 Cargando modelos...
✅ Modelo binario cargado exitosamente
✅ Modelo multiclase cargado - Categorías: [...]

📊 PASO 1: CLASIFICACIÓN BINARIA
✅ RELEVANTE: No puedo iniciar sesión, siempre me sale error...
❌ NO RELEVANTE: Excelente aplicación, muy rápida

📊 PASO 2: CLASIFICACIÓN MULTICLASE
📌 AUTENTICIDAD (confianza: 85.23%)
   No puedo iniciar sesión, siempre me sale error de autenticación
```

### Opción 2: Iniciar el servidor API

```bash
python main.py
```

El servidor estará disponible en: `http://localhost:8000`

### Opción 3: Probar el endpoint completo

1. Iniciar el servidor (en una terminal):
```bash
python main.py
```

2. Ejecutar el script de prueba (en otra terminal):
```bash
python test_api.py
```

**O usar curl**:
```bash
curl -X POST "http://localhost:8000/api/scraping/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "playstore_url": "https://play.google.com/store/apps/details?id=com.bcp.bank.bcp",
    "max_reviews": 100,
    "max_rating": 3
  }'
```

## Formato de Request

**POST** `/api/scraping/scrape`

```json
{
  "playstore_url": "https://play.google.com/store/apps/details?id=<APP_ID>",
  "max_reviews": 9000,
  "max_rating": 3
}
```

**Parámetros**:
- `playstore_url` (required): URL completa de la app en Play Store
- `max_reviews` (opcional): Número máximo de comentarios a extraer (default: 9000)
- `max_rating` (opcional): Calificación máxima a filtrar (default: 3)

## Formato de Response

```json
{
  "success": true,
  "app_id": "com.bcp.bank.bcp",
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
    "duplicados_evitados": 23,
    "comentarios_antes_filtro": 1200,
    "comentarios_relevantes": 450,
    "tasa_relevancia": 0.375,
    "distribucion_categorias": {
      "autenticidad": 180,
      "integridad": 120,
      "confidencialidad": 90,
      "resistencia": 40,
      "no_repudio": 15,
      "responsabilidad": 5
    }
  }
}
```

## Arquitectura del Código

```
app/
├── api/
│   └── routes/
│       └── scraping.py          # Endpoint que orquesta todo el proceso
├── services/
│   ├── scraping_service.py      # Lógica de scraping de Play Store
│   └── bert_classifier_service.py  # Servicio de clasificación BERT
├── schemas/
│   └── scraping_schemas.py      # Modelos Pydantic (Request/Response)
└── models/
    ├── modelo_bert_binario/     # Modelo de filtrado binario
    └── modelo_bert_multiclase/  # Modelo de clasificación multiclase
```

## Optimizaciones

### Procesamiento por Lotes
El clasificador procesa los comentarios en lotes (batch_size=32) para optimizar el uso de GPU/CPU.

### Singleton Pattern
Los modelos se cargan una sola vez al iniciar la aplicación usando el patrón Singleton (`get_bert_classifier()`).

### GPU Acceleration
Si hay una GPU disponible, se utiliza automáticamente para acelerar la inferencia:
```python
self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
```

## Estadísticas del Modelo Multiclase

Según `model_metadata.json`:

- **Precisión en test**: 78.5%
- **F1-Score**: 74.1%
- **Total de ejemplos de entrenamiento**: 2,340
- **Idioma**: Español
- **Modelo base**: `dccuchile/bert-base-spanish-wwm-uncased`

## Troubleshooting

### Error: "No module named 'transformers'"
```bash
pip install transformers torch safetensors
```

### Error: "CUDA out of memory"
Reduce el `batch_size` en el endpoint:
```python
classified_reviews = classifier.filter_and_classify(
    reviews=scraping_result['reviews'],
    batch_size=16  # Reducir de 32 a 16
)
```

### Modelos tardan mucho en cargar
Es normal la primera vez. Los modelos se cargan una sola vez y se reutilizan.

### La API no responde
El procesamiento puede tardar varios minutos dependiendo de:
- Número de comentarios
- Velocidad del scraping de Play Store
- Hardware disponible (CPU vs GPU)

## Logs del Sistema

El sistema imprime logs detallados en consola:

```
============================================================
🚀 INICIANDO PROCESO DE SCRAPING Y CLASIFICACIÓN
============================================================

🎯 Extrayendo 100 comentarios negativos recientes (≤ 3⭐)
...

✅ Scraping completado: 100 comentarios extraídos

============================================================
🤖 INICIANDO CLASIFICACIÓN CON MODELOS BERT
============================================================

🔍 Iniciando filtrado en cascada para 100 comentarios

📊 Paso 1: Clasificación binaria (relevante/no relevante)
  Procesados 32/100 comentarios
  Procesados 64/100 comentarios
  Procesados 100/100 comentarios
✅ Comentarios relevantes: 45/100 (45.0%)

📊 Paso 2: Clasificación multiclase (categorías ISO 25010)
  Clasificados 32/45 comentarios
  Clasificados 45/45 comentarios
✅ Clasificación completada

📈 Distribución por categorías:
  autenticidad: 18 (40.0%)
  integridad: 12 (26.7%)
  confidencialidad: 9 (20.0%)
  resistencia: 4 (8.9%)
  no_repudio: 1 (2.2%)
  responsabilidad: 1 (2.2%)
```

## Próximos Pasos

Posibles mejoras:

1. **Caché de resultados**: Guardar comentarios ya clasificados en BD
2. **API asíncrona mejorada**: Usar background tasks de FastAPI
3. **Exportación**: Agregar endpoints para exportar a CSV/Excel
4. **Filtros adicionales**: Por categoría, rango de fechas, nivel de confianza
5. **Análisis de tendencias**: Evolución temporal de categorías
6. **Fine-tuning**: Reentrenar modelos con comentarios específicos del dominio
