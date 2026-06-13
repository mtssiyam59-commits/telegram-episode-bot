import requests
from bs4 import BeautifulSoup
import schedule
import time
import json
from telegram import Bot
from datetime import datetime
from config import BOT1_TOKEN, NOTIFICATION_CHANNEL_ID, WEBSITE_URL, CHECK_INTERVAL
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT1_TOKEN)
LAST_EPISODES_FILE = 'last_episodes.json'

def load_last_episodes():
    """আগের এপিসোড সংরক্ষণ থেকে লোড করবে"""
    try:
        with open(LAST_EPISODES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_last_episodes(episodes):
    """এপিসোড সংরক্ষণ করবে"""
    with open(LAST_EPISODES_FILE, 'w', encoding='utf-8') as f:
        json.dump(episodes, f, ensure_ascii=False, indent=2)

def is_bengali(text):
    """বাংলা ভাষা চেক করবে"""
    bengali_range = range(0x0980, 0x09FF)
    return any(ord(char) in bengali_range for char in text)

def scrape_sunnxt():
    """SunNXT থেকে নতুন এপিসোড খুঁজবে"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(WEBSITE_URL, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.content, 'html.parser')
        
        episodes = []
        
        # SunNXT এর জন্য এপিসোড খুঁজবে (স্ট্রাকচার অনুযায়ী আপডেট করুন)
        episode_items = soup.find_all('div', class_='episode-item')
        
        for item in episode_items:
            try:
                title = item.find('h3') or item.find('p', class_='title')
                if not title:
                    continue
                
                title_text = title.get_text(strip=True)
                
                # শুধুমাত্র বাংলা এপিসোড
                if not is_bengali(title_text):
                    continue
                
                link_elem = item.find('a', href=True)
                img_elem = item.find('img')
                
                episode_link = link_elem['href'] if link_elem else ''
                image_url = img_elem['src'] if img_elem else ''
                
                # সম্পূর্ণ URL তৈরি করুন যদি রিলেটিভ হয়
                if episode_link and not episode_link.startswith('http'):
                    episode_link = WEBSITE_URL + episode_link
                
                if image_url and not image_url.startswith('http'):
                    image_url = WEBSITE_URL + image_url
                
                episodes.append({
                    'title': title_text,
                    'link': episode_link,
                    'image': image_url,
                    'id': episode_link  # unique identifier
                })
                
            except Exception as e:
                logger.error(f"এপিসোড পার্স করতে ত্রুটি: {e}")
                continue
        
        return episodes
    
    except Exception as e:
        logger.error(f"SunNXT স্ক্র্যাপ করতে ত্রুটি: {e}")
        return []

def send_notification(episode):
    """Telegram এ নোটিফিকেশন পাঠাবে"""
    try:
        message = f"""
🎬 নতুন এপিসোড আপলোড হয়েছে!

📺 নাম: {episode['title']}

🔗 লিংক: {episode['link']}

⏬ ডাউনলোড করতে নিচের মেসেজ ফরওয়ার্ড করুন →
        """
        
        # ছবি সহ মেসেজ পাঠান
        if episode['image']:
            bot.send_photo(
                chat_id=NOTIFICATION_CHANNEL_ID,
                photo=episode['image'],
                caption=message,
                parse_mode='HTML'
            )
        else:
            bot.send_message(
                chat_id=NOTIFICATION_CHANNEL_ID,
                text=message,
                parse_mode='HTML'
            )
        
        logger.info(f"✅ নোটিফিকেশন পাঠানো হয়েছে: {episode['title']}")
        
    except Exception as e:
        logger.error(f"নোটিফিকেশন পাঠাতে ত্রুটি: {e}")

def check_new_episodes():
    """নতুন এপিসোড চেক করবে এবং পাঠাবে"""
    logger.info(f"🔍 চেক করছি... {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    last_episodes = load_last_episodes()
    new_episodes = scrape_sunnxt()
    
    for episode in new_episodes:
        if episode['id'] not in last_episodes:
            logger.info(f"নতুন এপিসোড পাওয়া গেছে: {episode['title']}")
            send_notification(episode)
            last_episodes[episode['id']] = True
    
    save_last_episodes(last_episodes)

def start_scheduler():
    """সিডিউলার শুরু করবে"""
    schedule.every(CHECK_INTERVAL).seconds.do(check_new_episodes)
    
    logger.info(f"✅ Bot 1 (Notifier) শুরু হয়েছে!")
    logger.info(f"প্রতি {CHECK_INTERVAL} সেকেন্ডে চেক করবে...")
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    try:
        start_scheduler()
    except KeyboardInterrupt:
        logger.info("বট বন্ধ করা হয়েছে")
