from openai import OpenAI
from typing import List, Dict
import os
import json

class OpenRouterRequirementsGenerator:
    """
    Servicio para generar requisitos No Funcionales usando OpenRouter/Mistral.

    Utiliza el modelo Mistral Small para elicitar requisitos No Funcionales
    basándose en comentarios de usuarios clasificados por categorías ISO 25010.
    """

    def __init__(self):
        """Inicializa el cliente de OpenRouter."""
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
        self.model = "x-ai/grok-4-fast"

    def _create_prompt(self, comentarios_clasificados: List[Dict]) -> str:
        """
        Crea el prompt para generar requisitos No Funcionales.

        Args:
            comentarios_clasificados: Lista de comentarios con su categoría ISO 25010

        Returns:
            Prompt formateado para el modelo
        """
        # Agrupar comentarios por categoría
        comentarios_por_categoria = {}
        for item in comentarios_clasificados:
            categoria = item['categoria']
            if categoria not in comentarios_por_categoria:
                comentarios_por_categoria[categoria] = []
            comentarios_por_categoria[categoria].append({
                'comentario': item['comentario'],
                'confianza': item['confianza'],
                'calificacion': item['calificacion']
            })

        # Construir el prompt
        prompt = """Eres un experto en ingeniería de requisitos especializado en requisitos No Funcionales (NFR) basados en ISO 25010 y experto en la norma ISO/IEC/IEEE 29148 y en redacción de Requisitos No Funcionales (RNF) claros, verificables y medibles.

Tu tarea es analizar comentarios de usuarios de una aplicación móvil que han sido clasificados en categorías de seguridad según ISO 25010, y generar requisitos No Funcionales específicos, medibles y accionables.

**Categorías ISO 25010 de Seguridad:**
- autenticidad: Verificación de identidad y autenticación
- confidencialidad: Privacidad y protección de datos
- integridad: Prevención de corrupción o modificación no autorizada de datos
- no_repudio: Trazabilidad y responsabilidad de acciones
- resistencia: Disponibilidad y robustez del sistema
- responsabilidad: Auditoría y rendición de cuentas

**Comentarios clasificados por categoría:**

"""

        for categoria, comentarios in comentarios_por_categoria.items():
            prompt += f"\n### {categoria.upper()} ({len(comentarios)} comentarios)\n"
            for i, item in enumerate(comentarios, 1):
                prompt += f"{i}. \"{item['comentario']}\" (Confianza: {item['confianza']:.2f}, Rating: {item['calificacion']}★)\n"

        prompt += """

**Instrucciones:**

Analiza los comentarios y genera requisitos No Funcionales siguiendo estos principios:

1. **CANTIDAD DE REQUISITOS:** Decide tú mismo cuántos requisitos generar basándote en:
   - La cantidad de problemas únicos identificados
   - La diversidad de temas mencionados
   - La severidad de los problemas reportados
   - Agrupa comentarios similares, pero crea requisitos separados si abordan problemas diferentes

2. **GRANULARIDAD:** 
   - Si múltiples comentarios mencionan el MISMO problema específico → Crea 1 requisito
   - Si los comentarios mencionan problemas RELACIONADOS pero DIFERENTES → Crea requisitos separados
   - NO fuerces un número mínimo o máximo, genera los que sean necesarios

3. **PRIORIDAD (DINÁMICA):**
   Asigna prioridad de forma RELATIVA basándote en:
   
   - **Alta**: Requisitos que agrupan la MAYOR cantidad de comentarios relacionados en tu análisis
   - **Media**: Requisitos con cantidad MODERADA de comentarios relacionados
   - **Baja**: Requisitos con MENOR cantidad de comentarios relacionados
   **IMPORTANTE:** La prioridad es RELATIVA al conjunto de datos que estás analizando.

4. **REDACCIÓN SEGÚN ISO/IEC/IEEE 29148 (OBLIGATORIO):**

   Cada requisito DEBE seguir esta estructura sintáctica:
   
   ✅ **Fórmula:** [Artefacto técnico específico] + DEBERÁ + [restricción/condición técnica] + [métrica cuantificable]
   
   **Reglas obligatorias:**
   
   a) **Usar SIEMPRE el verbo modal "deberá"** (no "debe", "debería", "podría")
      - Define obligatoriedad y verificabilidad
   
   b) **Identificar UN artefacto técnico específico** (no usar "el sistema" genéricamente)
      - ✅ Ejemplos válidos: "El servicio de autenticación", "La pantalla de login", "El módulo de pagos"
      - ❌ Evitar: "El sistema", "La aplicación", "El software"
   
   c) **Incluir métricas CUANTIFICABLES Y OBSERVABLES:**
      - Tiempos: < 2 segundos, < 100 ms, en menos de 3 segundos
      - Porcentajes: 99.9% de disponibilidad, tasa de error < 1%
      - Límites: hasta 1000 usuarios concurrentes, máximo 5 intentos
      - Estándares: WCAG 2.1 AA, ISO 27001, HTTPS/TLS 1.3
      - Frecuencias: durante horario de 8:00-20:00, cada 24 horas
   
   d) **PROHIBIDO usar palabras VAGAS o SUBJETIVAS:**
      - ❌ rápido, lento, fácil, intuitivo, eficiente, óptimo, adecuado, moderno, amigable, robusto
      - ✅ Reemplazar por métricas observables
   
   e) **Criterio SMART obligatorio:**
      - **S**pecífico: Artefacto y contexto definidos
      - **M**edible: Métrica cuantificable incluida
      - **A**lcanzable: Técnicamente posible
      - **R**elevante: Contribuye a la calidad del sistema
      - **T**emporal: Incluir frecuencia, duración o ventana temporal cuando aplique

   **Ejemplos de requisitos CORRECTOS según ISO 29148:**
   
   ✅ "El servicio de autenticación biométrica deberá responder en menos de 2 segundos bajo carga de hasta 500 usuarios concurrentes."
   
   ✅ "La pantalla de consulta de saldo deberá estar disponible el 99.5% del tiempo durante el horario de 8:00 a 20:00."
   
   ✅ "El módulo de recuperación de contraseña deberá enviar el código de verificación en menos de 30 segundos."
   
   ✅ "La interfaz web de transferencias deberá cumplir con el estándar WCAG 2.1 nivel AA para accesibilidad."
   
   **Ejemplos de requisitos INCORRECTOS:**
   
   ❌ "El sistema debe ser rápido" → Vago, sin métrica, sin artefacto específico
   ❌ "La app deberá tener buena seguridad" → Subjetivo, no medible
   ❌ "Debe cargar eficientemente" → Sin sujeto, palabra prohibida, sin métrica
   
5. **CONTEXTO OPERATIVO (cuando aplique):**
   - Especificar condiciones: "bajo carga de X usuarios", "durante horario laboral", "en Chrome/Firefox/Safari"

**Formato de respuesta (JSON):**

```json
{
  "requisitos": [
    {
      "id": "NFR-001",
      "categoria": "autenticidad",
      "requisito": "El servicio de autenticación biométrica deberá validar la identidad del usuario en menos de 2 segundos con una tasa de error menor al 1% bajo carga de hasta 500 usuarios concurrentes.",
      "prioridad": "Alta",
      "justificacion": "45 usuarios reportan problemas con el inicio de sesión por huella digital, siendo el problema más frecuente en esta categoría, con calificaciones promedio de 1.2★",
      "criterios_aceptacion": [
        "El servicio deberá soportar autenticación por huella digital y reconocimiento facial",
        "El tiempo de respuesta deberá ser menor a 2 segundos en el 95% de los casos",
        "El servicio deberá proporcionar fallback a contraseña en caso de fallo biométrico en menos de 1 segundo"
      ],
      "comentarios_relacionados": 45
    }
  ],
  "resumen": {
    "total_requisitos": 0,
    "por_categoria": {},
    "prioridad_alta": 0,
    "prioridad_media": 0,
    "prioridad_baja": 0
  }
}
```

**IMPORTANTE:** 
- Responde ÚNICAMENTE con el JSON, sin texto adicional antes o después.
- TODOS los requisitos y criterios de aceptación DEBEN usar "deberá" y seguir la norma ISO 29148.
- EVITA requisitos vagos, subjetivos o sin métricas cuantificables.
- La prioridad debe ser RELATIVA al dataset actual, no usar límites absolutos.
- Genera tantos requisitos como sean necesarios para cubrir todos los problemas identificados.
"""

        return prompt

    def generate_requirements(
        self,
        comentarios_clasificados: List[Dict],
        max_retries: int = 3
    ) -> Dict:
        """
        Genera requisitos No Funcionales basados en comentarios clasificados.

        Args:
            comentarios_clasificados: Lista de diccionarios con comentarios y su clasificación
            max_retries: Número máximo de reintentos en caso de error

        Returns:
            Diccionario con requisitos generados y resumen

        Raises:
            Exception: Si no se puede generar requisitos después de max_retries intentos
        """
        if not comentarios_clasificados:
            return {
                "requisitos": [],
                "resumen": {
                    "total_requisitos": 0,
                    "por_categoria": {},
                    "prioridad_alta": 0,
                    "prioridad_media": 0,
                    "prioridad_baja": 0
                },
                "error": "No hay comentarios clasificados para procesar"
            }

        print(f"\n{'='*60}")
        print("🧠 GENERANDO REQUISITOS NO FUNCIONALES")
        print(f"{'='*60}")
        print(f"Total de comentarios a procesar: {len(comentarios_clasificados)}")

        prompt = self._create_prompt(comentarios_clasificados)

        for attempt in range(max_retries):
            try:
                print(f"\nIntento {attempt + 1}/{max_retries}...")

                completion = self.client.chat.completions.create(
                    extra_headers={
                        "HTTP-Referer": "https://github.com/yourusername/requirements-elicitation",
                        "X-Title": "Requirements Elicitation System",
                    },
                    extra_body={},
                    model=self.model,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.7,
                    max_tokens=16000  # Aumentado para permitir 50-100+ requisitos detallados
                )

                response_text = completion.choices[0].message.content
                print(f"\n✅ Respuesta recibida del modelo ({len(response_text)} caracteres)")

                # Intentar parsear JSON
                # Remover bloques de código markdown si existen
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0].strip()

                requisitos_data = json.loads(response_text)

                print(f"✅ Requisitos generados exitosamente")
                print(f"   Total: {requisitos_data.get('resumen', {}).get('total_requisitos', 0)} requisitos")

                return requisitos_data

            except json.JSONDecodeError as e:
                print(f"⚠️  Error al parsear JSON (intento {attempt + 1}): {str(e)}")
                if attempt == max_retries - 1:
                    # Último intento, retornar respuesta cruda
                    return {
                        "requisitos": [],
                        "resumen": {
                            "total_requisitos": 0,
                            "por_categoria": {},
                            "prioridad_alta": 0,
                            "prioridad_media": 0,
                            "prioridad_baja": 0
                        },
                        "error": "No se pudo parsear la respuesta del modelo",
                        "raw_response": response_text
                    }
            except Exception as e:
                print(f"❌ Error en intento {attempt + 1}: {str(e)}")
                if attempt == max_retries - 1:
                    raise Exception(f"No se pudieron generar requisitos después de {max_retries} intentos: {str(e)}")

        return {
            "requisitos": [],
            "resumen": {
                "total_requisitos": 0,
                "por_categoria": {},
                "prioridad_alta": 0,
                "prioridad_media": 0,
                "prioridad_baja": 0
            },
            "error": "No se pudieron generar requisitos"
        }

    def _create_single_comment_prompt(self, comentario: str, categoria: str, confianza: float, calificacion: int) -> str:
        """
        Crea el prompt para generar un requisito basado en un solo comentario.

        Args:
            comentario: Texto del comentario
            categoria: Categoría ISO 25010 asignada
            confianza: Nivel de confianza de la clasificación
            calificacion: Calificación en estrellas

        Returns:
            Prompt formateado para el modelo
        """
        # Mapeo de categorías a descripciones
        categorias_info = {
            "autenticidad": "Verificación de identidad y autenticación",
            "confidencialidad": "Privacidad y protección de datos",
            "integridad": "Prevención de corrupción o modificación no autorizada de datos",
            "no_repudio": "Trazabilidad y responsabilidad de acciones",
            "resistencia": "Disponibilidad y robustez del sistema",
            "responsabilidad": "Auditoría y rendición de cuentas"
        }

        categoria_desc = categorias_info.get(categoria, "Seguridad general")

        prompt = f"""Eres un experto en ingeniería de requisitos especializado en requisitos No Funcionales (NFR) basados en ISO 25010.

Tu tarea es analizar UN comentario de usuario de una aplicación móvil que ha sido clasificado en una categoría de seguridad según ISO 25010, y generar UN requisito No Funcional específico, medible y accionable.

**Comentario del usuario:**
- Texto: "{comentario}"
- Calificación: {calificacion}★
- Categoría ISO 25010: {categoria} ({categoria_desc})
- Confianza de clasificación: {confianza:.2f}

**Instrucciones:**

Genera UN requisito No Funcional siguiendo la norma ISO/IEC/IEEE 29148:

1. **REDACCIÓN OBLIGATORIA según ISO 29148:**
   
   ✅ **Fórmula:** [Artefacto técnico específico] + DEBERÁ + [restricción/condición técnica] + [métrica cuantificable]
   
   **Reglas obligatorias:**
   
   a) **Usar SIEMPRE el verbo modal "deberá"** (no "debe", "debería", "podría")
   
   b) **Identificar UN artefacto técnico específico** (no usar "el sistema" genéricamente)
      - ✅ Ejemplos: "El servicio de autenticación", "La pantalla de login", "El módulo de pagos"
      - ❌ Evitar: "El sistema", "La aplicación"
   
   c) **Incluir métricas CUANTIFICABLES:**
      - Tiempos: < 2 segundos, < 100 ms
      - Porcentajes: 99.9% disponibilidad, tasa de error < 1%
      - Límites: hasta 1000 usuarios, máximo 5 intentos
      - Estándares: WCAG 2.1 AA, HTTPS/TLS 1.3
   
   d) **PROHIBIDO usar palabras VAGAS:**
      - ❌ rápido, lento, fácil, intuitivo, eficiente, óptimo, adecuado
      - ✅ Usar métricas observables
   
   e) **Criterio SMART:**
      - Específico, Medible, Alcanzable, Relevante, Temporal

2. **Ejemplos CORRECTOS:**
   ✅ "El servicio de autenticación biométrica deberá responder en menos de 2 segundos bajo carga de 500 usuarios."
   ✅ "El módulo de recuperación de contraseña deberá enviar el código en menos de 30 segundos."

3. **Criterios de aceptación:**
   - TODOS deben usar "deberá" y seguir la misma estructura
   - Deben ser verificables y medibles

**Formato de respuesta (JSON):**

```json
{{
  "id": "NFR-001",
  "categoria": "{categoria}",
  "requisito": "[Artefacto técnico] deberá [acción] [métrica cuantificable]",
  "prioridad": "Alta|Media|Baja",
  "justificacion": "Basado en el comentario del usuario: [explicación del problema identificado]",
  "criterios_aceptacion": [
    "[Artefacto] deberá [criterio medible 1]",
    "[Artefacto] deberá [criterio medible 2]",
    "[Artefacto] deberá [criterio medible 3]"
  ],
  "comentarios_relacionados": 1
}}
```

**IMPORTANTE:**
- Responde ÚNICAMENTE con el JSON, sin texto adicional.
- TODOS los requisitos y criterios DEBEN usar "deberá" y seguir ISO 29148.
- EVITA requisitos vagos, subjetivos o sin métricas cuantificables.
"""

        return prompt

    def generate_single_requirement(
        self,
        comentario: str,
        categoria: str,
        confianza: float,
        calificacion: int = 1,
        max_retries: int = 3
    ) -> Dict:
        """
        Genera UN requisito No Funcional basado en un solo comentario clasificado.

        Args:
            comentario: Texto del comentario
            categoria: Categoría ISO 25010 asignada
            confianza: Nivel de confianza de la clasificación
            calificacion: Calificación en estrellas (1-5)
            max_retries: Número máximo de reintentos en caso de error

        Returns:
            Diccionario con el requisito generado

        Raises:
            Exception: Si no se puede generar el requisito después de max_retries intentos
        """
        print(f"\n{'='*60}")
        print("🧠 GENERANDO REQUISITO PARA COMENTARIO INDIVIDUAL")
        print(f"{'='*60}")
        print(f"Categoría: {categoria} (confianza: {confianza:.2f})")
        print(f"Comentario: \"{comentario[:80]}...\"" if len(comentario) > 80 else f"Comentario: \"{comentario}\"")

        prompt = self._create_single_comment_prompt(comentario, categoria, confianza, calificacion)

        for attempt in range(max_retries):
            try:
                print(f"\nIntento {attempt + 1}/{max_retries}...")

                completion = self.client.chat.completions.create(
                    extra_headers={
                        "HTTP-Referer": "https://github.com/yourusername/requirements-elicitation",
                        "X-Title": "Requirements Elicitation System",
                    },
                    extra_body={},
                    model=self.model,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.7,
                    max_tokens=1000
                )

                response_text = completion.choices[0].message.content
                print(f"✅ Respuesta recibida del modelo ({len(response_text)} caracteres)")

                # Intentar parsear JSON
                # Remover bloques de código markdown si existen
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0].strip()

                requisito_data = json.loads(response_text)

                print(f"✅ Requisito generado exitosamente")
                print(f"   ID: {requisito_data.get('id', 'N/A')}")
                print(f"   Prioridad: {requisito_data.get('prioridad', 'N/A')}")
                print(f"{'='*60}\n")

                return requisito_data

            except json.JSONDecodeError as e:
                print(f"⚠️  Error al parsear JSON (intento {attempt + 1}): {str(e)}")
                if attempt == max_retries - 1:
                    # Último intento, retornar error
                    return {
                        "error": "No se pudo parsear la respuesta del modelo",
                        "raw_response": response_text
                    }
            except Exception as e:
                print(f"❌ Error en intento {attempt + 1}: {str(e)}")
                if attempt == max_retries - 1:
                    raise Exception(f"No se pudo generar el requisito después de {max_retries} intentos: {str(e)}")

        return {
            "error": "No se pudo generar el requisito"
        }


# Singleton para reutilizar el cliente
_generator_instance = None

def get_requirements_generator() -> OpenRouterRequirementsGenerator:
    """
    Obtiene la instancia singleton del generador de requisitos.

    Returns:
        Instancia de OpenRouterRequirementsGenerator
    """
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = OpenRouterRequirementsGenerator()
    return _generator_instance
