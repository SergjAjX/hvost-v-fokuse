# fetch_posts.py
import os
import json
import requests
from bs4 import BeautifulSoup

CHANNEL_NAME = os.getenv('CHANNEL', '@hvost_v_fokuse').replace('@', '')
URL = f'https://t.me/s/{CHANNEL_NAME}'

def fetch_posts():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    posts = []
    # Ищем все блоки постов в публичном канале
    tg_posts = soup.find_all('div', class_='tgme_widget_message_wrap')
    
    for post in tg_posts[:5]: # Берем только последние 5
        message = post.find('div', class_='tgme_widget_message')
        if not message:
            continue
            
        # Дата
        date_tag = message.find('time', class_='tgme_widget_message_date')
        date = date_tag['datetime'] if date_tag else 'Неизвестно'
        date_text = date_tag.text if date_tag else ''
        
        # Текст
        text_tag = message.find('div', class_='tgme_widget_message_text')
        text = text_tag.get_text(separator='\n', strip=True) if text_tag else ''
        
        # Изображение
        image = None
        img_tag = message.find('img', class_='tgme_widget_message_photo_img')
        if img_tag and 'src' in img_tag.attrs:
            image = img_tag['src']
        else:
            # Проверка на круглое видео/фото
            style_tag = message.find('div', class_='tgme_widget_message_photo_wrap')
            if style_tag and 'style' in style_tag.attrs:
                import re
                url_match = re.search(r"url\('(.+?)'\)", style_tag['style'])
                if url_match:
                    image = url_match.group(1)

        # Ссылка на пост
        link_tag = message.find('a', class_='tgme_widget_message_date')
        link = link_tag['href'] if link_tag else f'https://t.me/{CHANNEL_NAME}'

        posts.append({
            'date': date_text,
            'datetime': date,
            'text': text,
            'image': image,
            'link': link
        })

    with open('posts.json', 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
    print("Successfully updated posts.json")

if __name__ == '__main__':
    fetch_posts()
