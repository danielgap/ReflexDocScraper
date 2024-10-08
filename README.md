# ReflexDocScraper

ReflexDocScraper es una herramienta automatizada para extraer y estructurar la documentación de [Reflex](https://reflex.dev). Utiliza **web scraping** multihilo para extraer el contenido de la documentación técnica disponible en el sitio, limpiarlo y guardarlo en archivos Markdown bien formateados. Al finalizar, la documentación completa es comprimida en un archivo ZIP.

## Características

- **Scraping multihilo**: Extrae la documentación de Reflex de manera paralela, mejorando el rendimiento y reduciendo el tiempo de ejecución.
- **Almacenamiento en Markdown**: Toda la documentación extraída se guarda en archivos Markdown con una estructura clara y ejemplos de código bien formateados.
- **Comprimido en ZIP**: Al finalizar el scraping, toda la documentación es comprimida en un archivo ZIP para facilitar su almacenamiento o distribución.

## Requisitos

Para ejecutar ReflexDocScraper, necesitas tener instaladas las siguientes bibliotecas de Python:

- [httpx](https://www.python-httpx.org/) - Cliente HTTP asíncrono y moderno.
- [selectolax](https://github.com/rushter/selectolax) - Parser HTML ultra rápido basado en `lexbor`.
- [shutil](https://docs.python.org/3/library/shutil.html) - Biblioteca estándar para operaciones de archivos (ya viene con Python).

Puedes instalarlas con el siguiente comando:

```bash
pip install httpx selectolax
```

## Instalación

1. Clona este repositorio en tu máquina local:

    ```bash
    git clone https://github.com/tu_usuario/ReflexDocScraper.git
    ```

2. Instala las dependencias necesarias:

    ```bash
    pip install -r requirements.txt
    ```

3. Ejecuta el script principal para comenzar el scraping:

    ```bash
    python reflex_doc_scraper.py
    ```

## Uso

Este proyecto scrapeará toda la documentación disponible en [Reflex](https://reflex.dev) bajo la ruta `/docs/` y la guardará en archivos Markdown.

### Ejecución

1. Ejecuta el siguiente comando para comenzar el scraping:

    ```bash
    python reflex_doc_scraper.py
    ```

2. Al finalizar, se creará una carpeta llamada `docs/` que contendrá todos los archivos Markdown generados.
3. Además, se comprimirá la carpeta `docs` en un archivo ZIP llamado `reflex_docs.zip` que contendrá toda la documentación en un formato portátil.

### Estructura del Markdown generado

Cada archivo Markdown tendrá la siguiente estructura:

```markdown
# Título de la Página

**URL**: https://reflex.dev/docs/algun-enlace/

Descripción extraída de la documentación.

## Examples

```python
# Ejemplo de código extraído de la documentación
def example():
    pass
```
```

## Ejemplo de salida

Al ejecutar el script, generará archivos Markdown organizados en la carpeta `docs/` y un archivo comprimido `reflex_docs.zip`.

```
docs/
    getting_started.md
    installation.md
    components.md
    axis.md
    ...
reflex_docs.zip
```

## Personalización

### Número de hilos

Por defecto, el scraping se realiza utilizando 10 hilos para acelerar el proceso. Puedes ajustar este número en el archivo `reflex_doc_scraper.py` cambiando el valor de `max_workers` en la siguiente línea:

```python
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
```

### URLs a scrapear

El scraper extrae automáticamente las URLs desde el sitemap de Reflex (`https://reflex.dev/sitemap-0.xml`), filtrando aquellas que pertenecen a `/docs/`. Si quieres añadir más URLs o modificar el comportamiento, puedes cambiar la lógica dentro de la función `get_docs_urls()`.

## Contribuciones

¡Las contribuciones son bienvenidas! Si encuentras algún problema o tienes alguna sugerencia para mejorar el proyecto, no dudes en crear un [issue](https://github.com/tu_usuario/ReflexDocScraper/issues) o enviar un pull request.

## Licencia

Este proyecto está licenciado bajo la licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.
