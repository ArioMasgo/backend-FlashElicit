"""
Servicio para generar PDFs de requisitos No Funcionales.

Este servicio recibe los datos de requisitos y genera un documento PDF
profesional con formato estructurado.
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.platypus import Image as RLImage
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from io import BytesIO
from datetime import datetime
from typing import Dict, Any


class RequirementsPDFGenerator:
    """Generador de PDFs para requisitos No Funcionales."""

    # Mapeo de categorías ISO 25010 a descripciones
    CATEGORIAS_ISO = {
        "autenticidad": "Seguridad - Autenticidad",
        "confidencialidad": "Seguridad - Confidencialidad",
        "integridad": "Seguridad - Integridad",
        "no_repudio": "Seguridad - No Repudio",
        "resistencia": "Seguridad - Resistencia",
        "responsabilidad": "Seguridad - Responsabilidad"
    }

    # Colores para prioridades
    PRIORIDAD_COLORS = {
        "Alta": colors.HexColor("#EF4444"),      # Rojo
        "Media": colors.HexColor("#F59E0B"),     # Naranja
        "Baja": colors.HexColor("#10B981")       # Verde
    }

    def __init__(self):
        """Inicializa el generador de PDF."""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Configura estilos personalizados para el PDF."""

        # Estilo para el título principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor("#1F2937"),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Estilo para subtítulos
        self.styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor("#374151"),
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))

        # Estilo para el cuerpo de texto
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            textColor=colors.HexColor("#1F2937"),
            alignment=TA_JUSTIFY,
            spaceAfter=12
        ))

        # Estilo para metadatos
        self.styles.add(ParagraphStyle(
            name='Metadata',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor("#6B7280"),
            alignment=TA_CENTER,
            spaceAfter=6
        ))

    def generate_pdf(self, requirements_data: Dict[str, Any]) -> bytes:
        """
        Genera un PDF a partir de los datos de requisitos.

        Args:
            requirements_data: Diccionario con la estructura:
                - app_id: str
                - fecha_generacion: str
                - total_comentarios_analizados: int
                - requisitos: List[RequirementData]
                - resumen: RequirementsResumen

        Returns:
            bytes: Buffer con el contenido del PDF
        """
        buffer = BytesIO()

        # Crear documento con márgenes
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
        )

        # Construir el contenido del PDF
        story = []

        # 1. Portada
        story.extend(self._build_cover_page(requirements_data))
        story.append(PageBreak())

        # 2. Resumen Ejecutivo
        story.extend(self._build_executive_summary(requirements_data))
        story.append(Spacer(1, 0.3 * inch))

        # 3. Lista de Requisitos
        story.extend(self._build_requirements_list(requirements_data))

        # 4. Apéndice (opcional)
        story.append(PageBreak())
        story.extend(self._build_appendix(requirements_data))

        # Generar PDF
        doc.build(story)

        # Retornar bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()

        return pdf_bytes

    def _build_cover_page(self, data: Dict[str, Any]) -> list:
        """Construye la portada del documento."""
        elements = []

        # Espaciado superior
        elements.append(Spacer(1, 1.5 * inch))

        # Título principal
        title = Paragraph(
            "Requisitos No Funcionales<br/>Generados Automáticamente",
            self.styles['CustomTitle']
        )
        elements.append(title)
        elements.append(Spacer(1, 0.5 * inch))

        # Información de la aplicación
        app_id = data.get('app_id', 'N/A')
        elements.append(Paragraph(
            f"<b>Aplicación:</b> {app_id}",
            self.styles['Metadata']
        ))

        # Fecha de generación
        fecha = data.get('fecha_generacion', datetime.now().isoformat())
        try:
            fecha_obj = datetime.fromisoformat(fecha.replace('Z', '+00:00'))
            fecha_formateada = fecha_obj.strftime("%d de %B de %Y, %H:%M")
        except:
            fecha_formateada = fecha

        elements.append(Paragraph(
            f"<b>Fecha de generación:</b> {fecha_formateada}",
            self.styles['Metadata']
        ))

        # Total de comentarios analizados
        total_comentarios = data.get('total_comentarios_analizados', 0)
        elements.append(Paragraph(
            f"<b>Comentarios analizados:</b> {total_comentarios}",
            self.styles['Metadata']
        ))

        # Herramienta
        elements.append(Spacer(1, 1 * inch))
        elements.append(Paragraph(
            "Generado por <b>Flash Elicit</b>",
            self.styles['Metadata']
        ))
        elements.append(Paragraph(
            "Sistema de Elicitación de Requisitos basado en ISO 25010",
            self.styles['Metadata']
        ))

        return elements

    def _build_executive_summary(self, data: Dict[str, Any]) -> list:
        """Construye el resumen ejecutivo."""
        elements = []

        elements.append(Paragraph(
            "Resumen Ejecutivo",
            self.styles['CustomHeading2']
        ))

        resumen = data.get('resumen', {})
        requisitos = data.get('requisitos', [])

        # Información general
        total_requisitos = resumen.get('total_requisitos', len(requisitos))

        summary_text = f"""
        Este documento presenta <b>{total_requisitos} requisitos No Funcionales</b>
        generados automáticamente a partir del análisis de comentarios negativos de usuarios
        en Google Play Store. Los requisitos se clasifican según las categorías de seguridad
        de la norma ISO 25010.
        """
        elements.append(Paragraph(summary_text, self.styles['CustomBody']))
        elements.append(Spacer(1, 0.2 * inch))

        # Tabla de distribución por categoría
        elements.append(Paragraph(
            "Distribución por Categoría ISO 25010",
            self.styles['Heading3']
        ))

        por_categoria = resumen.get('por_categoria', {})
        if por_categoria:
            categoria_data = [['Categoría', 'Cantidad', 'Porcentaje']]

            for categoria, cantidad in sorted(por_categoria.items(), key=lambda x: x[1], reverse=True):
                porcentaje = (cantidad / total_requisitos * 100) if total_requisitos > 0 else 0
                categoria_nombre = self.CATEGORIAS_ISO.get(categoria, categoria.title())
                categoria_data.append([
                    categoria_nombre,
                    str(cantidad),
                    f"{porcentaje:.1f}%"
                ])

            categoria_table = Table(categoria_data, colWidths=[3.5 * inch, 1 * inch, 1.2 * inch])
            categoria_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#3B82F6")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F4F6")]),
            ]))
            elements.append(categoria_table)
            elements.append(Spacer(1, 0.2 * inch))

        # Tabla de distribución por prioridad
        elements.append(Paragraph(
            "Distribución por Prioridad",
            self.styles['Heading3']
        ))

        prioridad_data = [['Prioridad', 'Cantidad', 'Porcentaje']]

        prioridades = {
            'Alta': resumen.get('prioridad_alta', 0),
            'Media': resumen.get('prioridad_media', 0),
            'Baja': resumen.get('prioridad_baja', 0)
        }

        for prioridad, cantidad in prioridades.items():
            porcentaje = (cantidad / total_requisitos * 100) if total_requisitos > 0 else 0
            prioridad_data.append([
                prioridad,
                str(cantidad),
                f"{porcentaje:.1f}%"
            ])

        prioridad_table = Table(prioridad_data, colWidths=[2 * inch, 1.5 * inch, 1.5 * inch])
        prioridad_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#3B82F6")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F4F6")]),
        ]))
        elements.append(prioridad_table)

        return elements

    def _build_requirements_list(self, data: Dict[str, Any]) -> list:
        """Construye la lista detallada de requisitos."""
        elements = []

        elements.append(PageBreak())
        elements.append(Paragraph(
            "Lista de Requisitos No Funcionales",
            self.styles['CustomHeading2']
        ))
        elements.append(Spacer(1, 0.2 * inch))

        requisitos = data.get('requisitos', [])

        for idx, req in enumerate(requisitos):
            # Separador entre requisitos
            if idx > 0:
                elements.append(Spacer(1, 0.3 * inch))

            # ID del requisito
            req_id = req.get('id', f'NFR-{idx + 1:03d}')
            categoria = req.get('categoria', 'N/A')
            categoria_nombre = self.CATEGORIAS_ISO.get(categoria, categoria.title())
            prioridad = req.get('prioridad', 'Media')

            # Encabezado del requisito con color según prioridad
            prioridad_color = self.PRIORIDAD_COLORS.get(prioridad, colors.grey)

            header_text = f"""
            <b><font size="14" color="#1F2937">{req_id}</font></b> -
            <font color="#6B7280">{categoria_nombre}</font> -
            <font color="{prioridad_color.hexval()}">Prioridad {prioridad}</font>
            """
            elements.append(Paragraph(header_text, self.styles['CustomBody']))
            elements.append(Spacer(1, 0.1 * inch))

            # Descripción del requisito
            requisito_text = req.get('requisito', 'N/A')
            elements.append(Paragraph(
                f"<b>Requisito:</b> {requisito_text}",
                self.styles['CustomBody']
            ))

            # Justificación
            justificacion = req.get('justificacion', 'N/A')
            elements.append(Paragraph(
                f"<b>Justificación:</b> {justificacion}",
                self.styles['CustomBody']
            ))

            # Criterios de aceptación
            criterios = req.get('criterios_aceptacion', [])
            if criterios:
                elements.append(Paragraph(
                    "<b>Criterios de Aceptación:</b>",
                    self.styles['CustomBody']
                ))

                criterios_list = "<br/>".join([f"• {criterio}" for criterio in criterios])
                elements.append(Paragraph(criterios_list, self.styles['CustomBody']))

            # Comentarios relacionados
            comentarios_relacionados = req.get('comentarios_relacionados', 0)
            elements.append(Paragraph(
                f"<b>Basado en:</b> {comentarios_relacionados} comentarios de usuarios",
                self.styles['CustomBody']
            ))

            # Línea separadora
            elements.append(Spacer(1, 0.1 * inch))
            line_data = [['', '']]
            line_table = Table(line_data, colWidths=[6 * inch])
            line_table.setStyle(TableStyle([
                ('LINEABOVE', (0, 0), (-1, 0), 1, colors.HexColor("#E5E7EB")),
            ]))
            elements.append(line_table)

        return elements

    def _build_appendix(self, data: Dict[str, Any]) -> list:
        """Construye el apéndice con información metodológica."""
        elements = []

        elements.append(Paragraph(
            "Apéndice: Metodología",
            self.styles['CustomHeading2']
        ))

        methodology_text = """
        <b>Proceso de Generación de Requisitos</b><br/><br/>

        Los requisitos No Funcionales presentados en este documento fueron generados
        automáticamente mediante el siguiente proceso:<br/><br/>

        <b>1. Extracción de Comentarios:</b> Se recopilaron comentarios negativos
        (≤ 3 estrellas) de Google Play Store.<br/><br/>

        <b>2. Filtrado Binario:</b> Se utilizó un modelo BERT entrenado en español
        (dccuchile/bert-base-spanish-wwm-uncased) para filtrar comentarios relevantes
        para seguridad.<br/><br/>

        <b>3. Clasificación Multiclase:</b> Los comentarios relevantes se clasificaron
        en 6 categorías de seguridad según ISO 25010:
        <br/>• Autenticidad
        <br/>• Confidencialidad
        <br/>• Integridad
        <br/>• No Repudio
        <br/>• Resistencia
        <br/>• Responsabilidad<br/><br/>

        <b>4. Generación de Requisitos:</b> Se utilizó el modelo Mistral Small
        (vía OpenRouter) para sintetizar los comentarios clasificados en requisitos
        No Funcionales específicos, medibles y accionables.<br/><br/>

        <b>Categorías ISO 25010</b><br/><br/>

        <b>Autenticidad:</b> Verificación de identidad de usuarios y sistemas.<br/>
        <b>Confidencialidad:</b> Protección de datos contra acceso no autorizado.<br/>
        <b>Integridad:</b> Prevención de modificación no autorizada de datos.<br/>
        <b>No Repudio:</b> Trazabilidad de acciones y transacciones.<br/>
        <b>Resistencia:</b> Disponibilidad y robustez ante fallos.<br/>
        <b>Responsabilidad:</b> Auditoría y rendición de cuentas.<br/><br/>

        <b>Nota:</b> Estos requisitos deben ser revisados y refinados por expertos
        en el dominio antes de su implementación.
        """

        elements.append(Paragraph(methodology_text, self.styles['CustomBody']))

        # Información de generación
        elements.append(Spacer(1, 0.3 * inch))
        elements.append(Paragraph(
            "_______________________________________________________________",
            self.styles['Metadata']
        ))
        elements.append(Paragraph(
            "Documento generado por Flash Elicit - Sistema de Elicitación de Requisitos",
            self.styles['Metadata']
        ))
        elements.append(Paragraph(
            f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            self.styles['Metadata']
        ))

        return elements


# Instancia singleton del generador
_pdf_generator_instance = None

def get_pdf_generator() -> RequirementsPDFGenerator:
    """Retorna la instancia singleton del generador de PDF."""
    global _pdf_generator_instance
    if _pdf_generator_instance is None:
        _pdf_generator_instance = RequirementsPDFGenerator()
    return _pdf_generator_instance
