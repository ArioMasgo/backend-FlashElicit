# Generación de PDF de Requisitos No Funcionales

## 📋 Descripción

Este módulo permite generar documentos PDF profesionales con los requisitos No Funcionales generados por Flash Elicit. El PDF incluye formato estructurado, portada, resumen ejecutivo y lista detallada de requisitos.

## 🎯 Características

- ✅ **Stateless**: No requiere base de datos ni cache
- ✅ **Formato profesional**: PDF bien estructurado con estilos corporativos
- ✅ **Resumen ejecutivo**: Estadísticas y distribuciones visuales
- ✅ **Categorías ISO 25010**: Clasificación según norma de calidad
- ✅ **Prioridades con color**: Alta (rojo), Media (naranja), Baja (verde)
- ✅ **Metadatos completos**: App ID, fecha, comentarios analizados

## 🔄 Flujo de Trabajo

```
1. Frontend → POST /scrape → Obtiene requirements
2. Frontend → Guarda requirements en estado (React/Vue/etc.)
3. Usuario → Click en "Descargar PDF"
4. Frontend → POST /generate-pdf (envía requirements)
5. Backend → Genera PDF profesional
6. Frontend → Descarga automática del archivo
```

## 📂 Archivos Creados

```
backend/
├── app/
│   ├── api/routes/
│   │   └── scraping.py               # ✅ Endpoint /generate-pdf agregado
│   ├── services/
│   │   └── pdf_generator_service.py  # 🆕 Servicio generador de PDF
│   └── schemas/
│       └── scraping_schemas.py       # ✅ PDFGenerationRequest agregado
├── requirements.txt                  # ✅ reportlab>=4.0.0 agregado
├── test_pdf_generation.py            # 🆕 Script de prueba
└── README_PDF.md                     # 🆕 Esta documentación
```

## 🚀 Instalación

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

La dependencia `reportlab>=4.0.0` ya está incluida en `requirements.txt`.

### 2. Verificar que el servidor esté ejecutándose

```bash
python main.py
```

El servidor debe estar en: `http://localhost:8000`

## 📡 Uso del Endpoint

### Endpoint

```
POST /api/scraping/generate-pdf
```

### Request Body

```json
{
  "app_id": "com.example.app",
  "fecha_generacion": "2025-10-22T10:30:00",
  "total_comentarios_analizados": 150,
  "requisitos": [
    {
      "id": "NFR-001",
      "categoria": "autenticidad",
      "requisito": "El sistema debe implementar autenticación biométrica...",
      "prioridad": "Alta",
      "justificacion": "Múltiples usuarios reportan problemas...",
      "criterios_aceptacion": [
        "Soporte para huella digital",
        "Tiempo de respuesta menor a 2 segundos"
      ],
      "comentarios_relacionados": 23
    }
  ],
  "resumen": {
    "total_requisitos": 6,
    "por_categoria": {
      "autenticidad": 2,
      "confidencialidad": 3,
      "integridad": 1
    },
    "prioridad_alta": 3,
    "prioridad_media": 2,
    "prioridad_baja": 1
  }
}
```

### Response

- **Content-Type**: `application/pdf`
- **Headers**: `Content-Disposition: attachment; filename=requisitos_{app_id}.pdf`
- **Body**: Archivo PDF binario

### Ejemplo con cURL

```bash
curl -X POST http://localhost:8000/api/scraping/generate-pdf \
  -H "Content-Type: application/json" \
  -d @requisitos_data.json \
  --output requisitos.pdf
```

### Ejemplo con Python (requests)

```python
import requests
from datetime import datetime

data = {
    "app_id": "com.example.app",
    "fecha_generacion": datetime.now().isoformat(),
    "total_comentarios_analizados": 150,
    "requisitos": [...],  # Lista de requisitos
    "resumen": {...}      # Resumen estadístico
}

response = requests.post(
    "http://localhost:8000/api/scraping/generate-pdf",
    json=data
)

if response.status_code == 200:
    with open("requisitos.pdf", "wb") as f:
        f.write(response.content)
    print("PDF generado exitosamente")
```

## 🧪 Testing

### Ejecutar script de prueba

```bash
python test_pdf_generation.py
```

Este script:
1. Genera datos de ejemplo con 6 requisitos
2. Envía al endpoint `/generate-pdf`
3. Guarda el PDF generado
4. Verifica el tamaño y contenido

**Salida esperada**:

```
🧪 PRUEBA DE GENERACIÓN DE PDF
============================================================

📊 Datos de prueba:
   App ID: com.example.banking.app
   Requisitos: 6
   Comentarios analizados: 150

🌐 Conectando a http://localhost:8000/api/scraping/generate-pdf...
✅ PDF generado exitosamente!

📄 PDF guardado en: requisitos_test_20251022_103045.pdf
   Tamaño: 45231 bytes

✅ Prueba completada exitosamente!
```

### Pruebas manuales

1. **Iniciar el servidor**:
   ```bash
   python main.py
   ```

2. **Ejecutar test**:
   ```bash
   python test_pdf_generation.py
   ```

3. **Abrir el PDF generado** y verificar:
   - Portada con metadatos
   - Resumen ejecutivo con tablas
   - Lista de requisitos detallada
   - Apéndice con metodología

## 📄 Estructura del PDF

### 1. Portada

- Título: "Requisitos No Funcionales Generados Automáticamente"
- App ID
- Fecha de generación
- Total de comentarios analizados
- Marca "Flash Elicit"

### 2. Resumen Ejecutivo

- Descripción general del documento
- **Tabla de Distribución por Categoría**:
  - Categoría ISO 25010
  - Cantidad de requisitos
  - Porcentaje

- **Tabla de Distribución por Prioridad**:
  - Alta / Media / Baja
  - Cantidad
  - Porcentaje

### 3. Lista de Requisitos

Para cada requisito:

- **Encabezado**: ID - Categoría - Prioridad (con color)
- **Requisito**: Descripción completa
- **Justificación**: Por qué es importante
- **Criterios de Aceptación**: Lista con viñetas
- **Basado en**: Número de comentarios relacionados

### 4. Apéndice

- **Metodología**: Proceso de generación
  1. Extracción de comentarios
  2. Filtrado binario (BERT)
  3. Clasificación multiclase (ISO 25010)
  4. Generación de requisitos (Mistral)

- **Categorías ISO 25010**: Descripción de cada categoría

- **Información de generación**: Timestamp del PDF

## 🎨 Estilos y Formato

### Colores por Prioridad

- **Alta**: <span style="color:#EF4444">Rojo</span>
- **Media**: <span style="color:#F59E0B">Naranja</span>
- **Baja**: <span style="color:#10B981">Verde</span>

### Categorías ISO 25010

| Categoría | Descripción |
|-----------|-------------|
| `autenticidad` | Verificación de identidad de usuarios y sistemas |
| `confidencialidad` | Protección de datos contra acceso no autorizado |
| `integridad` | Prevención de modificación no autorizada |
| `no_repudio` | Trazabilidad de acciones y transacciones |
| `resistencia` | Disponibilidad y robustez ante fallos |
| `responsabilidad` | Auditoría y rendición de cuentas |

### Tipografía

- **Títulos**: Helvetica-Bold, 24pt
- **Subtítulos**: Helvetica-Bold, 16pt
- **Cuerpo**: Helvetica, 11pt
- **Metadatos**: Helvetica, 10pt (gris)

## 🔧 Personalización

### Modificar estilos del PDF

Editar `app/services/pdf_generator_service.py`:

```python
class RequirementsPDFGenerator:
    # Cambiar colores de prioridades
    PRIORIDAD_COLORS = {
        "Alta": colors.HexColor("#EF4444"),    # Personalizar
        "Media": colors.HexColor("#F59E0B"),   # Personalizar
        "Baja": colors.HexColor("#10B981")     # Personalizar
    }
```

### Agregar logo/marca

En el método `_build_cover_page()`:

```python
# Agregar logo
logo = RLImage("path/to/logo.png", width=2*inch, height=1*inch)
elements.append(logo)
```

### Cambiar tamaño de página

En el método `generate_pdf()`:

```python
doc = SimpleDocTemplate(
    buffer,
    pagesize=letter,  # Cambiar a A4, legal, etc.
    # ...
)
```

## ⚙️ Integración con Frontend

### Angular (Guía Completa)

Para una guía completa de integración con Angular, consulta:

📘 **[README_ANGULAR.md](README_ANGULAR.md)** - Guía completa con servicios, componentes y ejemplos

### React Example

```javascript
const downloadPDF = async (requirementsData) => {
  try {
    const response = await fetch('http://localhost:8000/api/scraping/generate-pdf', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requirementsData),
    });

    if (!response.ok) throw new Error('Error al generar PDF');

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `requisitos_${requirementsData.app_id}.pdf`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  } catch (error) {
    console.error('Error:', error);
  }
};
```

### Vue Example

```javascript
async downloadPDF() {
  try {
    const response = await axios.post(
      'http://localhost:8000/api/scraping/generate-pdf',
      this.requirementsData,
      { responseType: 'blob' }
    );

    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `requisitos_${this.requirementsData.app_id}.pdf`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  } catch (error) {
    console.error('Error al generar PDF:', error);
  }
}
```

## 🐛 Troubleshooting

### Error: "No module named 'reportlab'"

```bash
pip install reportlab>=4.0.0
```

### Error: "No se pudo conectar al servidor"

Asegúrate de que el servidor esté ejecutándose:

```bash
python main.py
```

### PDF vacío o corrupto

Verifica que los datos enviados tengan la estructura correcta:

```python
# Debe tener al menos un requisito
assert len(data['requisitos']) > 0

# Cada requisito debe tener todos los campos
for req in data['requisitos']:
    assert 'id' in req
    assert 'categoria' in req
    assert 'requisito' in req
    # ...
```

### Error 422: Validation Error

Verifica que todos los campos requeridos estén presentes:

- `app_id` (string, no vacío)
- `fecha_generacion` (string ISO format)
- `total_comentarios_analizados` (int)
- `requisitos` (array, al menos 1 elemento)
- `resumen` (object con estructura correcta)

## 📊 Performance

| Métrica | Valor Típico |
|---------|--------------|
| Generación de PDF (10 requisitos) | ~1-2 segundos |
| Generación de PDF (50 requisitos) | ~3-5 segundos |
| Tamaño de PDF (10 requisitos) | ~30-50 KB |
| Tamaño de PDF (50 requisitos) | ~80-150 KB |
| Timeout recomendado | 30 segundos |

## 🔐 Seguridad

- ✅ **Sin persistencia**: No se almacenan datos en el servidor
- ✅ **Validación de entrada**: Pydantic valida estructura
- ✅ **Sin inyección**: ReportLab escapa caracteres especiales
- ✅ **Stateless**: Cada request es independiente

## 📚 Documentación Relacionada

- [README.md](README.md) - Documentación principal
- [README_REQUISITOS.md](README_REQUISITOS.md) - Generación de requisitos
- [README_CLASIFICACION.md](README_CLASIFICACION.md) - Clasificación BERT
- [ReportLab User Guide](https://www.reportlab.com/docs/reportlab-userguide.pdf)

## 🎯 Próximas Mejoras

- [ ] Agregar gráficos (pie charts, bar charts)
- [ ] Incluir comentarios originales en apéndice
- [ ] Exportación en múltiples formatos (DOCX, Markdown)
- [ ] Plantillas personalizables
- [ ] Marca de agua personalizable
- [ ] Numeración de páginas
- [ ] Tabla de contenidos automática
- [ ] Opción para incluir/excluir secciones

## 📝 Licencia

[Tu licencia aquí]

## 👥 Contribuciones

Las contribuciones son bienvenidas. Para agregar features:

1. Fork el repositorio
2. Crea una rama para tu feature
3. Implementa y prueba
4. Abre un Pull Request

---

**Generado por**: Flash Elicit
**Fecha**: 22 de octubre de 2025
**Versión**: 1.0
