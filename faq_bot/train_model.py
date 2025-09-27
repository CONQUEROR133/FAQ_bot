#!/usr/bin/env python3
"""
Model training script for FAQ Bot
This script trains the Sentence-BERT model on the FAQ data
"""

import sys
import os
import logging
import time

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Fix imports
from src.faq_loader import FAQLoader
from src.config import config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'cache', 'training.log'), encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main training function"""
    logger.info("🚀 Начало обучения модели...")
    
    try:
        # Initialize FAQ loader
        logger.info("🔧 Инициализация загрузчика FAQ...")
        faq_loader = FAQLoader()
        
        # Load FAQ data
        logger.info("📥 Загрузка FAQ данных...")
        stats = faq_loader.load_faq()
        logger.info(f"✅ Загружено {stats.valid_queries} записей ({stats.total_variations} вариаций)")
        
        # Show loading statistics
        logger.info(f"⏱️  Время загрузки: {stats.loading_time:.2f} секунд")
        
        # Create embeddings (rebuild)
        logger.info("🧠 Создание эмбеддингов...")
        start_time = time.time()
        faq_data, index = faq_loader.create_embeddings(force_rebuild=True)
        embedding_time = time.time() - start_time
        
        logger.info(f"✅ Эмбеддинги созданы и сохранены")
        logger.info(f"⏱️  Время создания эмбеддингов: {embedding_time:.2f} секунд")
        logger.info(f"📊 Размерность векторов: {index.d if index else 'N/A'}")
        logger.info(f"📊 Количество векторов: {index.ntotal if index else 'N/A'}")
        
        # Show final statistics
        if stats.embedding_time > 0:
            logger.info(f"⏱️  Общее время создания эмбеддингов: {stats.embedding_time:.2f} секунд")
        
        logger.info("🎉 Обучение модели завершено успешно!")
        logger.info("📁 Файлы модели сохранены в директории cache/")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Ошибка обучения модели: {e}")
        logger.exception("Подробности ошибки:")
        return 1

if __name__ == "__main__":
    sys.exit(main())