import asyncio
import logging
import aiohttp
import html
from telegram import Bot
from telegram.error import TelegramError

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

TOKEN = '7687199674:AAHYhMvZMCmyFEBm7DaerfhQLOvKJuM6qtI'
CHAT_ID = '@api_robot_developer'
NEWSDATA_API_KEY = 'pub_b1fb50f5c7e5458baa7bdac622282b2e'

async def fetch_khmer_news(session: aiohttp.ClientSession):
    url = "https://newsdata.io/api/1/latest"
    params = {
        'country': 'kh',
        'language': 'km',
        'apikey': NEWSDATA_API_KEY
    }

    try:
        async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=15)) as response:
            if response.status == 200:
                data = await response.json()
                articles = [a for a in data.get('results', []) if a.get('image_url')]
                logger.info(f"Fetched {len(articles)} articles with images.")
                return articles
            else:
                logger.error(f"NewsData API Error: {response.status}")
                return []
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        return []

def format_caption(article):
    title = html.escape(article.get('title', 'No title'))
    source = html.escape(article.get('source_id', 'Unknown Source').upper())
    url = article.get('link', '')
    description = article.get('description', '')

    if description and len(description) > 200:
        description = description[:197] + "..."

    description = html.escape(description)

    caption = (
        f"\U0001f4f0 <b>CAMBODIA NEWS</b>\n\n"
        f"<b>{title}</b>\n\n"
        f"{description}\n\n"
        f"\U0001f310 Source: {source}\n"
        f"<a href='{url}'>Read Full Article</a>"
    )
    return caption

async def main():
    if not TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set!")
        return
    if not NEWSDATA_API_KEY:
        logger.error("NEWSDATA_API_KEY not set!")
        return

    bot = Bot(token=TOKEN)

    async with aiohttp.ClientSession() as session:
        articles = await fetch_khmer_news(session)

        if not articles:
            logger.warning("No articles found. Exiting.")
            return

        article = articles[0]
        image_url = article.get('image_url')
        caption_text = format_caption(article)

        try:
            await bot.send_photo(
                chat_id=CHAT_ID,
                photo=image_url,
                caption=caption_text,
                parse_mode='HTML'
            )
            logger.info(f"Sent: {article.get('title')[:50]}...")
        except TelegramError as e:
            logger.error(f"Telegram Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
