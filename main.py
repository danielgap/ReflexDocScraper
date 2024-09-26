import httpx
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import re
import unicodedata
import os
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed

# Crear directorio 'docs' si no existe
if not os.path.exists('docs'):
    os.makedirs('docs')

# Función para limpiar y normalizar el texto
def clean_text(text):
    text = unicodedata.normalize("NFKD", text)
    text = text.encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'\\([_+\\-])', r'\1', text)
    return text

# Función para limpiar el HTML y eliminar etiquetas no deseadas
def clean_html(soup):
    for tag in soup(['script', 'style', 'button', 'nav', 'svg', 'footer', 'noscript', 'meta', 'link', 'header']):
        tag.decompose()
    for tag in soup.find_all(True):
        tag.attrs = {}
    return soup

# Descargar y procesar cada página
def process_url(url, file_name):
    try:
        response = httpx.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        soup = clean_html(soup)

        # Convertir el HTML a Markdown
        markdown = md(str(soup), heading_style="ATX", strip=['a', 'div', 'span'], code_language="python")
        markdown = clean_text(markdown)

        # Ajustar y limpiar el Markdown
        markdown = re.sub(r'```python\s+```python', '```python', markdown)
        markdown = re.sub(r'```python\n\n```', '```python\n', markdown)
        markdown = re.sub(r'\n{2,}', '\n\n', markdown)

        # Guardar el archivo en la carpeta 'docs'
        with open(f'docs/{file_name}.md', 'w', encoding='utf-8') as f:
            f.write(markdown)
        print(f"Guardado: docs/{file_name}.md")
    except Exception as e:
        print(f"Error procesando {url}: {e}")

# Descargar y procesar el sitemap
def get_urls_from_sitemap(sitemap_url):
    response = httpx.get(sitemap_url)
    sitemap_soup = BeautifulSoup(response.content, 'xml')
    urls = [url_tag.text for url_tag in sitemap_soup.find_all('loc')]
    return urls

# Función para ejecutar el procesamiento multihilo
def download_all_pages(sitemap_url):
    urls = get_urls_from_sitemap(sitemap_url)
    
    # Usar un ThreadPoolExecutor para el procesamiento multihilo
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for url in urls:
            # Usar el último segmento de la URL como nombre de archivo
            file_name = url.split('/')[-2] if url.endswith('/') else url.split('/')[-1]
            futures.append(executor.submit(process_url, url, file_name))
        
        # Mostrar el estado de las descargas
        for future in as_completed(futures):
            future.result()

# Crear un archivo ZIP con todos los documentos Markdown
def zip_markdown_files():
    zip_file_name = 'docs.zip'
    with zipfile.ZipFile(zip_file_name, 'w') as zipf:
        for root, dirs, files in os.walk('docs'):
            for file in files:
                zipf.write(os.path.join(root, file), file)
    print(f"Archivos comprimidos en {zip_file_name}")

# Ejecutar el programa
if __name__ == "__main__":
    sitemap_url = 'https://reflex.dev/sitemap-0.xml'
    download_all_pages(sitemap_url)
    zip_markdown_files()
