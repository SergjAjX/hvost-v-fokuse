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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept-Language': 'ru-RU,ru;q=0.9'
    }

    try:
        response = requests.get(URL, headers=headers, timeout=20)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Ошибка сети: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    posts_data = []

    message_wraps = soup.find_all('div', class_='tgme_widget_message_wrap')[:10]
    print(f"📝 Найдено блоков в HTML: {len(message_wraps)}")

    for wrap in message_wraps:
        if len(posts_data) >= 5:
            break
            
        msg = wrap.find('div', class_='tgme_widget_message')
        if not msg:
            continue

        # 1. Дата
        date_text = 'Неизвестно'
        date_tag = msg.find('time', class_='tgme_widget_message_date')
        if date_tag:
            date_text = date_tag.text.strip()
        else:
            date_tag = msg.find('time')
            if date_tag and 'datetime' in date_tag.attrs:
                date_text = date_tag.attrs['datetime'][:10]

        # 2. Ссылка
        link = f'https://t.me/{CHANNEL_NAME}'
        link_tag = msg.find('a', class_='tgme_widget_message_date')
        if link_tag and 'href' in link_tag.attrs:
            link = link_tag['href']

        # 3. Текст
        text = ""
        text_tag = msg.find('div', class_='tgme_widget_message_text')
        if text_tag:
            for br in text_tag.find_all('br'):
                br.replace_with('\n')
            text = text_tag.get_text(separator='\n', strip=True)

        # 4. Изображение (УМНЫЙ ПОИСК ПО ДОМЕНУ TELESCO.PE)
        image = None
        
        # Превращаем весь блок сообщения в строку для гибкого поиска
        msg_html = str(msg)
        
        # Ищем любую ссылку на картинку Telegram (cdn4.telesco.pe/file/...)
        # Это работает для обычных фото, альбомов, круглых видео и превью
        img_match = re.search(r'(https://cdn\d+\.telesco\.pe/file/[^\s\'"<>]+)', msg_html)
        if img_match:
            image = img_match.group(1)
            print(f"  ✅ Найдено фото по домену telesco.pe для поста: '{text[:30]}...'")
        else:
            print(f"  ⚠️ Фото НЕ НАЙДЕНО для поста: '{text[:30]}...'")

        # Сохраняем пост
        if text or image:
            posts_data.append({
                'date': date_text,
                'text': text,
                'image': image,
                'link': link
            })

    print(f"🏁 ИТОГО: Собрано {len(posts_data)} постов.")

    with open('posts.json', 'w', encoding='utf-8') as f:
        json.dump(posts_data, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    fetch_posts()
