import os
import json
import requests
from bs4 import BeautifulSoup
import re

CHANNEL_NAME = os.getenv('CHANNEL', 'HVOST_V_FOKUSE').replace('@', '').strip()
URL = f'https://t.me/s/{CHANNEL_NAME}'

def fetch_posts():
    print(f"🔍 Запрос к: {URL}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept-Language': 'ru-RU,ru;q=0.9'
    }

    try:
        response = requests.get(URL, headers=headers, timeout=20)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        with open('posts.json', 'w', encoding='utf-8') as f:
            json.dump([{"error": "Не удалось подключиться"}], f, ensure_ascii=False, indent=2)
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    posts_data = []

    message_wraps = soup.find_all('div', class_='tgme_widget_message_wrap')

    for wrap in message_wraps:
        msg = wrap.find('div', class_='tgme_widget_message')
        if not msg:
            continue

        # 1. Дата — улучшенный поиск
        date_text = 'Неизвестно'
        date_tag = msg.find('time', class_='tgme_widget_message_date')
        if date_tag:
            date_text = date_tag.text.strip()
        else:
            # Пробуем найти дату по атрибуту datetime
            date_tag = msg.find('time')
            if date_tag and 'datetime' in date_tag.attrs:
                date_text = date_tag.attrs['datetime'][:10]  # Берем только дату YYYY-MM-DD

        # 2. Ссылка на пост
        link = f'https://t.me/{CHANNEL_NAME}'
        link_tag = msg.find('a', class_='tgme_widget_message_date')
        if link_tag and 'href' in link_tag.attrs:
            link = link_tag['href']

        # 3. Текст поста
        text = ""
        text_tag = msg.find('div', class_='tgme_widget_message_text')
        if text_tag:
            for br in text_tag.find_all('br'):
                br.replace_with('\n')
            text = text_tag.get_text(separator='\n', strip=True)

        # 4. Изображение — расширенный поиск
        image = None
        
        # Ищем в разных местах
        for img_class in ['tgme_widget_message_photo_img', 'tgme_widget_message_roundvideo']:
            img_tag = msg.find('img', class_=img_class)
            if img_tag and 'src' in img_tag.attrs:
                image = img_tag['src']
                break
        
        if not image:
            # Ищем в background-image
            for wrap_class in ['tgme_widget_message_photo_wrap', 'tgme_widget_message_video_wrap']:
                wrap_tag = msg.find('div', class_=wrap_class)
                if wrap_tag and 'style' in wrap_tag.attrs:
                    match = re.search(r"url\(['\"]?(.*?)['\"]?\)", wrap_tag['style'])
                    if match:
                        image = match.group(1)
                        break

        # Сохраняем пост с контентом
        if text or image:
            posts_data.append({
                'date': date_text,
                'text': text,
                'image': image,
                'link': link
            })

        if len(posts_data) >= 5:
            break

    print(f"✅ Найдено {len(posts_data)} постов")

    with open('posts.json', 'w', encoding='utf-8') as f:
        json.dump(posts_data, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    fetch_posts()
