import asyncio
import logging
from contextlib import asynccontextmanager
from aiogram import Dispatcher, Bot
from aiohttp import web
from app.api.routes import setup_routes
from app.middleware.cors import setup_cors
from app.middleware.error_handler import setup_error_handlers
from app.tasks.scheduler import setup_scheduler
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
bot: Optional[Bot] = None
dp: Optional[Dispatcher] = None
scheduler = None

@asynccontextmanager
async def lifespan(app):
    # Startup
    global bot, dp, scheduler
    
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()
    
    scheduler = setup_scheduler()
    scheduler.start()
    
    logger.info("✅ Application started")
    yield
    
    # Shutdown
    if scheduler:
        scheduler.shutdown()
    if bot:
        await bot.session.close()
    logger.info("❌ Application stopped")

async def create_app():
    app = web.Application()
    
    # Setup middleware
    setup_cors(app)
    setup_error_handlers(app)
    
    # Setup routes
    setup_routes(app)
    
    return app

if __name__ == "__main__":
    app = asyncio.run(create_app())
    web.run_app(app, host=settings.HOST, port=settings.PORT)
