# fetch_posts.py
import os
import json
import requests
from bs4 import BeautifulSoup
import re

# Используем точное имя канала из секретов, по умолчанию HVOST_V_FOKUSE
CHANNEL_NAME = os.getenv('CHANNEL', 'HVOST_V_FOKUSE').replace('@', '').strip().upper()
URL = f'https://t.me/s/{CHANNEL_NAME}'

def fetch_posts():
    print(f"🔍 Попытка получить данные из публичного канала: {URL}")
    
    # Маскируемся под обычный браузер, чтобы Telegram не блокировал запрос
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    
    try:
        response = requests.get(URL, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ ОШИБКА СЕТИ: Не удалось подключиться к {URL}")
        print(f"Детали: {e}")
        # Создаем файл с сообщением об ошибке, чтобы фронтенд не ломался
        with open('posts.json', 'w', encoding='utf-8') as f:
            json.dump([{"error": "Канал недоступен. Проверьте точность имени HVOST_V_FOKUSE и убедитесь, что в канале есть хотя бы один пост."}], f, ensure_ascii=False, indent=2)
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Проверка на пустой канал или несуществующий
    if "If you have Telegram, you can view" in response.text or "no posts" in response.text.lower():
        print(f"⚠️ ВНИМАНИЕ: Канал @{CHANNEL_NAME} не найден, является частным или в нем нет ни одного поста.")
        with open('posts.json', 'w', encoding='utf-8') as f:
            json.dump([{"error": "Канал пуст или не является публичным. Добавьте хотя бы один пост и убедитесь, что в настройках канала задана постоянная ссылка."}], f, ensure_ascii=False, indent=2)
        return

    posts = []
    tg_posts = soup.find_all('div', class_='tgme_widget_message_wrap')
    
    for post in tg_posts[:5]: # Берем строго последние 5 постов
        message = post.find('div', class_='tgme_widget_message')
        if not message:
            continue
            
        # Дата
        date_tag = message.find('time', class_='tgme_widget_message_date')
        date_text = date_tag.text.strip() if date_tag else 'Неизвестно'
        datetime_iso = date_tag['datetime'] if date_tag else ''
        
        # Текст
        text_tag = message.find('div', class_='tgme_widget_message_text')
        text = text_tag.get_text(separator='\n', strip=True) if text_tag else ''
        
        # Изображение
        image = None
        img_tag = message.find('img', class_='tgme_widget_message_photo_img')
        if img_tag and 'src' in img_tag.attrs:
            image = img_tag['src']
        else:
            style_tag = message.find('div', class_='tgme_widget_message_photo_wrap')
            if style_tag and 'style' in style_tag.attrs:
                url_match = re.search(r"url\('(.+?)'\)", style_tag['style'])
                if url_match:
                    image = url_match.group(1)

        # Ссылка на пост
        link_tag = message.find('a', class_='tgme_widget_message_date')
        link = link_tag['href'] if link_tag else f'https://t.me/{CHANNEL_NAME}'

        posts.append({
            'date': date_text,
            'datetime': datetime_iso,
            'text': text,
            'image': image,
            'link': link
        })

    with open('posts.json', 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
    print(f"✅ УСПЕХ! Сохранено {len(posts)} постов в posts.json для канала @{CHANNEL_NAME}")

if __name__ == '__main__':
    fetch_posts()
