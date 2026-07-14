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
    
    posts = []
    
    try:
        response = requests.get(URL, headers=headers, timeout=20)
        print(f"📡 Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            tg_posts = soup.find_all('div', class_='tgme_widget_message_wrap')
            print(f"📝 Найдено постов в HTML: {len(tg_posts)}")
            
            for post in tg_posts[:5]:
                message = post.find('div', class_='tgme_widget_message')
                if not message:
                    continue
                
                date_tag = message.find('time', class_='tgme_widget_message_date')
                date_text = date_tag.text.strip() if date_tag else 'Неизвестно'
                
                text_tag = message.find('div', class_='tgme_widget_message_text')
                text = text_tag.get_text(separator='\n', strip=True) if text_tag else ''
                
                image = None
                style_tag = message.find('div', class_='tgme_widget_message_photo_wrap')
                if style_tag and 'style' in style_tag.attrs:
                    url_match = re.search(r"url\('(.+?)'\)", style_tag['style'])
                    if url_match:
                        image = url_match.group(1)
                
                link_tag = message.find('a', class_='tgme_widget_message_date')
                link = link_tag['href'] if link_tag else f'https://t.me/{CHANNEL_NAME}'
                
                posts.append({
                    'date': date_text,
                    'text': text,
                    'image': image,
                    'link': link
                })
        else:
            print(f"❌ HTTP {response.status_code}")
            posts = [{"error": f"Канал вернул код {response.status_code}. Проверьте имя канала."}]
            
    except Exception as e:
        print(f"❌ Исключение: {e}")
        posts = [{"error": "Ошибка сети. Попробуйте позже."}]
    
    # ВСЕГДА сохраняем валидный JSON
    with open('posts.json', 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
    
    if posts and not posts[0].get('error'):
        print(f"✅ УСПЕХ! Сохранено {len(posts)} постов")
    else:
        print(f"⚠️ Сохранено сообщение об ошибке")

if __name__ == '__main__':
    fetch_posts()
