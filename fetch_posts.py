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

    # Находим все блоки сообщений
    messages = soup.find_all('div', class_='tgme_widget_message')
    print(f"📝 Найдено сообщений в HTML: {len(messages)}")

    for msg in messages:
        if len(posts_data) >= 5:
            break

        # 1. Текст: ищем строго в теле сообщения
        text = ""
        text_tag = msg.find('div', class_='tgme_widget_message_text')
        if text_tag:
            for br in text_tag.find_all('br'):
                br.replace_with('\n')
            text = text_tag.get_text(separator='\n', strip=True)

        # 2. Изображение: МНОГОУРОВНЕВЫЙ ПОИСК
        image = None
        
        # А. Фото как фон (основной способ Telegram для постов с фото)
        photo_wrap = msg.find('div', class_='tgme_widget_message_photo_wrap')
        if photo_wrap and photo_wrap.get('style'):
            match = re.search(r'url\(\s*[\'"]?(.*?)[\'"]?\s*\)', photo_wrap['style'])
            if match:
                image = match.group(1)
        
        # Б. Видео/Гифка как фон
        if not image:
            video_wrap = msg.find('div', class_='tgme_widget_message_video_wrap')
            if video_wrap and video_wrap.get('style'):
                match = re.search(r'url\(\s*[\'"]?(.*?)[\'"]?\s*\)', video_wrap['style'])
                if match:
                    image = match.group(1)

        # В. Превью внешней ссылки
        if not image:
            link_preview = msg.find('div', class_='tgme_widget_message_link_preview')
            if link_preview:
                prev_img = link_preview.find('img')
                if prev_img and prev_img.get('src'):
                    image = prev_img['src']

        # Г. ЗАПАСНОЙ ВАРИАНТ: Любая картинка внутри ТЕЛА сообщения (исключает аватарку канала!)
        if not image:
            body = msg.find('div', class_='tgme_widget_message_body')
            if body:
                imgs = body.find_all('img')
                for img in imgs:
                    src = img.get('src', '')
                    # Проверяем, что это реальное медиа Telegram, а не смайлик или иконка
                    if 'cdn' in src and 'telesco.pe' in src:
                        image = src
                        break

        # 3. Дата
        date_text = 'Неизвестно'
        date_tag = msg.find('time', class_='tgme_widget_message_date')
        if date_tag:
            date_text = date_tag.text.strip()
        else:
            date_tag = msg.find('time')
            if date_tag and 'datetime' in date_tag.attrs:
                date_text = date_tag.attrs['datetime'][:10]

        # 4. Ссылка
        link = f'https://t.me/{CHANNEL_NAME}'
        link_tag = msg.find('a', class_='tgme_widget_message_date')
        if link_tag and 'href' in link_tag.attrs:
            link = link_tag['href']

        # Сохраняем, если есть текст ИЛИ изображение (теперь посты только с фото тоже сохранятся!)
        if text or image:
            posts_data.append({
                'date': date_text,
                'text': text,
                'image': image,
                'link': link
            })
            print(f"✅ Добавлен: Дата={date_text}, Текст={len(text)} зн., Фото={'Да' if image else 'Нет'}")
        else:
            print(f"⏩ Пропущен пустой/сервисный блок")

    print(f"🏁 ИТОГО: Собрано {len(posts_data)} постов.")

    with open('posts.json', 'w', encoding='utf-8') as f:
        json.dump(posts_data, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    fetch_posts()
