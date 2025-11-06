from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.schemas.scraping_schemas import (
    ScrapingRequest, ScrapingResponse, ReviewData, RequirementsData,
    SingleCommentRequest, SingleCommentResponse, RequirementData,
    PDFGenerationRequest
)
from app.services.scraping_service import PlayStoreScraper
from app.services.bert_classifier_service import get_bert_classifier
from app.services.openrouter_service import get_requirements_generator
from app.services.pdf_generator_service import get_pdf_generator
import io

router = APIRouter()

@router.post("/scrape", response_model=ScrapingResponse)
async def scrape_playstore_reviews(payload: ScrapingRequest):
    """
    Endpoint para extraer, clasificar comentarios y generar requisitos No Funcionales.

    Proceso:
    1. Extrae comentarios negativos de Play Store
    2. Filtra comentarios relevantes usando modelo BERT binario
    3. Clasifica comentarios relevantes usando modelo BERT multiclase (ISO 25010)
    4. Genera requisitos No Funcionales usando Mistral (OpenRouter)
    5. Retorna comentarios clasificados y requisitos generados
    """
    try:
        # Paso 1: Scraping de comentarios
        print(f"\n{'='*60}")
        print("🚀 INICIANDO PROCESO DE SCRAPING Y CLASIFICACIÓN")
        print(f"{'='*60}")

        scraper = PlayStoreScraper()
        scraping_result = scraper.scrape_negative_reviews(
            app_id=payload.app_id,
            num_comentarios_negativos=payload.max_reviews,
            filtro_estrellas=payload.max_rating,
            criterio_busqueda=payload.criterios_busqueda,
            lang='es',
            country='pe'
        )

        print(f"\n✅ Scraping completado: {scraping_result['total_found']} comentarios extraídos")

        # Paso 2 y 3: Filtrado binario + Clasificación multiclase
        print(f"\n{'='*60}")
        print("🤖 INICIANDO CLASIFICACIÓN CON MODELOS BERT")
        print(f"{'='*60}")

        classifier = get_bert_classifier()
        classified_reviews = classifier.filter_and_classify(
            reviews=scraping_result['reviews'],
            batch_size=32,
            multiclass_model=payload.multiclass_model
        )

        print(f"\n{'='*60}")
        print("✅ CLASIFICACIÓN COMPLETADA")
        print(f"{'='*60}")
        print(f"Total scrapeado: {scraping_result['total_found']}")
        print(f"Total relevante: {len(classified_reviews)}")
        print(f"Tasa de relevancia: {len(classified_reviews)/scraping_result['total_found']*100:.1f}%")
        print(f"{'='*60}\n")

        # Paso 4: Generación de requisitos No Funcionales
        requirements_data = None
        try:
            generator = get_requirements_generator()
            requirements_result = generator.generate_requirements(classified_reviews)

            # Convertir a RequirementsData si la generación fue exitosa
            if requirements_result and 'requisitos' in requirements_result:
                requirements_data = RequirementsData(**requirements_result)

                print(f"\n{'='*60}")
                print("✅ REQUISITOS GENERADOS EXITOSAMENTE")
                print(f"{'='*60}")
                print(f"Total de requisitos: {requirements_data.resumen.total_requisitos}")
                print(f"Por categoría: {requirements_data.resumen.por_categoria}")
                print(f"{'='*60}\n")
        except Exception as e:
            print(f"\n⚠️  Error al generar requisitos: {str(e)}")
            print("Continuando sin requisitos...\n")

        # Convertir a ReviewData
        reviews_data = [ReviewData(**r) for r in classified_reviews]

        # Actualizar estadísticas
        stats = scraping_result['stats'].copy()
        stats['comentarios_antes_filtro'] = scraping_result['total_found']
        stats['comentarios_relevantes'] = len(classified_reviews)
        stats['tasa_relevancia'] = round(len(classified_reviews) / scraping_result['total_found'], 4) if scraping_result['total_found'] > 0 else 0

        # Agregar distribución de categorías
        category_distribution = {}
        for review in classified_reviews:
            cat = review['categoria']
            category_distribution[cat] = category_distribution.get(cat, 0) + 1
        stats['distribucion_categorias'] = category_distribution

        print(f"\n{'='*60}")
        print("✅ PROCESO COMPLETO FINALIZADO")
        print(f"{'='*60}\n")

        return ScrapingResponse(
            success=True,
            app_id=payload.app_id,
            total_reviews=len(classified_reviews),
            reviews=reviews_data,
            stats=stats,
            requirements=requirements_data
        )
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/classify-single", response_model=SingleCommentResponse)
async def classify_single_comment(payload: SingleCommentRequest):
    """
    Endpoint para clasificar un solo comentario y generar un requisito si es relevante.

    Proceso:
    1. Recibe un comentario individual
    2. Aplica filtro binario (relevante vs no relevante)
    3. Si es NO relevante → Retorna mensaje específico
    4. Si es relevante → Aplica clasificación multiclase (ISO 25010)
    5. Si es relevante → Genera requisito No Funcional con Mistral
    6. Retorna resultado completo
    """
    try:
        print(f"\n{'='*60}")
        print("🔍 CLASIFICACIÓN DE COMENTARIO INDIVIDUAL")
        print(f"{'='*60}")
        print(f"Comentario: \"{payload.comentario[:80]}...\"" if len(payload.comentario) > 80 else f"Comentario: \"{payload.comentario}\"")
        print(f"Calificación: {payload.calificacion}★")

        # Paso 1: Obtener el clasificador
        classifier = get_bert_classifier()

        # Paso 2: Aplicar filtro binario
        print(f"\n{'='*60}")
        print("🤖 APLICANDO FILTRO BINARIO (Relevancia)")
        print(f"{'='*60}")

        is_relevant_list = classifier.classify_binary([payload.comentario])
        is_relevant = is_relevant_list[0]

        print(f"Resultado: {'✅ RELEVANTE' if is_relevant else '❌ NO RELEVANTE'}")

        # Paso 3: Si NO es relevante, retornar mensaje específico
        if not is_relevant:
            print(f"\n{'='*60}")
            print("⚠️  COMENTARIO NO RELEVANTE - Proceso finalizado")
            print(f"{'='*60}\n")

            return SingleCommentResponse(
                success=True,
                es_relevante=False,
                mensaje="El comentario no fue clasificado como relevante para requisitos de seguridad según ISO 25010. No se generó ningún requisito.",
                comentario=payload.comentario,
                calificacion=payload.calificacion
            )

        # Paso 4: Si ES relevante, aplicar clasificación multiclase
        print(f"\n{'='*60}")
        print("🤖 APLICANDO CLASIFICACIÓN MULTICLASE (ISO 25010)")
        print(f"{'='*60}")

        classification_result = classifier.classify_multiclass(
            [payload.comentario],
            model_name=payload.multiclass_model
        )
        categoria, confianza = classification_result[0]

        print(f"Categoría: {categoria}")
        print(f"Confianza: {confianza:.4f}")

        # Paso 5: Generar requisito No Funcional
        requisito_data = None
        error_message = None

        try:
            generator = get_requirements_generator()
            requisito_result = generator.generate_single_requirement(
                comentario=payload.comentario,
                categoria=categoria,
                confianza=confianza,
                calificacion=payload.calificacion
            )

            # Verificar si hubo error
            if 'error' in requisito_result:
                error_message = requisito_result.get('error', 'Error desconocido al generar requisito')
                print(f"⚠️  {error_message}")
            else:
                # Convertir a RequirementData
                requisito_data = RequirementData(**requisito_result)
                print(f"✅ Requisito generado exitosamente")

        except Exception as e:
            error_message = f"Error al generar requisito: {str(e)}"
            print(f"❌ {error_message}")

        print(f"\n{'='*60}")
        print("✅ PROCESO COMPLETADO")
        print(f"{'='*60}\n")

        # Retornar respuesta completa
        return SingleCommentResponse(
            success=True,
            es_relevante=True,
            mensaje=f"Comentario clasificado como relevante en la categoría '{categoria}' con {confianza:.2%} de confianza.",
            comentario=payload.comentario,
            calificacion=payload.calificacion,
            categoria=categoria,
            confianza=round(confianza, 4),
            requisito=requisito_data,
            error=error_message
        )

    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-pdf")
async def generate_requirements_pdf(payload: PDFGenerationRequest):
    """
    Endpoint para generar un PDF de requisitos No Funcionales.

    Este endpoint recibe los datos de requisitos que el frontend ya obtuvo
    del endpoint /scrape y genera un documento PDF profesional descargable.

    Flujo:
    1. Frontend hace scraping → obtiene requirements
    2. Frontend guarda requirements en estado
    3. Usuario hace clic en "Descargar PDF"
    4. Frontend envía requirements a este endpoint
    5. Backend genera PDF y lo retorna
    6. Frontend descarga automáticamente el archivo

    Args:
        payload: PDFGenerationRequest con app_id, fecha_generacion,
                 total_comentarios_analizados, requisitos y resumen

    Returns:
        StreamingResponse con el PDF generado (application/pdf)
    """
    try:
        print(f"\n{'='*60}")
        print("📄 GENERANDO PDF DE REQUISITOS")
        print(f"{'='*60}")
        print(f"App ID: {payload.app_id}")
        print(f"Total de requisitos: {len(payload.requisitos)}")
        print(f"Comentarios analizados: {payload.total_comentarios_analizados}")

        # Convertir el payload a diccionario
        requirements_data = {
            "app_id": payload.app_id,
            "fecha_generacion": payload.fecha_generacion,
            "total_comentarios_analizados": payload.total_comentarios_analizados,
            "requisitos": [req.dict() for req in payload.requisitos],
            "resumen": payload.resumen.dict()
        }

        # Generar el PDF
        pdf_generator = get_pdf_generator()
        pdf_bytes = pdf_generator.generate_pdf(requirements_data)

        print(f"✅ PDF generado exitosamente ({len(pdf_bytes)} bytes)")
        print(f"{'='*60}\n")

        # Crear nombre de archivo
        filename = f"requisitos_{payload.app_id}.pdf"

        # Retornar el PDF como respuesta descargable
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except Exception as e:
        print(f"\n❌ ERROR al generar PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al generar PDF: {str(e)}")
