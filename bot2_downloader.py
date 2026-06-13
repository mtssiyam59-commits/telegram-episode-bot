from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import BOT2_TOKEN, DOWNLOADS_DIR
import yt_dlp
import os
import logging
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DownloadBot:
    def __init__(self):
        self.app = Application.builder().token(BOT2_TOKEN).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """হ্যান্ডলার সেট করবে"""
        self.app.add_handler(CommandHandler('start', self.start))
        self.app.add_handler(CommandHandler('help', self.help_command))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """স্টার্ট কমান্ড"""
        await update.message.reply_text(
            "👋 স্বাগতম!\n\n"
            "আমি এপিসোড ডাউনলোড করতে পারি। Bot 1 থেকে যেকোনো মেসেজ ফরওয়ার্ড করুন এবং আমি ডাউনলোড করে দেব।"
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """হেল্প কমান্ড"""
        await update.message.reply_text(
            "📖 সাহায্য:\n\n"
            "/start - শুরু করুন\n"
            "/help - এই মেসেজ\n\n"
            "লিংক সহ মেসেজ পাঠান এবং আমি ডাউনলোড করব!"
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """ফরওয়ার্ড করা মেসেজ হ্যান্ডেল করবে"""
        try:
            message_text = update.message.text
            
            # লিংক খুঁজবে
            if not ('http://' in message_text or 'https://' in message_text):
                await update.message.reply_text("❌ কোনো লিংক পাওয়া যায়নি। কৃপয়া লিংক সহ মেসেজ পাঠান।")
                return
            
            # লিংক এক্সট্র্যাক্ট করুন
            link = None
            for word in message_text.split():
                if word.startswith('http'):
                    link = word
                    break
            
            if not link:
                await update.message.reply_text("❌ বৈধ লিংক পাওয়া যায়নি।")
                return
            
            # ডাউনলোড শুরু করুন
            await update.message.reply_text("⏳ ডাউনলোড শুরু হয়েছে... অপেক্ষা করুন।")
            
            await self.download_video(update, link)
            
        except Exception as e:
            logger.error(f"মেসেজ হ্যান্ডল করতে ত্রুটি: {e}")
            await update.message.reply_text(f"❌ ত্রুটি হয়েছে: {str(e)}")
    
    async def download_video(self, update: Update, url: str):
        """ভিডিও ডাউনলোড করবে"""
        try:
            # ফাইল নাম তৈরি করুন
            parsed_url = urlparse(url)
            filename = parsed_url.path.split('/')[-1] or 'episode'
            filepath = os.path.join(DOWNLOADS_DIR, f"{filename}.mp4")
            
            # yt-dlp কনফিগারেশন
            ydl_opts = {
                'format': 'best',
                'outtmpl': filepath,
                'quiet': False,
                'no_warnings': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info(f"ডাউনলোড শুরু: {url}")
                info = ydl.extract_info(url, download=True)
                video_file = ydl.prepare_filename(info)
            
            # ফাইল সাইজ চেক করুন
            file_size = os.path.getsize(video_file)
            
            if file_size > 2000000000:  # 2GB এর বেশি হলে
                await update.message.reply_text(
                    f"⚠️ ফাইল বড়! ({file_size / 1024 / 1024 / 1024:.2f} GB)\n"
                    f"💾 ফাইল সংরক্ষিত: `{video_file}`"
                )
                logger.warning(f"বড় ফাইল ডাউনলোড হয়েছে: {video_file}")
            else:
                # ছোট ফাইল হলে Telegram এ পাঠান
                with open(video_file, 'rb') as f:
                    await update.message.reply_video(
                        video=f,
                        caption="✅ ডাউনলোড সম্পন্ন!"
                    )
                
                logger.info(f"✅ ভিডিও পাঠানো হয়েছে: {video_file}")
            
        except Exception as e:
            logger.error(f"ভিডিও ডাউনলোড করতে ত্রুটি: {e}")
            await update.message.reply_text(f"❌ ডাউনলোড ব্যর্থ: {str(e)}")
    
    def run(self):
        """বট চালু করবে"""
        logger.info("✅ Bot 2 (Downloader) শুরু হয়েছে!")
        self.app.run_polling()

if __name__ == '__main__':
    bot = DownloadBot()
    bot.run()
