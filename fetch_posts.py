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

    # Находим все блоки сообщений на странице
    messages = soup.find_all('div', class_='tgme_widget_message')
    print(f"📝 Найдено сообщений в HTML: {len(messages)}")

    for msg in messages:
        if len(posts_data) >= 5:
            break

        # 1. Текст поста (строгий поиск по классу текста)
        text = ""
        text_tag = msg.find('div', class_='tgme_widget_message_text')
        if text_tag:
            for br in text_tag.find_all('br'):
                br.replace_with('\n')
            text = text_tag.get_text(separator='\n', strip=True)

        # 2. Изображение поста (СТРОГИЙ ПОИСК, исключающий аватарку канала)
        image = None
        
        # Способ А: Обертка фото (самый частый и надежный вариант для постов с картинкой)
        photo_wrap = msg.find('div', class_='tgme_widget_message_photo_wrap')
        if photo_wrap and photo_wrap.get('style'):
            match = re.search(r'url\(\s*[\'"]?(.*?)[\'"]?\s*\)', photo_wrap['style'])
            if match:
                image = match.group(1)
        
        # Способ Б: Тег img с классом фото сообщения (если нет wrap)
        if not image:
            img_tag = msg.find('img', class_='tgme_widget_message_photo_img')
            if img_tag and img_tag.get('src'):
                image = img_tag['src']
                
        # Способ В: Превью ссылки (если пост - это ссылка на внешнюю статью)
        if not image:
            link_preview = msg.find('div', class_='tgme_widget_message_link_preview')
            if link_preview:
                prev_img = link_preview.find('img')
                if prev_img and prev_img.get('src'):
                    image = prev_img['src']

        # 3. Дата
        date_text = 'Неизвестно'
        date_tag = msg.find('time', class_='tgme_widget_message_date')
        if date_tag:
            date_text = date_tag.text.strip()
        else:
            date_tag = msg.find('time')
            if date_tag and 'datetime' in date_tag.attrs:
                date_text = date_tag.attrs['datetime'][:10]

        # 4. Ссылка на пост
        link = f'https://t.me/{CHANNEL_NAME}'
        link_tag = msg.find('a', class_='tgme_widget_message_date')
        if link_tag and 'href' in link_tag.attrs:
            link = link_tag['href']

        # Сохраняем пост, если есть текст ИЛИ изображение (или и то, и другое)
        if text or image:
            posts_data.append({
                'date': date_text,
                'text': text,
                'image': image,
                'link': link
            })
            print(f"✅ Добавлен: Дата={date_text}, Текст={len(text)} зн., Фото={'Да' if image else 'Нет'}")

    print(f"🏁 ИТОГО: Собрано {len(posts_data)} постов.")

    with open('posts.json', 'w', encoding='utf-8') as f:
        json.dump(posts_data, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    fetch_posts()
