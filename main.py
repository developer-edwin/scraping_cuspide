import requests
from bs4 import BeautifulSoup
import mysql.connector
import datetime

def get_usd_blue_exchange_rate():
    url_dolarhoy = 'https://dolarhoy.com/'
    response_dolarhoy = requests.get(url_dolarhoy)

    if response_dolarhoy.status_code == 200:
        soup_dolarhoy = BeautifulSoup(response_dolarhoy.text, 'html.parser')
        div_val = soup_dolarhoy.find('div', class_='venta').find('div', class_='val')
        exchange_rate = float(div_val.text.strip().replace('$', ''))
        return exchange_rate
    else:
        print("Error al obtener el valor del USD blue.")
        exit()

# Configurar la conexión a la base de datos
conexion = mysql.connector.connect(
    host='localhost',
    user='root',
    password='1enter',
    database='scraping'
)

cursor = conexion.cursor()

url_base = 'https://www.cuspide.com'
url = url_base + '/cienmasvendidos'
response = requests.get(url)

if response.status_code == 200:
    html_content = response.text
else:
    print("Error al obtener el contenido de la página")
    exit()

soup = BeautifulSoup(html_content, 'html.parser')

# Buscar todas las etiquetas 'article'
articulos = soup.find_all('article')

# Obtengo el tipo de cambio a la venta actual
cambio_venta = get_usd_blue_exchange_rate()

for index, articulo in enumerate(articulos):
    # Buscar la etiqueta 'a' dentro de 'article'
    # con el atributo 'id' específico
    enlace_tapa = articulo.find('a')
    
    # Construir la nueva URL para cada libro
    libro_url = url_base + enlace_tapa['href']
    response_libro = requests.get(libro_url)
    
    if response_libro.status_code == 200:
        html_libro = response_libro.text
    else:
        print(f"Error al obtener el contenido del libro: {enlace_tapa['title']}")
        continue

    soup_libro = BeautifulSoup(html_libro, 'html.parser')

    # Buscar los elementos 'div' que contienen los precios
    div_precios = soup_libro.find_all('div', class_='precio')
    
    # Obtener el precio en AR$ y USD
    precio_ar = None
    precio_usd = None
    precio_usd_blue = None
    for div_precio in div_precios:
        # Buscar el elemento 'span' que contiene la moneda (AR$ o U$s)
        span_moneda = div_precio.find('span')
        if span_moneda:
            moneda = span_moneda.text.strip()

            # Obtener el precio en la moneda correspondiente
            precio = div_precio.text.replace(span_moneda.text, '').strip()
            if moneda == 'AR$':
                precio_ar = float(precio.split('U$s ')[0].replace('.', '').replace(',', '.'))
                precio_usd = float(precio.split('U$s ')[1].replace('.', '').replace(',', '.'))
                precio_usd_blue = round(precio_ar / cambio_venta, 2)
    
    # Obtener la fecha actual
    fecha_actual = datetime.datetime.now()
    
    # Insertar los datos en la tabla 'libros'
    query = "INSERT INTO libros (titulo, url, precio, precio_usd, precio_usd_blue, fecha) VALUES (%s, %s, %s, %s, %s, %s)"
    valores = (enlace_tapa['title'], libro_url, precio_ar, precio_usd, precio_usd_blue, fecha_actual)

    cursor.execute(query, valores)
    conexion.commit()
    
    print(f'Intento numero: {index}')
    print(f"Libro: {enlace_tapa['title']}")
    print(f"URL: {libro_url}")
    print(f"Precio AR$: {precio_ar}")
    print(f"Precio USD: {precio_usd}")
    print(f"Fecha: {fecha_actual}")
    print("=====================")

conexion.close()
