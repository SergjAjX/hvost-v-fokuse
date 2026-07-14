import os
import json
import requests
import re
import html

CHANNEL_NAME = os.getenv('CHANNEL', 'HVOST_V_FOKUSE').replace('@', '').strip()
URL = f'https://t.me/s/{CHANNEL_NAME}'

def fetch_posts():
    print(f"🔍 Запрос к: {URL}")

    # Максимально реалистичные заголовки обычного браузера Chrome
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
    }

    try:
        response = requests.get(URL, headers=headers, timeout=20)
        print(f"📡 Статус ответа Telegram: {response.status_code}")

        if response.status_code != 200:
            error_msg = f"Telegram вернул код {response.status_code} (возможна блокировка запросов с IP GitHub)."
            print(f"❌ {error_msg}")
            with open('posts.json', 'w', encoding='utf-8') as f:
                json.dump([{"error": error_msg}], f, ensure_ascii=False, indent=2)
            return

        posts = []
        # Ищем блоки сообщений с помощью регулярных выражений (самый надежный способ для t.me/s/)
        post_blocks = re.findall(r'<div class="tgme_widget_message_wrap.*?</div>\s*</div>', response.text, re.DOTALL)
        
        print(f"📝 Найдено блоков постов в HTML: {len(post_blocks)}")

        for block in post_blocks[:5]: # Берем только 5 последних
            # 1. Дата
            date_match = re.search(r'<time class="tgme_widget_message_date"[^>]*>(.*?)</time>', block)
            date_text = date_match.group(1).strip() if date_match else 'Неизвестно'
            
            # 2. Ссылка на пост
            link_match = re.search(r'<a class="tgme_widget_message_date"[^>]*href="(.*?)"', block)
            link = link_match.group(1) if link_match else f'https://t.me/{CHANNEL_NAME}'
            
            # 3. Текст (очищаем от HTML-тегов)
            text_match = re.search(r'<div class="tgme_widget_message_text[^>]*>(.*?)</div>', block, re.DOTALL)
            if text_match:
                text = re.sub(r'<[^>]+>', '\n', text_match.group(1))
                text = re.sub(r'\n+', '\n', text).strip()
                text = html.unescape(text) # Преобразуем &quot; и т.д.
            else:
                text = ''

            # 4. Картинка (ищем в style или в img src)
            img_match = re.search(r'background-image:url\((.*?)\)', block)
            if not img_match:
                img_match = re.search(r'<img class="tgme_widget_message_photo_img"[^>]*src="(.*?)"', block)
            
            image = img_match.group(1) if img_match else None

            # Добавляем пост, только если в нем есть текст или картинка
            if text or image:
                posts.append({
                    'date': date_text,
                    'text': text,
                    'image': image,
                    'link': link
                })

        print(f"✅ УСПЕХ! Корректно обработано {len(posts)} постов.")
        
        with open('posts.json', 'w', encoding='utf-8') as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)

    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА СКРИПТА: {e}")
        with open('posts.json', 'w', encoding='utf-8') as f:
            json.dump([{"error": f"Сбой скрипта: {str(e)}"}], f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    fetch_posts()
