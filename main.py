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
        # Extraemos todas las URLs dentro del sitemap
        for loc in parser.tags('loc'):
            url = loc.text().strip()
            # Filtramos solo las que pertenecen a /docs/
            if '/docs/' in url:
                urls.append(url)
        return urls
    else:
        print(f"Error al acceder al sitemap: {response.status_code}")
        return []

# Función para filtrar y formatear el contenido innecesario
def clean_content(content_node):
    # Eliminamos script, style y clases CSS que no son útiles
    for tag in content_node.css('script, style, [class*="css-"], footer, nav'):
        tag.decompose()  # Eliminamos estos elementos del árbol DOM

    # Retornamos texto limpio con saltos de línea para Markdown
    return content_node.text(separator="\n\n").strip()

# Función para obtener y formatear ejemplos de código
def extract_code_blocks(content_node):
    # Buscar bloques de código en la página
    code_blocks = content_node.css('pre, code')
    formatted_code = []
    
    for block in code_blocks:
        # Eliminar cualquier contenido dentro de tags innecesarios dentro del bloque de código
        clean_block = block.text().strip()
        if clean_block:
            formatted_code.append(f"```python\n{clean_block}\n```")
    
    return "\n\n".join(formatted_code)

# Función para scrapear el contenido de cada página
def scrape_page(url):
    try:
        response = httpx.get(url)
        if response.status_code == 200:
            parser = HTMLParser(response.text)
            content = parser.css_first('main')
            if content:
                # Extraer el título de la página
                title_node = content.css_first('h1')
                title = title_node.text(strip=True) if title_node else 'No Title'

                # Limpiar el contenido y extraer el texto
                doc_text = clean_content(content)
                
                # Extraer ejemplos de código, si existen
                code_examples = extract_code_blocks(content)

                # Formatear el contenido con ejemplos de código separados
                full_content = f"{doc_text}\n\n## Examples\n\n{code_examples}" if code_examples else doc_text
                
                save_to_markdown(title, full_content, url)
            else:
                print(f"No se encontró contenido principal en: {url}")
        else:
            print(f"Error al acceder a la página: {response.status_code}")
    except Exception as e:
        print(f"Error al scrapear {url}: {e}")

# Función para guardar el contenido en un archivo Markdown
def save_to_markdown(title, content, url):
    # Crear nombre de archivo basado en el título
    file_name = title.replace(' ', '_').lower() + '.md'
    # Crear la carpeta "docs" si no existe
    os.makedirs(output_dir, exist_ok=True)
    # Ruta completa para guardar el archivo
    file_path = os.path.join(output_dir, file_name)

    # Formatear y escribir el contenido en el archivo Markdown
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(f"# {title}\n\n")
        f.write(f"**URL**: {url}\n\n")
        f.write(content)

    print(f"Guardado: {file_path}")

# Función para comprimir la carpeta de documentación en un archivo ZIP
def create_zip(output_dir, zip_filename):
    shutil.make_archive(zip_filename.replace('.zip', ''), 'zip', output_dir)
    print(f"Documentación comprimida en: {zip_filename}")

# Función principal con uso de hilos
def main():
    # Obtener todas las URLs de la documentación desde el sitemap
    docs_urls = get_docs_urls(sitemap_url)

    if docs_urls:
        print(f"Se encontraron {len(docs_urls)} páginas en la documentación.")
        
        # Ejecutar scraping en paralelo usando múltiples hilos
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(scrape_page, docs_urls)
        
        # Comprimir la carpeta docs en un archivo ZIP
        create_zip(output_dir, zip_filename)
    else:
        print("No se encontraron URLs de documentación.")

if __name__ == '__main__':
    main()
