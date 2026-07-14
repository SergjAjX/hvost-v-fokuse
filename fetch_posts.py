import os
import json
import requests
from bs4 import BeautifulSoup
import re

CHANNEL_NAME = os.getenv('CHANNEL', 'HVOST_V_FOKUSE').replace('@', '').strip()
URL = f'https://t.me/s/{CHANNEL_NAME}'

def fetch_posts():
    print(f"🔍 Запрос к: {URL}")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(URL, headers=headers, timeout=20)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Ошибка сети: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    posts_data = []
    messages = soup.find_all('div', class_='tgme_widget_message')
    print(f"📝 Найдено сообщений в HTML: {len(messages)}")

    for i, msg in enumerate(messages):
        if len(posts_data) >= 5:
            break

        # 1. Текст
        text = ""
        text_tag = msg.find('div', class_='tgme_widget_message_text')
        if text_tag:
            text = text_tag.get_text(separator='\n', strip=True)

        # 2. Изображение (Стандартный поиск)
        image = None
        photo_wrap = msg.find('div', class_='tgme_widget_message_photo_wrap')
        if photo_wrap and photo_wrap.get('style'):
            match = re.search(r'url\(["\']?(.*?)["\']?\)', photo_wrap['style'])
            if match: image = match.group(1)

        # 3. Дата и ссылка
        date_text = 'Неизвестно'
        date_tag = msg.find('time')
        if date_tag:
            date_text = date_tag.text.strip() or date_tag.get('datetime', 'Неизвестно')[:10]
        
        link = f'https://t.me/{CHANNEL_NAME}'
        link_tag = msg.find('a', class_='tgme_widget_message_date')
        if link_tag and link_tag.get('href'):
            link = link_tag['href']

        # ЛОГИКА СОХРАНЕНИЯ И ДИАГНОСТИКИ
        if text or image:
            posts_data.append({'date': date_text, 'text': text, 'image': image, 'link': link})
            print(f"✅ Пост #{len(posts_data)}: Текст={len(text)} зн., Фото={'Да' if image else 'Нет'}")
        else:
            # 🔍 ПОЛНЫЙ РЕЖИМ ДЕТЕКТИВА: Печатаем ВСЕ медиа в пропущенном блоке
            print(f"⚠️ Блок {i+1} пропущен. Классы: {msg.get('class', [])}")
            
            # Ищем все теги img
            for img in msg.find_all('img'):
                src = img.get('src', '')
                classes = img.get('class', [])
                print(f"   🖼️ Найдена картинка (img):")
                print(f"      src: {src[:80]}...")
                print(f"      class: {classes}")
            
            # Ищем все фоновые изображения
            for div in msg.find_all('div'):
                style = div.get('style', '')
                if 'background-image' in style and 'telesco.pe' in style:
                    print(f"   🖼️ Найдено фоновое изображение (div): {style[:100]}...")

    print(f"🏁 ИТОГО: Собрано {len(posts_data)} постов.")
    with open('posts.json', 'w', encoding='utf-8') as f:
        json.dump(posts_data, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    fetch_posts()
