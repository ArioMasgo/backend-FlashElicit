# Integración con Angular - Generación de PDF de Requisitos

## 📋 Descripción

Esta guía muestra cómo consumir el endpoint `/generate-pdf` de Flash Elicit desde una aplicación Angular. Incluye ejemplos completos de servicios, componentes y manejo de descarga de archivos.

## 🎯 Flujo de Trabajo

```
1. Usuario inicia scraping → /scrape
2. Angular guarda requirements en estado
3. Usuario hace clic en "Descargar PDF"
4. Angular envía requirements → /generate-pdf
5. Backend retorna PDF
6. Angular descarga automáticamente el archivo
```

## 📂 Estructura de Archivos Angular

```
src/
├── app/
│   ├── services/
│   │   └── requisitos.service.ts      # 🆕 Servicio para API
│   ├── models/
│   │   └── requisitos.model.ts        # 🆕 Interfaces TypeScript
│   └── components/
│       └── requisitos/
│           ├── requisitos.component.ts       # 🆕 Componente principal
│           ├── requisitos.component.html     # 🆕 Template
│           └── requisitos.component.scss     # 🆕 Estilos
```

## 🚀 Implementación Paso a Paso

### 1. Definir Interfaces (Models)

**Archivo**: `src/app/models/requisitos.model.ts`

```typescript
/**
 * Modelos de datos para requisitos No Funcionales
 * Basado en los schemas de Pydantic del backend
 */

export interface RequirementData {
  id: string;
  categoria: string;
  requisito: string;
  prioridad: 'Alta' | 'Media' | 'Baja';
  justificacion: string;
  criterios_aceptacion: string[];
  comentarios_relacionados: number;
}

export interface RequirementsResumen {
  total_requisitos: number;
  por_categoria: { [key: string]: number };
  prioridad_alta: number;
  prioridad_media: number;
  prioridad_baja: number;
}

export interface RequirementsData {
  requisitos: RequirementData[];
  resumen: RequirementsResumen;
  error?: string;
  raw_response?: string;
}

export interface PDFGenerationRequest {
  app_id: string;
  fecha_generacion: string;
  total_comentarios_analizados: number;
  requisitos: RequirementData[];
  resumen: RequirementsResumen;
}

export interface ScrapingResponse {
  success: boolean;
  app_id: string;
  total_reviews: number;
  reviews: any[];
  stats: any;
  requirements: RequirementsData | null;
}

export interface ScrapingRequest {
  playstore_url: string;
  max_reviews?: number;
  max_rating?: number;
}
```

### 2. Crear Servicio de Requisitos

**Archivo**: `src/app/services/requisitos.service.ts`

```typescript
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import {
  ScrapingRequest,
  ScrapingResponse,
  PDFGenerationRequest,
  RequirementsData
} from '../models/requisitos.model';

@Injectable({
  providedIn: 'root'
})
export class RequisitosService {
  private baseUrl = 'http://localhost:8000/api/scraping';

  constructor(private http: HttpClient) {}

  /**
   * Realiza scraping de comentarios y genera requisitos
   */
  scrapeAndGenerateRequirements(request: ScrapingRequest): Observable<ScrapingResponse> {
    return this.http.post<ScrapingResponse>(`${this.baseUrl}/scrape`, request);
  }

  /**
   * Genera un PDF de requisitos y lo descarga automáticamente
   */
  generateAndDownloadPDF(
    appId: string,
    totalComentarios: number,
    requirements: RequirementsData
  ): Observable<Blob> {
    const pdfRequest: PDFGenerationRequest = {
      app_id: appId,
      fecha_generacion: new Date().toISOString(),
      total_comentarios_analizados: totalComentarios,
      requisitos: requirements.requisitos,
      resumen: requirements.resumen
    };

    return this.http.post(`${this.baseUrl}/generate-pdf`, pdfRequest, {
      responseType: 'blob',
      headers: new HttpHeaders({
        'Content-Type': 'application/json'
      })
    });
  }

  /**
   * Descarga un archivo blob como PDF
   */
  downloadPDFBlob(blob: Blob, filename: string): void {
    // Crear URL temporal para el blob
    const url = window.URL.createObjectURL(blob);

    // Crear elemento <a> temporal
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;

    // Simular click para iniciar descarga
    document.body.appendChild(link);
    link.click();

    // Limpiar
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  }

  /**
   * Método combinado: genera y descarga el PDF en un solo paso
   */
  generatePDF(
    appId: string,
    totalComentarios: number,
    requirements: RequirementsData
  ): Observable<void> {
    return this.generateAndDownloadPDF(appId, totalComentarios, requirements).pipe(
      map((blob: Blob) => {
        const filename = `requisitos_${appId}_${Date.now()}.pdf`;
        this.downloadPDFBlob(blob, filename);
      })
    );
  }
}
```

### 3. Crear Componente Principal

**Archivo**: `src/app/components/requisitos/requisitos.component.ts`

```typescript
import { Component, OnInit } from '@angular/core';
import { RequisitosService } from '../../services/requisitos.service';
import {
  ScrapingRequest,
  ScrapingResponse,
  RequirementsData
} from '../../models/requisitos.model';

@Component({
  selector: 'app-requisitos',
  templateUrl: './requisitos.component.html',
  styleUrls: ['./requisitos.component.scss']
})
export class RequisitosComponent implements OnInit {
  // Estado de la aplicación
  playstoreUrl: string = '';
  isLoading: boolean = false;
  isGeneratingPDF: boolean = false;
  error: string | null = null;

  // Datos de requisitos
  appId: string = '';
  totalComentariosAnalizados: number = 0;
  requirements: RequirementsData | null = null;

  constructor(private requisitosService: RequisitosService) {}

  ngOnInit(): void {}

  /**
   * Inicia el proceso de scraping y generación de requisitos
   */
  iniciarScraping(): void {
    if (!this.playstoreUrl) {
      this.error = 'Por favor ingresa una URL de Play Store';
      return;
    }

    this.isLoading = true;
    this.error = null;
    this.requirements = null;

    const request: ScrapingRequest = {
      playstore_url: this.playstoreUrl,
      max_reviews: 100,
      max_rating: 3
    };

    this.requisitosService.scrapeAndGenerateRequirements(request).subscribe({
      next: (response: ScrapingResponse) => {
        this.isLoading = false;

        if (response.success && response.requirements) {
          // Guardar datos en el estado del componente
          this.appId = response.app_id;
          this.totalComentariosAnalizados = response.total_reviews;
          this.requirements = response.requirements;

          console.log('✅ Requisitos generados exitosamente:', this.requirements);
        } else {
          this.error = 'No se pudieron generar requisitos';
        }
      },
      error: (err) => {
        this.isLoading = false;
        this.error = `Error al procesar la solicitud: ${err.message}`;
        console.error('❌ Error:', err);
      }
    });
  }

  /**
   * Genera y descarga el PDF de requisitos
   */
  descargarPDF(): void {
    if (!this.requirements || !this.appId) {
      this.error = 'No hay requisitos disponibles para generar PDF';
      return;
    }

    this.isGeneratingPDF = true;
    this.error = null;

    this.requisitosService
      .generatePDF(this.appId, this.totalComentariosAnalizados, this.requirements)
      .subscribe({
        next: () => {
          this.isGeneratingPDF = false;
          console.log('✅ PDF descargado exitosamente');
          // Opcional: mostrar mensaje de éxito al usuario
        },
        error: (err) => {
          this.isGeneratingPDF = false;
          this.error = `Error al generar PDF: ${err.message}`;
          console.error('❌ Error al generar PDF:', err);
        }
      });
  }

  /**
   * Limpia el estado y permite nuevo scraping
   */
  limpiar(): void {
    this.playstoreUrl = '';
    this.requirements = null;
    this.appId = '';
    this.totalComentariosAnalizados = 0;
    this.error = null;
  }

  /**
   * Verifica si hay requisitos disponibles
   */
  get tieneRequisitos(): boolean {
    return this.requirements !== null && this.requirements.requisitos.length > 0;
  }

  /**
   * Obtiene el total de requisitos
   */
  get totalRequisitos(): number {
    return this.requirements?.resumen.total_requisitos || 0;
  }
}
```

### 4. Crear Template HTML

**Archivo**: `src/app/components/requisitos/requisitos.component.html`

```html
<div class="requisitos-container">
  <div class="header">
    <h1>Flash Elicit - Generador de Requisitos</h1>
    <p class="subtitle">Analiza comentarios de Play Store y genera requisitos No Funcionales</p>
  </div>

  <!-- Formulario de entrada -->
  <div class="form-section" *ngIf="!requirements">
    <div class="input-group">
      <label for="playstore-url">URL de Google Play Store:</label>
      <input
        type="text"
        id="playstore-url"
        [(ngModel)]="playstoreUrl"
        placeholder="https://play.google.com/store/apps/details?id=com.example.app"
        [disabled]="isLoading"
      />
    </div>

    <button
      class="btn btn-primary"
      (click)="iniciarScraping()"
      [disabled]="isLoading || !playstoreUrl"
    >
      <span *ngIf="!isLoading">🚀 Generar Requisitos</span>
      <span *ngIf="isLoading">
        <span class="spinner"></span> Procesando...
      </span>
    </button>
  </div>

  <!-- Mensaje de error -->
  <div class="alert alert-error" *ngIf="error">
    <strong>❌ Error:</strong> {{ error }}
  </div>

  <!-- Resultados -->
  <div class="results-section" *ngIf="tieneRequisitos">
    <!-- Resumen -->
    <div class="summary-card">
      <h2>📊 Resumen de Resultados</h2>
      <div class="stats">
        <div class="stat-item">
          <span class="stat-label">App ID:</span>
          <span class="stat-value">{{ appId }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Comentarios Analizados:</span>
          <span class="stat-value">{{ totalComentariosAnalizados }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Requisitos Generados:</span>
          <span class="stat-value">{{ totalRequisitos }}</span>
        </div>
      </div>

      <!-- Distribución por prioridad -->
      <div class="distribution">
        <h3>Distribución por Prioridad</h3>
        <div class="priority-bars">
          <div class="priority-item alta">
            <span>Alta:</span>
            <span>{{ requirements?.resumen.prioridad_alta }}</span>
          </div>
          <div class="priority-item media">
            <span>Media:</span>
            <span>{{ requirements?.resumen.prioridad_media }}</span>
          </div>
          <div class="priority-item baja">
            <span>Baja:</span>
            <span>{{ requirements?.resumen.prioridad_baja }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Lista de requisitos -->
    <div class="requirements-list">
      <h2>📋 Requisitos No Funcionales</h2>
      <div
        class="requirement-card"
        *ngFor="let req of requirements?.requisitos"
        [class.alta]="req.prioridad === 'Alta'"
        [class.media]="req.prioridad === 'Media'"
        [class.baja]="req.prioridad === 'Baja'"
      >
        <div class="req-header">
          <span class="req-id">{{ req.id }}</span>
          <span class="req-category">{{ req.categoria }}</span>
          <span class="req-priority" [class]="req.prioridad.toLowerCase()">
            {{ req.prioridad }}
          </span>
        </div>

        <div class="req-body">
          <p class="req-text"><strong>Requisito:</strong> {{ req.requisito }}</p>
          <p class="req-justification">
            <strong>Justificación:</strong> {{ req.justificacion }}
          </p>

          <div class="req-criteria">
            <strong>Criterios de Aceptación:</strong>
            <ul>
              <li *ngFor="let criterio of req.criterios_aceptacion">{{ criterio }}</li>
            </ul>
          </div>

          <p class="req-comments">
            <strong>Basado en:</strong> {{ req.comentarios_relacionados }} comentarios
          </p>
        </div>
      </div>
    </div>

    <!-- Botones de acción -->
    <div class="actions">
      <button
        class="btn btn-success"
        (click)="descargarPDF()"
        [disabled]="isGeneratingPDF"
      >
        <span *ngIf="!isGeneratingPDF">📄 Descargar PDF</span>
        <span *ngIf="isGeneratingPDF">
          <span class="spinner"></span> Generando PDF...
        </span>
      </button>

      <button class="btn btn-secondary" (click)="limpiar()">
        🔄 Nuevo Análisis
      </button>
    </div>
  </div>
</div>
```

### 5. Estilos (Opcional)

**Archivo**: `src/app/components/requisitos/requisitos.component.scss`

```scss
.requisitos-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;

  .header {
    text-align: center;
    margin-bottom: 2rem;

    h1 {
      font-size: 2.5rem;
      color: #1f2937;
      margin-bottom: 0.5rem;
    }

    .subtitle {
      font-size: 1.1rem;
      color: #6b7280;
    }
  }

  .form-section {
    background: white;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    margin-bottom: 2rem;

    .input-group {
      margin-bottom: 1.5rem;

      label {
        display: block;
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: #374151;
      }

      input {
        width: 100%;
        padding: 0.75rem;
        border: 1px solid #d1d5db;
        border-radius: 6px;
        font-size: 1rem;

        &:focus {
          outline: none;
          border-color: #3b82f6;
          box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }

        &:disabled {
          background-color: #f3f4f6;
          cursor: not-allowed;
        }
      }
    }
  }

  .btn {
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 6px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;

    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    &.btn-primary {
      background-color: #3b82f6;
      color: white;

      &:hover:not(:disabled) {
        background-color: #2563eb;
      }
    }

    &.btn-success {
      background-color: #10b981;
      color: white;

      &:hover:not(:disabled) {
        background-color: #059669;
      }
    }

    &.btn-secondary {
      background-color: #6b7280;
      color: white;

      &:hover:not(:disabled) {
        background-color: #4b5563;
      }
    }
  }

  .alert {
    padding: 1rem;
    border-radius: 6px;
    margin-bottom: 1rem;

    &.alert-error {
      background-color: #fee2e2;
      color: #991b1b;
      border: 1px solid #fecaca;
    }
  }

  .summary-card {
    background: white;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    margin-bottom: 2rem;

    h2 {
      margin-bottom: 1.5rem;
      color: #1f2937;
    }

    .stats {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1rem;
      margin-bottom: 2rem;

      .stat-item {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;

        .stat-label {
          font-size: 0.875rem;
          color: #6b7280;
        }

        .stat-value {
          font-size: 1.5rem;
          font-weight: 700;
          color: #1f2937;
        }
      }
    }

    .priority-bars {
      .priority-item {
        display: flex;
        justify-content: space-between;
        padding: 0.75rem;
        margin-bottom: 0.5rem;
        border-radius: 6px;
        font-weight: 600;

        &.alta {
          background-color: #fee2e2;
          color: #991b1b;
        }

        &.media {
          background-color: #fef3c7;
          color: #92400e;
        }

        &.baja {
          background-color: #d1fae5;
          color: #065f46;
        }
      }
    }
  }

  .requirements-list {
    .requirement-card {
      background: white;
      padding: 1.5rem;
      border-radius: 8px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
      margin-bottom: 1rem;
      border-left: 4px solid #d1d5db;

      &.alta {
        border-left-color: #ef4444;
      }

      &.media {
        border-left-color: #f59e0b;
      }

      &.baja {
        border-left-color: #10b981;
      }

      .req-header {
        display: flex;
        gap: 1rem;
        margin-bottom: 1rem;
        flex-wrap: wrap;

        .req-id {
          font-weight: 700;
          color: #1f2937;
        }

        .req-category {
          color: #6b7280;
        }

        .req-priority {
          padding: 0.25rem 0.75rem;
          border-radius: 9999px;
          font-size: 0.875rem;
          font-weight: 600;

          &.alta {
            background-color: #fee2e2;
            color: #991b1b;
          }

          &.media {
            background-color: #fef3c7;
            color: #92400e;
          }

          &.baja {
            background-color: #d1fae5;
            color: #065f46;
          }
        }
      }

      .req-body {
        p {
          margin-bottom: 1rem;
          line-height: 1.6;
        }

        .req-criteria {
          ul {
            margin-left: 1.5rem;
            margin-top: 0.5rem;

            li {
              margin-bottom: 0.5rem;
            }
          }
        }

        .req-comments {
          font-size: 0.875rem;
          color: #6b7280;
        }
      }
    }
  }

  .actions {
    display: flex;
    gap: 1rem;
    justify-content: center;
    margin-top: 2rem;
  }

  .spinner {
    display: inline-block;
    width: 1rem;
    height: 1rem;
    border: 2px solid currentColor;
    border-right-color: transparent;
    border-radius: 50%;
    animation: spin 0.6s linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
}
```

### 6. Configurar Módulo

**Archivo**: `src/app/app.module.ts`

```typescript
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

import { AppComponent } from './app.component';
import { RequisitosComponent } from './components/requisitos/requisitos.component';
import { RequisitosService } from './services/requisitos.service';

@NgModule({
  declarations: [
    AppComponent,
    RequisitosComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule,  // ✅ Importante para hacer peticiones HTTP
    FormsModule        // ✅ Importante para ngModel
  ],
  providers: [
    RequisitosService
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
```

## 🔧 Configuración CORS (Backend)

Si Angular corre en `http://localhost:4200` y el backend en `http://localhost:8000`, necesitas habilitar CORS en el backend.

**Archivo**: `backend/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",  # Angular dev server
        "http://localhost:3000",  # Otros frontends
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ... resto del código
```

## 🧪 Testing

### 1. Ejecutar el Backend

```bash
cd backend
python main.py
```

### 2. Ejecutar Angular

```bash
cd frontend
ng serve
```

### 3. Abrir en el navegador

```
http://localhost:4200
```

### 4. Probar el flujo completo

1. Ingresa una URL de Play Store
2. Haz clic en "Generar Requisitos"
3. Espera a que se procesen los comentarios
4. Verifica que se muestren los requisitos
5. Haz clic en "Descargar PDF"
6. Verifica que se descargue el archivo PDF

## 📱 Ejemplo de Uso con Botón Simple

Si solo necesitas un botón para descargar el PDF:

```typescript
// En tu componente
downloadPDF() {
  const pdfRequest = {
    app_id: this.appId,
    fecha_generacion: new Date().toISOString(),
    total_comentarios_analizados: this.totalComentarios,
    requisitos: this.requirements.requisitos,
    resumen: this.requirements.resumen
  };

  this.http.post('http://localhost:8000/api/scraping/generate-pdf', pdfRequest, {
    responseType: 'blob'
  }).subscribe({
    next: (blob: Blob) => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `requisitos_${this.appId}.pdf`;
      a.click();
      window.URL.revokeObjectURL(url);
    },
    error: (error) => {
      console.error('Error al generar PDF:', error);
    }
  });
}
```

```html
<button (click)="downloadPDF()">📄 Descargar PDF</button>
```

## 🛠️ Manejo de Errores Avanzado

```typescript
generatePDF(): void {
  this.isGeneratingPDF = true;
  this.error = null;

  this.requisitosService
    .generatePDF(this.appId, this.totalComentariosAnalizados, this.requirements!)
    .subscribe({
      next: () => {
        this.isGeneratingPDF = false;
        // Mostrar notificación de éxito
        this.showSuccessNotification('PDF descargado exitosamente');
      },
      error: (err) => {
        this.isGeneratingPDF = false;

        // Manejo de errores específicos
        if (err.status === 422) {
          this.error = 'Los datos de requisitos no son válidos';
        } else if (err.status === 500) {
          this.error = 'Error interno del servidor al generar PDF';
        } else if (err.status === 0) {
          this.error = 'No se pudo conectar con el servidor. Verifica que esté ejecutándose.';
        } else {
          this.error = `Error al generar PDF: ${err.message}`;
        }

        console.error('❌ Error completo:', err);
      }
    });
}
```

## 🎨 Mejoras Adicionales

### 1. Añadir Indicador de Progreso

```html
<div class="progress-bar" *ngIf="isGeneratingPDF">
  <div class="progress-fill"></div>
  <span>Generando PDF...</span>
</div>
```

### 2. Preview de Requisitos Antes de Descargar

```typescript
previewRequirements() {
  const modal = this.modalService.open(RequirementsPreviewComponent);
  modal.componentInstance.requirements = this.requirements;
}
```

### 3. Guardar en LocalStorage

```typescript
// Guardar requisitos
localStorage.setItem('requirements', JSON.stringify(this.requirements));

// Recuperar requisitos
const saved = localStorage.getItem('requirements');
if (saved) {
  this.requirements = JSON.parse(saved);
}
```

## 📚 Recursos Adicionales

- [Angular HttpClient](https://angular.io/guide/http)
- [TypeScript Interfaces](https://www.typescriptlang.org/docs/handbook/interfaces.html)
- [RxJS Observables](https://rxjs.dev/guide/observable)
- [Blob API](https://developer.mozilla.org/en-US/docs/Web/API/Blob)

## ⚠️ Notas Importantes

1. **CORS**: Asegúrate de configurar CORS en el backend
2. **Timeout**: Ajusta el timeout si el procesamiento es largo
3. **Tamaño**: Los PDFs con muchos requisitos pueden ser grandes
4. **Cache**: Considera guardar requisitos en estado global (NgRx, Akita, etc.)
5. **Loading States**: Siempre maneja estados de carga para mejor UX

## 🐛 Troubleshooting

### Error: "CORS policy: No 'Access-Control-Allow-Origin'"

Configura CORS en el backend (ver sección de configuración CORS arriba).

### Error: "Cannot find module '@angular/common/http'"

```bash
npm install @angular/common
```

### El PDF se descarga pero está vacío

Verifica que `responseType: 'blob'` esté configurado correctamente en la petición HTTP.

### El PDF no se descarga automáticamente

Algunos navegadores bloquean descargas automáticas. Verifica la configuración del navegador.

---

**¿Listo para integrar?** 🚀

Con esta guía tienes todo lo necesario para integrar la generación de PDFs en tu aplicación Angular. Si tienes dudas, revisa la documentación completa en [README_PDF.md](README_PDF.md).
