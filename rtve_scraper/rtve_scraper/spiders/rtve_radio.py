import scrapy
import json
import logging
from scrapy.spiders import Spider

class RtveRadioSpider(Spider):
    """
    Spider para extraer información de los programas de radio de RTVE.
    
    Attributes:
        name (str): Nombre identificador del spider
        allowed_domains (list): Dominios permitidos para el crawling
    """
    
    name = "rtve_radio"
    allowed_domains = ["rtve.es", "api.rtve.es"]
    
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'ROBOTSTXT_OBEY': False,
        'DOWNLOAD_DELAY': 1,
    }
    
    def start_requests(self):
        """
        Método para iniciar las peticiones a la API
        """
        headers = {
            'Accept': 'application/json',
            'Accept-Language': 'es-ES,es;q=0.9',
            'Origin': 'https://www.rtve.es',
            'Referer': 'https://www.rtve.es/play/radio/',
        }
        
        # URL de la API para obtener programas de Radio Nacional
        api_url = "https://api.rtve.es/api/programas/radio/rne/todos"
        
        yield scrapy.Request(
            url=api_url,
            headers=headers,
            callback=self.parse_api
        )
    
    def parse_api(self, response):
        """
        Método para parsear la respuesta de la API
        
        Args:
            response: Objeto response de Scrapy
            
        Yields:
            dict: Diccionario con la información de cada programa
        """
        self.logger.info(f'Parseando URL API: {response.url}')
        self.logger.info(f'Status: {response.status}')
        
        try:
            data = json.loads(response.text)
            self.logger.info(f'Datos recibidos: {len(data)} bytes')
            
            if 'page' in data and 'items' in data['page']:
                programas = data['page']['items']
                self.logger.info(f'Encontrados {len(programas)} programas')
                
                for programa in programas:
                    yield {
                        'titulo': programa.get('name', ''),
                        'descripcion': programa.get('description', ''),
                        'url': f"https://www.rtve.es/play/radio/{programa.get('uri', '')}",
                        'imagen': programa.get('image', {}).get('url', '') if programa.get('image') else None
                    }
            else:
                self.logger.warning('Estructura de datos inesperada en la respuesta')
                
        except json.JSONDecodeError:
            self.logger.error('Error al decodificar JSON de la respuesta')
            self.logger.debug(f'Contenido de la respuesta: {response.text[:500]}...')
