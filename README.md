# Ejercico 1.a del taller de programación aumentada con IA

[Web del curso](https://doble.io/es/courses/ai-enhanced-coding)

## RTVE Radio Scraper

Scraper para extraer información de los programas de radio de RTVE.

## Instalación

1. Crear un entorno virtual:
```bash
python -m venv venv
```

2. Activar el entorno virtual:
- Windows:
```bash
.\venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Uso

Para ejecutar el scraper:

```bash
cd rtve_scraper
scrapy crawl rtve_radio -o programas.json
```

Esto generará un archivo `programas.json` con la información de todos los programas de radio encontrados.

## Datos extraídos

Para cada programa se extrae:
- Título
- Descripción
- URL del programa
- URL de la imagen
