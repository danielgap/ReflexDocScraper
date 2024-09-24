import httpx
from selectolax.parser import HTMLParser
import os
import concurrent.futures
import shutil

# URL del sitemap
sitemap_url = 'https://reflex.dev/sitemap-0.xml'
output_dir = 'docs'  # Carpeta donde se almacenarán los archivos markdown
zip_filename = 'reflex_docs.zip'  # Nombre del archivo ZIP final

# Función para obtener las URLs de la sección /docs/ desde el sitemap
def get_docs_urls(sitemap_url):
    response = httpx.get(sitemap_url)
    if response.status_code == 200:
        parser = HTMLParser(response.text)
        urls = []
        for loc in parser.tags('loc'):
            url = loc.text().strip()
            if '/docs/' in url:
                urls.append(url)
        return urls
    else:
        print(f"Error al acceder al sitemap: {response.status_code}")
        return []

# Función para limpiar y filtrar el contenido relevante
def clean_and_filter_content(html_content):
    tree = HTMLParser(html_content)

    # Eliminar menús, pies de página y otros elementos no relacionados
    for tag in tree.css('nav, footer, header, aside, script, style'):
        tag.decompose()

    # Extraer el contenido principal
    main_content = tree.css_first('main, article, .content')
    if not main_content:
        main_content = tree.body

    # Extraer el texto relevante
    filtered_text = []
    for node in main_content.css('h1, h2, h3, p, li'):
        # Detectar títulos y subtítulos y formatearlos adecuadamente
        if node.tag in ['h1', 'h2', 'h3']:
            text = f"## {node.text(strip=True)}"
        else:
            text = node.text(strip=True)
        
        if text and text not in filtered_text:
            filtered_text.append(text)

    # Extraer bloques de código (solo Python en este caso)
    code_blocks = [node.text(strip=True) for node in main_content.css('pre, code') if 'python' in node.attributes.get('class', '')]

    return "\n\n".join(filtered_text), code_blocks

# Formatear en Markdown
def format_to_markdown(title, content, url, code_blocks):
    markdown = f"# {title}\n\n**URL**: {url}\n\n{content}\n\n"

    if code_blocks:
        markdown += "## Ejemplos de Código\n\n"
        for code in code_blocks:
            markdown += f"```python\n{code}\n```\n\n"

    return markdown

# Guardar el contenido formateado
def save_markdown(title, markdown_content):
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"{title.replace(' ', '_').lower()}.md")
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(markdown_content)
    print(f"Guardado en: {filename}")

# Función para scrapear el contenido de cada página
def scrape_page(url):
    try:
        response = httpx.get(url)
        response.raise_for_status()

        # Limpieza y filtrado del contenido
        content, code_blocks = clean_and_filter_content(response.text)

        # Extraer el título de la página
        tree = HTMLParser(response.text)
        title_node = tree.css_first('h1')
        title = title_node.text(strip=True) if title_node else 'Sin título'

        # Formateo en Markdown
        markdown_content = format_to_markdown(title, content, url, code_blocks)

        # Guardar en archivo Markdown
        save_markdown(title, markdown_content)

    except Exception as e:
        print(f"Error al extraer la página {url}: {e}")

# Función para comprimir la carpeta de documentación en un archivo ZIP
def create_zip(output_dir, zip_filename):
    shutil.make_archive(zip_filename.replace('.zip', ''), 'zip', output_dir)
    print(f"Documentación comprimida en: {zip_filename}")

# Función principal
def main():
    # Obtener todas las URLs de la documentación
    docs_urls = get_docs_urls(sitemap_url)

    if docs_urls:
        print(f"Se encontraron {len(docs_urls)} páginas en la documentación.")
        
        # Ejecutar scraping en paralelo usando múltiples hilos
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            executor.map(scrape_page, docs_urls)
        
        # Comprimir la carpeta docs en un archivo ZIP
        create_zip(output_dir, zip_filename)
    else:
        print("No se encontraron URLs de documentación.")

if __name__ == '__main__':
    main()
