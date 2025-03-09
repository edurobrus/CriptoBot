import os
import requests
import telebot
from bs4 import BeautifulSoup

# Configura tu bot de Telegram con el token
TOKEN = "7928339725:AAE6JYpPcd7x668IcIxIrlxwHB0Tx6DcqPI"
CHAT_ID = "1959498857"  # Reemplaza con el ID de tu grupo o el username de tu chat

# Inicializa el bot de Telegram
bot = telebot.TeleBot(TOKEN)

# URL de CoinMarketCap
url = 'https://coinmarketcap.com/'

# Configurar headers para evitar bloqueos
headers = {'User-Agent': 'Mozilla/5.0'}

# Hacer la solicitud GET
response = requests.get(url, headers=headers)

# Verificar si la solicitud fue exitosa
if response.status_code != 200:
    print(f"Error al obtener la página: {response.status_code}")
else:
    # Crear objeto BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Encontrar el cuerpo de la tabla de criptomonedas
    table_body = soup.find('tbody')

    if table_body:
        # Extraer las filas
        rows = table_body.find_all('tr')
        print(f"🔍 Filas encontradas: {len(rows)}\n")

        # Iterar sobre las primeras 10 criptomonedas
        for row in rows[:10]:
            try:
                # Buscar los elementos dentro de la fila con las nuevas clases
                rank = row.find('p', class_='sc-71024e3e-0 biekbf')  # Rango
                name = row.find('p', class_='sc-65e7f566-0 iPbTJf coin-item-name')  # Nombre
                symbol = row.find('p', class_='sc-65e7f566-0 byYAWx coin-item-symbol')  # Símbolo
                price = row.find('div', class_='sc-142c02c-0 lmjbLF')  # Precio
                market_cap = row.find('span', class_='sc-11478e5d-0 chpohi')  # Capitalización de mercado
                volume = row.find('p', class_='sc-71024e3e-0 fOLOxZ font_weight_500')  # Volumen
                circulating_supply = row.find('div', class_='circulating-supply-value')  # Suministro circulante
                logo_image_tag = row.find('img', class_='coin-logo')  # Logo de la cripto

                # Extraer valores de forma segura
                rank = rank.text.strip() if rank else "N/A"
                name = name.text.strip() if name else "N/A"
                symbol = symbol.text.strip() if symbol else "N/A"
                price = price.span.text.strip() if price and price.span else "N/A"
                market_cap = market_cap.text.strip() if market_cap else "N/A"
                volume = volume.text.strip() if volume else "N/A"
                circulating_supply = circulating_supply.text.strip() if circulating_supply else "N/A"
                logo_url = logo_image_tag['src'] if logo_image_tag else "N/A"

                # Si la URL del logo es válida, enviamos el logo y luego los datos
                if logo_url != "N/A":
                    # Enviar la imagen del logo y los datos en el mismo mensaje
                    message = f"*💥 {name} ({symbol})*\n"
                    message += f"💰 *Precio:* {price}\n"
                    message += f"🏦 *Capitalización de Mercado:* {market_cap}\n"
                    message += f"🔄 *Suministro Circulante:* {circulating_supply}\n"

                    # Enviar primero la foto con el texto en el mismo mensaje
                    bot.send_photo(CHAT_ID, logo_url, caption=message, parse_mode='Markdown')

            except Exception as e:
                print(f"⚠️ Error procesando fila: {e}")

    else:
        print("❌ No se encontró la tabla de criptomonedas.")
