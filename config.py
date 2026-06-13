import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Tokens
BOT1_TOKEN = os.getenv('BOT1_TOKEN')  # নোটিফিকেশন বট টোকেন
BOT2_TOKEN = os.getenv('BOT2_TOKEN')  # ডাউনলোড বট টোকেন

# Channel/Group IDs (Bot1 যেখানে মেসেজ পাঠাবে)
NOTIFICATION_CHANNEL_ID = int(os.getenv('NOTIFICATION_CHANNEL_ID'))

# Website Details
WEBSITE_URL = 'https://www.sunnxt.com'
CHECK_INTERVAL = 60  # প্রতি 1 মিনিটে চেক করবে

# Storage
DOWNLOADS_DIR = './downloads'  # ডাউনলোড ফোল্ডার তৈরি করবে

os.makedirs(DOWNLOADS_DIR, exist_ok=True)
