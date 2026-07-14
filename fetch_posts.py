import os
import json
import requests
from bs4 import BeautifulSoup
import re

CHANNEL_NAME = os.getenv('CHANNEL', 'HVOST_V_FOKUSE').replace('@', '').strip()
URL = f'https://t.me/s/{CHANNEL_NAME}'

def fetch_posts():
    print(f"🔍 Запрос к публичному каналу: {URL}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8'
    }

    try:
        response = requests.get(URL, headers=headers, timeout=20)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Ошибка сети: {e}")
        with open('posts.json', 'w', encoding='utf-8') as f:
            json.dump([{"error": "Не удалось подключиться к Telegram"}], f, ensure_ascii=False, indent=2)
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    posts_data = []

    # Находим все блоки сообщений на странице
    message_wraps = soup.find_all('div', class_='tgme_widget_message_wrap')

    for wrap in message_wraps:
        # Непосредственно контейнер самого сообщения
        msg = wrap.find('div', class_='tgme_widget_message')
        if not msg:
            continue

        # 1. Дата и время
        date_tag = msg.find('time', class_='tgme_widget_message_date')
        date_text = date_tag.text.strip() if date_tag else 'Неизвестно'

        # 2. Ссылка на конкретный пост
        link_tag = msg.find('a', class_='tgme_widget_message_date')
        link = link_tag['href'] if link_tag and 'href' in link_tag.attrs else f'https://t.me/{CHANNEL_NAME}'

        # 3. Текст поста
        text = ""
        text_tag = msg.find('div', class_='tgme_widget_message_text')
        if text_tag:
            # Заменяем переносы строк <br> на реальные символы \n перед извлечением текста
            for br in text_tag.find_all('br'):
                br.replace_with('\n')
            text = text_tag.get_text(separator='\n', strip=True)

        # 4. Изображение (проверяем два варианта, которые использует Telegram)
        image = None
        
        # Вариант А: обычная картинка в теге img
        img_tag = msg.find('img', class_='tgme_widget_message_photo_img')
        if img_tag and 'src' in img_tag.attrs:
            image = img_tag['src']
        else:
            # Вариант Б: картинка как фон (background-image)
            photo_wrap = msg.find('div', class_='tgme_widget_message_photo_wrap')
            if photo_wrap and 'style' in photo_wrap.attrs:
                style = photo_wrap['style']
                match = re.search(r"url\(['\"]?(.*?)['\"]?\)", style)
                if match:
                    image = match.group(1)

        # Сохраняем пост, только если в нем есть реальный контент (текст или картинка)
        if text or image:
            posts_data.append({
                'date': date_text,
                'text': text,
                'image': image,
                'link': link
            })

        # Останавливаемся, когда собрали 5 постов
        if len(posts_data) >= 5:
            break

    print(f"✅ Успешно обработано {len(posts_data)} реальных постов.")

    # Сохраняем результат в файл
    with open('posts.json', 'w', encoding='utf-8') as f:
        json.dump(posts_data, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    fetch_posts()
