from google_play_scraper import reviews, Sort
import time
from typing import List, Dict, Any
from ..schemas.scraping_schemas import ReviewData, CriteriosBusqueda

class PlayStoreScraper:
    def __init__(self):
        self.max_intentos_por_criterio = 10  # Hasta 10 páginas (1000 comentarios potenciales)
        self.reviews_por_request = 100  # 100 comentarios por request
        self.pausa_entre_requests = 2  # segundos

    def _map_criterio_to_sort(self, criterio: CriteriosBusqueda) -> Sort:
        """
        Mapea el criterio de búsqueda a Sort de google-play-scraper.

            criterio: Criterio de búsqueda ('recientes' o 'relevantes')

        Returns:
            Sort correspondiente
        """
        if criterio == CriteriosBusqueda.RECIENTES:
            return Sort.NEWEST
        elif criterio == CriteriosBusqueda.RELEVANTES:
            return Sort.MOST_RELEVANT
        else:
            # Fallback a más recientes
            return Sort.NEWEST

    def scrape_negative_reviews(
        self,
        app_id: str,
        num_comentarios_negativos: int = 9000,
        filtro_estrellas: int = 3,
        criterio_busqueda: CriteriosBusqueda = CriteriosBusqueda.RECIENTES,
        lang: str = 'es',
        country: str = 'pe'
    ) -> Dict[str, Any]:
        """
        Extrae comentarios negativos de Google Play Store según criterio de búsqueda.

        Args:
            app_id: ID de la aplicación (ej: com.bcp.bank.bcp)
            num_comentarios_negativos: Número máximo de comentarios a extraer
            filtro_estrellas: Calificación máxima a filtrar (≤ este valor)
            criterio_busqueda: Criterio de ordenamiento ('recientes' o 'relevantes')
            lang: Idioma de los comentarios
            country: País de origen

        Returns:
            Dict con los comentarios extraídos y estadísticas
        """
        # Mapear criterio de búsqueda a Sort
        sort_criterio = self._map_criterio_to_sort(criterio_busqueda)
        criterio_nombre = "MÁS RECIENTES" if criterio_busqueda == CriteriosBusqueda.RECIENTES else "MÁS RELEVANTES"

        # Variables de control
        comentarios_negativos_filtrados = []
        ids_unicos = set()  # Para evitar duplicados
        total_comentarios_revisados = 0
        duplicados_evitados = 0

        print(f"🎯 Extrayendo {num_comentarios_negativos} comentarios negativos (≤ {filtro_estrellas}⭐)")
        print(f"🏦 App: {app_id}")
        print(f"📅 Criterio: {criterio_nombre}\n")

        # Extracción con criterio seleccionado
        criterios_busqueda_lista = [sort_criterio]
        for criterio in criterios_busqueda_lista:
            if len(comentarios_negativos_filtrados) >= num_comentarios_negativos:
                break

            print(f"🔄 Procesando criterio: {criterio_nombre}")
            
            continuation_token = None
            intentos_criterio = 0
            negativos_este_criterio = 0
            
            # Bucle de paginación
            while (len(comentarios_negativos_filtrados) < num_comentarios_negativos and 
                   intentos_criterio < self.max_intentos_por_criterio):
                
                try:
                    # Extracción de comentarios
                    result, continuation_token = reviews(
                        app_id,
                        lang=lang,
                        country=country,
                        sort=criterio,
                        count=self.reviews_por_request,
                        continuation_token=continuation_token
                    )
                    
                    # Si no hay resultados, salir
                    if not result:
                        print("⚠️ No hay más comentarios disponibles")
                        break
                    
                    # Contar negativos en este lote
                    negativos_lote = sum(1 for r in result if r['score'] <= filtro_estrellas)
                    
                    print(f"📦 Lote {intentos_criterio + 1}: "
                          f"{len(result)} recibidos, {negativos_lote} negativos")
                    
                    # Filtrado de comentarios negativos
                    for review in result:
                        total_comentarios_revisados += 1
                        
                        # Filtro: Solo comentarios ≤ filtro_estrellas
                        if review['score'] <= filtro_estrellas:
                            review_id_original = review['reviewId']
                            
                            # Evitar duplicados
                            if review_id_original not in ids_unicos:
                                ids_unicos.add(review_id_original)
                                
                                # Almacenar comentario
                                comentarios_negativos_filtrados.append({
                                    'id_original': review_id_original,
                                    'comentario': review['content'] or '',
                                    'calificacion': review['score'],
                                    'fecha': review['at'].strftime('%Y-%m-%d'),
                                    'usuario': review['userName'] or 'Usuario anónimo'
                                })
                                negativos_este_criterio += 1
                            else:
                                duplicados_evitados += 1
                    
                    print(f"✅ Acumulados: {len(comentarios_negativos_filtrados)}/{num_comentarios_negativos}")
                    
                    # Pausa para evitar bloqueos
                    time.sleep(self.pausa_entre_requests)
                    intentos_criterio += 1
                    
                    # Si no hay más páginas, salir
                    if not continuation_token:
                        print("✅ No hay más comentarios disponibles")
                        break
                        
                except Exception as e:
                    print(f"❌ Error en lote {intentos_criterio + 1}: {e}")
                    time.sleep(5)
                    break
            
            print(f"📊 Páginas procesadas: {intentos_criterio}, "
                  f"Negativos únicos: {negativos_este_criterio}")
        
        # Limitar a objetivo
        if len(comentarios_negativos_filtrados) > num_comentarios_negativos:
            comentarios_negativos_filtrados = comentarios_negativos_filtrados[:num_comentarios_negativos]
        
        # Estadísticas finales
        stats = {
            'total_comentarios_revisados': total_comentarios_revisados,
            'duplicados_evitados': duplicados_evitados,
            'paginas_procesadas': intentos_criterio,
            'filtro_estrellas': filtro_estrellas,
            'criterio_busqueda': criterio_busqueda.value,  # 'recientes' o 'relevantes'
            'pais': country,
            'idioma': lang
        }
        
        print(f"🎉 Extracción completada: {len(comentarios_negativos_filtrados)} comentarios únicos")
        
        return {
            'reviews': comentarios_negativos_filtrados,
            'stats': stats,
            'total_found': len(comentarios_negativos_filtrados)
        }