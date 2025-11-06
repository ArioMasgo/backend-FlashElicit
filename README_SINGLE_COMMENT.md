# Endpoint de Clasificación de Comentario Individual

## Descripción

Este endpoint permite clasificar **un solo comentario** a través de los filtros BERT y generar un requisito No Funcional si el comentario es relevante.

## Ruta

```
POST /api/scraping/classify-single
```

## Flujo del Proceso

```
1. Recibe comentario individual
   ↓
2. Filtro binario (BERT) → ¿Es relevante?
   ↓
   ├─ NO → Retorna mensaje "no relevante" ❌
   │
   └─ SÍ → Continúa ✅
      ↓
3. Clasificación multiclase (BERT) → Categoría ISO 25010
   ↓
4. Generación de requisito (Mistral) → Requisito No Funcional
   ↓
5. Retorna comentario clasificado + requisito
```

## Request

### Schema

```json
{
  "comentario": "string (mínimo 10 caracteres)",
  "calificacion": 1-5 (opcional, default: 1)
}
```

### Validaciones

- El comentario no puede estar vacío
- Debe tener al menos 10 caracteres
- La calificación debe estar entre 1 y 5 estrellas

### Ejemplo

```bash
curl -X POST http://localhost:8000/api/scraping/classify-single \
  -H "Content-Type: application/json" \
  -d '{
    "comentario": "No puedo iniciar sesión con mi huella digital, siempre me pide la contraseña",
    "calificacion": 2
  }'
```

## Response

### Caso 1: Comentario NO Relevante

```json
{
  "success": true,
  "es_relevante": false,
  "mensaje": "El comentario no fue clasificado como relevante para requisitos de seguridad según ISO 25010. No se generó ningún requisito.",
  "comentario": "Me gusta mucho la interfaz, es muy bonita",
  "calificacion": 5,
  "categoria": null,
  "confianza": null,
  "requisito": null,
  "error": null
}
```

### Caso 2: Comentario Relevante (con requisito generado)

```json
{
  "success": true,
  "es_relevante": true,
  "mensaje": "Comentario clasificado como relevante en la categoría 'autenticidad' con 95.23% de confianza.",
  "comentario": "No puedo iniciar sesión con mi huella digital, siempre me pide la contraseña",
  "calificacion": 2,
  "categoria": "autenticidad",
  "confianza": 0.9523,
  "requisito": {
    "id": "NFR-001",
    "categoria": "autenticidad",
    "requisito": "El sistema debe implementar autenticación biométrica confiable con tasa de error menor al 1% y tiempo de respuesta menor a 2 segundos",
    "prioridad": "Alta",
    "justificacion": "El usuario reporta fallas constantes en la autenticación por huella digital, lo que afecta la experiencia y seguridad del acceso al sistema",
    "criterios_aceptacion": [
      "Soporte para múltiples métodos biométricos (huella digital y reconocimiento facial)",
      "Tasa de falsos rechazos menor al 1%",
      "Tiempo de respuesta de autenticación menor a 2 segundos",
      "Fallback automático a contraseña en caso de 3 intentos fallidos",
      "Registro de intentos de autenticación con timestamp y método utilizado"
    ],
    "comentarios_relacionados": 1
  },
  "error": null
}
```

### Caso 3: Comentario Relevante (error al generar requisito)

```json
{
  "success": true,
  "es_relevante": true,
  "mensaje": "Comentario clasificado como relevante en la categoría 'confidencialidad' con 87.45% de confianza.",
  "comentario": "La app solicita permisos innecesarios",
  "calificacion": 1,
  "categoria": "confidencialidad",
  "confianza": 0.8745,
  "requisito": null,
  "error": "No se pudo parsear la respuesta del modelo"
}
```

## Estructura de la Respuesta

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `success` | boolean | Indica si la operación fue exitosa |
| `es_relevante` | boolean | **true** si pasa el filtro binario, **false** si no |
| `mensaje` | string | Descripción del resultado |
| `comentario` | string | Comentario procesado |
| `calificacion` | int | Calificación en estrellas (1-5) |
| `categoria` | string\|null | Categoría ISO 25010 (solo si es relevante) |
| `confianza` | float\|null | Confianza de clasificación 0.0-1.0 (solo si es relevante) |
| `requisito` | object\|null | Requisito No Funcional generado (solo si es relevante) |
| `error` | string\|null | Mensaje de error (si hubo problemas al generar requisito) |

## Categorías ISO 25010

Las posibles categorías de clasificación son:

| Categoría | Descripción |
|-----------|-------------|
| `autenticidad` | Verificación de identidad y autenticación |
| `confidencialidad` | Privacidad y protección de datos |
| `integridad` | Prevención de corrupción de datos |
| `no_repudio` | Trazabilidad y responsabilidad de acciones |
| `resistencia` | Disponibilidad y robustez del sistema |
| `responsabilidad` | Auditoría y rendición de cuentas |

## Ejemplos de Uso

### Python (requests)

```python
import requests

url = "http://localhost:8000/api/scraping/classify-single"
payload = {
    "comentario": "La aplicación se cae cuando intento hacer transferencias",
    "calificacion": 1
}

response = requests.post(url, json=payload)
data = response.json()

if data['es_relevante']:
    print(f"Categoría: {data['categoria']}")
    if data['requisito']:
        print(f"Requisito: {data['requisito']['requisito']}")
else:
    print("Comentario no relevante")
```

### JavaScript (fetch)

```javascript
const url = "http://localhost:8000/api/scraping/classify-single";
const payload = {
  comentario: "No puedo iniciar sesión con mi huella digital",
  calificacion: 2
};

fetch(url, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(payload)
})
.then(res => res.json())
.then(data => {
  if (data.es_relevante) {
    console.log(`Categoría: ${data.categoria}`);
    if (data.requisito) {
      console.log(`Requisito: ${data.requisito.requisito}`);
    }
  } else {
    console.log("Comentario no relevante");
  }
});
```

### cURL

```bash
# Comentario relevante
curl -X POST http://localhost:8000/api/scraping/classify-single \
  -H "Content-Type: application/json" \
  -d '{
    "comentario": "No puedo iniciar sesión con mi huella digital",
    "calificacion": 2
  }' | jq

# Comentario no relevante
curl -X POST http://localhost:8000/api/scraping/classify-single \
  -H "Content-Type: application/json" \
  -d '{
    "comentario": "Me gusta la interfaz de la app",
    "calificacion": 5
  }' | jq
```

## Testing

### Script de Prueba

Ejecuta el script de prueba incluido:

```bash
python test_single_comment.py
```

Este script prueba:
- ✅ Comentarios relevantes (autenticidad, confidencialidad, resistencia)
- ❌ Comentarios no relevantes (generales, UI)

### Resultados

El script genera archivos JSON con las respuestas:
- `test_single_response_True.json` - Comentarios relevantes
- `test_single_response_False.json` - Comentarios no relevantes

## Logs del Servidor

El servidor muestra logs detallados:

```
============================================================
🔍 CLASIFICACIÓN DE COMENTARIO INDIVIDUAL
============================================================
Comentario: "No puedo iniciar sesión con mi huella digital..."
Calificación: 2★

============================================================
🤖 APLICANDO FILTRO BINARIO (Relevancia)
============================================================
Resultado: ✅ RELEVANTE

============================================================
🤖 APLICANDO CLASIFICACIÓN MULTICLASE (ISO 25010)
============================================================
Categoría: autenticidad
Confianza: 0.9523

============================================================
🧠 GENERANDO REQUISITO PARA COMENTARIO INDIVIDUAL
============================================================
Categoría: autenticidad (confianza: 0.95)
Comentario: "No puedo iniciar sesión con mi huella digital..."

Intento 1/3...
✅ Respuesta recibida del modelo (856 caracteres)
✅ Requisito generado exitosamente
   ID: NFR-001
   Prioridad: Alta
============================================================

============================================================
✅ PROCESO COMPLETADO
============================================================
```

## Códigos de Error

| Código | Descripción |
|--------|-------------|
| 200 | Operación exitosa |
| 422 | Validación fallida (comentario inválido) |
| 500 | Error interno del servidor |

### Ejemplo de Error de Validación (422)

```json
{
  "detail": [
    {
      "loc": ["body", "comentario"],
      "msg": "El comentario debe tener al menos 10 caracteres",
      "type": "value_error"
    }
  ]
}
```

## Comparación con Endpoint de Scraping

| Característica | `/scrape` | `/classify-single` |
|----------------|-----------|-------------------|
| Entrada | URL de Play Store | Un comentario de texto |
| Scraping | ✅ Sí | ❌ No |
| Cantidad | Múltiples comentarios | Un solo comentario |
| Filtro binario | ✅ Sí | ✅ Sí |
| Clasificación multiclase | ✅ Sí (si relevante) | ✅ Sí (si relevante) |
| Generación de requisitos | ✅ Múltiples | ✅ Uno |
| Mensaje si no relevante | No aplica | ✅ Mensaje específico |
| Tiempo de respuesta | 30s - 2min | 2-10s |

## Casos de Uso

### 1. Validación en Tiempo Real

Integra el endpoint en un formulario web para validar comentarios de usuarios en tiempo real:

```javascript
async function validateComment(comment) {
  const response = await fetch('/api/scraping/classify-single', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ comentario: comment, calificacion: 1 })
  });

  const data = await response.json();

  if (data.es_relevante) {
    showAlert("Este comentario es relevante para requisitos de seguridad");
    displayRequirement(data.requisito);
  }
}
```

### 2. Procesamiento de Feedback Individual

Procesa feedback de usuarios uno por uno para generar requisitos específicos:

```python
comments = load_user_feedback()

for comment in comments:
    response = classify_single_comment(comment)
    if response['es_relevante']:
        save_requirement(response['requisito'])
```

### 3. Análisis de Tickets de Soporte

Clasifica tickets de soporte para identificar problemas de seguridad:

```python
ticket = get_support_ticket(ticket_id)
result = classify_single_comment(ticket['description'])

if result['es_relevante']:
    escalate_to_security_team(ticket_id, result['categoria'])
```

## Optimizaciones

### Performance

- **Carga de modelos**: Los modelos BERT se cargan una sola vez (singleton)
- **Inferencia rápida**: Procesamiento de un comentario toma 2-5 segundos
- **GPU opcional**: Automáticamente usa GPU si está disponible

### Reintentos

- La generación de requisitos tiene **3 reintentos** automáticos
- Si falla, el endpoint aún retorna la clasificación sin el requisito

### Manejo de Errores

- Si el filtro binario falla → Error 500
- Si la generación de requisito falla → Retorna clasificación sin requisito
- Si el comentario es inválido → Error 422 (validación)

## Documentación de la API

FastAPI genera documentación interactiva automática:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Desde estas interfaces puedes:
- Ver el schema completo
- Probar el endpoint directamente
- Ver ejemplos de request/response

## Próximos Pasos

Mejoras posibles:

1. **Batch processing**: Procesar múltiples comentarios individuales en paralelo
2. **Caché**: Guardar clasificaciones para comentarios repetidos
3. **Webhooks**: Notificar cuando se genera un requisito crítico
4. **Refinamiento**: Permitir al usuario refinar el requisito generado
5. **Exportación**: Generar PDF del requisito generado
6. **Integración**: Conectar con sistemas de gestión de requisitos (Jira, etc.)

## Soporte

Para reportar problemas o sugerencias, crea un issue en el repositorio.
