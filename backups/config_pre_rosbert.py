import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
    DB_PATH = "analytics.db"
    FAQ_FILE = "faq.json"
    EMBEDDINGS_FILE = "faq_embeddings.pkl"
    INDEX_FILE = "faq_index.faiss"
    SIMILARITY_THRESHOLD = 0.73
    MODEL_NAME = "ai-forever/ru-en-RoSBERTa"
    
    # Настройки сети и стабильности
    REQUEST_TIMEOUT = 30  # секунд
    CONNECT_TIMEOUT = 30  # секунд
    READ_TIMEOUT = 30     # секунд
    
    # Настройки повторных попыток
    MAX_RETRIES = 3       # максимальное количество повторов
    RETRY_DELAY = 1       # задержка между повторами (секунд)
    
    # Аутентификация
    ACCESS_PASSWORD = os.getenv("ACCESS_PASSWORD", "1337")  # Moved to env for security
    
    BLOCKED_WORDS = [
        "хуй", "пизда", "ебан", "гандон", "пидор", "бля",
        "сука", "мудак", "долбоеб", "уебан", "залупа"
    ]

config = Config()