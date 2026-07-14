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

        # 2. Изображение/Медиа
        image = None
        
        # Фото
        photo_wrap = msg.find('div', class_='tgme_widget_message_photo_wrap')
        if photo_wrap and photo_wrap.get('style'):
            match = re.search(r'url\(["\']?(.*?)["\']?\)', photo_wrap['style'])
            if match: image = match.group(1)
        
        # Видео (обложка)
        if not image:
            video_wrap = msg.find('div', class_='tgme_widget_message_video_wrap')
            if video_wrap and video_wrap.get('style'):
                match = re.search(r'url\(["\']?(.*?)["\']?\)', video_wrap['style'])
                if match: image = match.group(1)

        # Превью ссылки
        if not image:
            link_preview = msg.find('div', class_='tgme_widget_message_link_preview')
            if link_preview:
                img = link_preview.find('img')
                if img and img.get('src'): image = img['src']

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
            # РЕЖИМ ДЕТЕКТИВА: Печатаем классы и кусок HTML пропущенного блока
            classes = msg.get('class', [])
            print(f"⚠️ Блок {i+1} пропущен. Классы: {classes}")
            inner_html = str(msg)[:400].replace('\n', ' ').replace('  ', ' ')
            print(f"   Содержимое блока: {inner_html}...")

    print(f"🏁 ИТОГО: Собрано {len(posts_data)} постов.")
    with open('posts.json', 'w', encoding='utf-8') as f:
        json.dump(posts_data, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    fetch_posts()
