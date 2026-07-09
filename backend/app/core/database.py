import logging
from motor.motor_asyncio import AsyncIOMotorClient
from backend.app.core.config import get_settings

logger = logging.getLogger(__name__)

class DatabaseService:
    client: AsyncIOMotorClient = None
    db = None

db_service = DatabaseService()

async def connect_to_mongo():
    """Connect to MongoDB at application startup."""
    settings = get_settings()
    logger.info(f"Connecting to MongoDB at {settings.mongodb_uri}...")
    try:
        db_service.client = AsyncIOMotorClient(settings.mongodb_uri)
        db_service.db = db_service.client[settings.mongodb_db_name]
        # Verify connection
        await db_service.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB.")
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        raise e

async def close_mongo_connection():
    """Close MongoDB connection at application shutdown."""
    if db_service.client:
        logger.info("Closing MongoDB connection...")
        db_service.client.close()
        logger.info("MongoDB connection closed.")

def get_db():
    """Dependency to get the database instance."""
    return db_service.db
