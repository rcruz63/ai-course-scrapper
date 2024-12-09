#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Scrapper para el programa Discopolis de RTVE.
Este script extrae información sobre los episodios del programa, incluyendo:
- Fecha de emisión
- URL de streaming
- Temática
- Artistas mencionados
- Descripción completa
- Duración
- Metadata adicional
"""

import scrapy
from scrapy.crawler import CrawlerProcess
from datetime import datetime
import csv
import logging
import sys
import asyncio
import nest_asyncio
import json
import re
from twisted.internet import reactor

class DiscopolisSpider(scrapy.Spider):
    """
    Spider para extraer información del programa Discopolis de RTVE.
    """
    name = 'discopolis'
    start_urls = ['https://www.rtve.es/play/audios/moduloRadio/1936/emisiones']
    
    def parse(self, response):
        """
        Método principal para parsear la página de episodios.
        
        Args:
            response: Respuesta HTTP de la página
            
        Yields:
            dict: Información extraída de cada episodio
        """
        # Extraer los elementos de cada episodio
        episodios = response.css('li.elem_')
        
        for episodio in episodios:
            # Extraer datos del setup
            setup_data = episodio.attrib.get('data-setup', '{}')
            setup_data = eval(setup_data)  # Convertir string a diccionario
            
            # Extraer título
            titulo = episodio.css('span.maintitle::text').get().strip()
            
            # Extraer fecha y duración
            fecha_str = episodio.css('span.datemi::text').get().strip()
            duracion = episodio.css('span.duration::text').get().strip()
            
            # Extraer URL del episodio
            url = episodio.css('a.goto_media::attr(href)').get()
            
            # Extraer ID del asset
            id_asset = setup_data.get('idAsset', '')
            
            item = {
                'titulo': titulo,
                'fecha': fecha_str,
                'duracion': duracion,
                'url': url,
                'id_asset': id_asset
            }
            
            # Seguir el enlace para obtener más detalles
            if url:
                yield scrapy.Request(
                    url,
                    callback=self.parse_episodio,
                    meta={'item': item}
                )

    def parse_episodio(self, response):
        """
        Parsea la página individual de cada episodio para extraer información detallada.
        
        Args:
            response: Respuesta HTTP de la página del episodio
            
        Yields:
            dict: Información detallada del episodio
        """
        item = response.meta['item']
        
        # Extraer descripción de los metadatos
        descripcion = response.css('meta[name="description"]::attr(content)').get()
        if descripcion:
            item['descripcion'] = descripcion.strip()
        
        # Extraer información del JSON-LD
        json_ld = None
        for script in response.css('script[type="application/ld+json"]::text'):
            try:
                data = json.loads(script.get())
                if data.get('@type') == 'AudioObject':
                    json_ld = data
                    break
            except json.JSONDecodeError:
                continue
        
        if json_ld:
            # Extraer información adicional del JSON-LD
            item['fecha_publicacion'] = json_ld.get('datePublished')
            item['duracion_iso'] = json_ld.get('duration')
            item['url_embed'] = json_ld.get('embedUrl')
            item['url_thumbnail'] = json_ld.get('thumbnailUrl')
            
            # Procesar la descripción para extraer las canciones
            descripcion_completa = json_ld.get('description', '')
            if descripcion_completa:
                # Intentar extraer la lista de canciones
                canciones = []
                for linea in descripcion_completa.split('\n'):
                    if ':' in linea and not linea.startswith('http'):
                        canciones.append(linea.strip())
                if canciones:
                    item['canciones'] = canciones
        
        # Extraer metadatos adicionales
        item['keywords'] = response.css('meta[name="keywords"]::attr(content)').get()
        item['director'] = response.xpath('//script[@type="application/ld+json"][contains(text(), "director")]/text()').re_first(r'"director":\s*"([^"]+)"')
        
        yield item

def main():
    """
    Función principal que ejecuta el scrapper.
    """
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s'
    )
    
    # Configurar el proceso de Scrapy
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/5.0 (compatible; DiscopolisBot/1.0)',
        'ROBOTSTXT_OBEY': True,
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 3,
        'FEEDS': {
            'discopolis_episodios.csv': {
                'format': 'csv',
                'encoding': 'utf8',
                'store_empty': False,
                'fields': [
                    'titulo', 'fecha', 'duracion', 'url', 'id_asset',
                    'descripcion', 'fecha_publicacion', 'duracion_iso',
                    'url_embed', 'url_thumbnail', 'canciones', 'keywords',
                    'director'
                ],
                'overwrite': True,
            }
        }
    })
    
    try:
        # Configurar el event loop para macOS
        if sys.platform == 'darwin':  # macOS
            nest_asyncio.apply()
            asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
            
        # Ejecutar el spider
        process.crawl(DiscopolisSpider)
        process.start(stop_after_crawl=True)
    except KeyboardInterrupt:
        # Manejo limpio de la interrupción por teclado
        reactor.stop()

if __name__ == '__main__':
    main() 