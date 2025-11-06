from pydantic import BaseModel, Field, validator
from typing import List, Optional
from enum import Enum
import re
from datetime import datetime

class CriteriosBusqueda(str, Enum):
    """Criterios de ordenamiento para comentarios de Google Play Store"""
    RECIENTES = "recientes"
    RELEVANTES = "relevantes"

class MulticlassModelEnum(str, Enum):
    """Modelos multiclase disponibles"""
    BETO = "beto"
    ROBERTUITO = "robertuito"

class ScrapingRequest(BaseModel):
    playstore_url: str = Field(..., description="URL de Google Play Store")
    max_reviews: int = Field(default=9000, description="Número máximo de comentarios a extraer")
    max_rating: int = Field(default=3, description="Calificación máxima a filtrar (≤ este valor)")
    criterios_busqueda: CriteriosBusqueda = Field(..., description="Criterio de ordenamiento: 'recientes' (más nuevos) o 'relevantes' (más útiles según Google)")
    multiclass_model: Optional[MulticlassModelEnum] = Field(
        default=MulticlassModelEnum.BETO,
        description="Modelo multiclase a utilizar para clasificación ISO 25010 (beto o robertuito)"
    )

    @validator('playstore_url')
    def validate_playstore_url(cls, v):
        if not v.startswith('https://play.google.com/store/apps/details?id='):
            raise ValueError('URL debe ser de Google Play Store')
        return v

    @property
    def app_id(self) -> str:
        """Extrae el app_id de la URL"""
        match = re.search(r'id=([^&]+)', self.playstore_url)
        if match:
            return match.group(1)
        raise ValueError("No se pudo extraer el app_id de la URL")

class ReviewData(BaseModel):
    id_original: str = Field(..., description="ID único del comentario")
    comentario: str = Field(..., description="Contenido del comentario")
    calificacion: int = Field(..., description="Calificación en estrellas (1-5)")
    fecha: str = Field(..., description="Fecha del comentario (YYYY-MM-DD)")
    usuario: str = Field(..., description="Nombre del usuario")
    categoria: str = Field(..., description="Categoría ISO 25010 asignada por el modelo multiclase")
    confianza: float = Field(..., description="Nivel de confianza de la clasificación (0.0 - 1.0)")

class RequirementData(BaseModel):
    """Estructura de un requisito No Funcional generado"""
    id: str = Field(..., description="Identificador único del requisito (ej: NFR-001)")
    categoria: str = Field(..., description="Categoría ISO 25010 del requisito")
    requisito: str = Field(..., description="Descripción del requisito No Funcional")
    prioridad: str = Field(..., description="Prioridad del requisito (Alta/Media/Baja)")
    justificacion: str = Field(..., description="Justificación basada en comentarios de usuarios")
    criterios_aceptacion: List[str] = Field(..., description="Lista de criterios de aceptación")
    comentarios_relacionados: int = Field(..., description="Número de comentarios que motivaron este requisito")

class RequirementsResumen(BaseModel):
    """Resumen de requisitos generados"""
    total_requisitos: int = Field(..., description="Total de requisitos generados")
    por_categoria: dict = Field(..., description="Conteo de requisitos por categoría ISO 25010")
    prioridad_alta: int = Field(..., description="Número de requisitos de prioridad alta")
    prioridad_media: int = Field(..., description="Número de requisitos de prioridad media")
    prioridad_baja: int = Field(..., description="Número de requisitos de prioridad baja")

class RequirementsData(BaseModel):
    """Estructura completa de requisitos generados"""
    requisitos: List[RequirementData] = Field(..., description="Lista de requisitos No Funcionales")
    resumen: RequirementsResumen = Field(..., description="Resumen estadístico de requisitos")
    error: Optional[str] = Field(None, description="Mensaje de error si la generación falló")
    raw_response: Optional[str] = Field(None, description="Respuesta cruda del modelo si hubo error de parseo")

class ScrapingResponse(BaseModel):
    success: bool = Field(..., description="Indica si la operación fue exitosa")
    app_id: str = Field(..., description="ID de la aplicación scrapeada")
    total_reviews: int = Field(..., description="Total de comentarios negativos encontrados")
    reviews: List[ReviewData] = Field(..., description="Lista de comentarios negativos")
    stats: dict = Field(..., description="Estadísticas del proceso de scraping")
    requirements: Optional[RequirementsData] = Field(None, description="Requisitos No Funcionales generados (opcional)")

# ===== Schemas para clasificación de comentario individual =====

class SingleCommentRequest(BaseModel):
    """Request para clasificar un solo comentario"""
    comentario: str = Field(..., description="Texto del comentario a clasificar")
    calificacion: int = Field(default=1, description="Calificación en estrellas (1-5)", ge=1, le=5)
    multiclass_model: Optional[MulticlassModelEnum] = Field(
        default=MulticlassModelEnum.BETO,
        description="Modelo multiclase a utilizar para clasificación ISO 25010 (beto o robertuito)"
    )

    @validator('comentario')
    def validate_comentario(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('El comentario no puede estar vacío')
        if len(v.strip()) < 10:
            raise ValueError('El comentario debe tener al menos 10 caracteres')
        return v.strip()

class SingleCommentResponse(BaseModel):
    """Response para clasificación de comentario individual"""
    success: bool = Field(..., description="Indica si la operación fue exitosa")
    es_relevante: bool = Field(..., description="Indica si el comentario es relevante según el filtro binario")
    mensaje: str = Field(..., description="Mensaje descriptivo del resultado")
    comentario: str = Field(..., description="Comentario procesado")
    calificacion: int = Field(..., description="Calificación del comentario")

    # Campos opcionales (solo si es relevante)
    categoria: Optional[str] = Field(None, description="Categoría ISO 25010 asignada")
    confianza: Optional[float] = Field(None, description="Nivel de confianza de la clasificación (0.0 - 1.0)")
    requisito: Optional[RequirementData] = Field(None, description="Requisito No Funcional generado")

    # Campo opcional para errores
    error: Optional[str] = Field(None, description="Mensaje de error si algo falló")

# ===== Schemas para generación de PDF =====

class PDFGenerationRequest(BaseModel):
    """Request para generar PDF de requisitos"""
    app_id: str = Field(..., description="ID de la aplicación (ej: com.example.app)")
    fecha_generacion: str = Field(..., description="Fecha de generación en formato ISO (ej: 2025-10-22T10:30:00)")
    total_comentarios_analizados: int = Field(..., description="Total de comentarios analizados en el proceso")
    requisitos: List[RequirementData] = Field(..., description="Lista de requisitos No Funcionales")
    resumen: RequirementsResumen = Field(..., description="Resumen estadístico de requisitos")

    @validator('app_id')
    def validate_app_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('El app_id no puede estar vacío')
        return v.strip()

    @validator('requisitos')
    def validate_requisitos(cls, v):
        if len(v) == 0:
            raise ValueError('Debe haber al menos un requisito para generar el PDF')
        return v