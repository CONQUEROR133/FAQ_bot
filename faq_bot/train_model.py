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

try:
    # Fix imports
    from src.faq_loader import FAQLoader
    from src.config import config
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you've installed all dependencies with: pip install -r requirements.txt")
    sys.exit(1)

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
    logger.info("🚀 Starting model training...")
    
    try:
        # Initialize FAQ loader
        logger.info("🔧 Initializing FAQ loader...")
        faq_loader = FAQLoader()
        
        # Load FAQ data
        logger.info("📥 Loading FAQ data...")
        stats = faq_loader.load_faq()
        logger.info(f"✅ Loaded {stats.valid_queries} entries ({stats.total_variations} variations)")
        
        # Show loading statistics
        logger.info(f"⏱️  Loading time: {stats.loading_time:.2f} seconds")
        
        # Create embeddings (rebuild)
        logger.info("🧠 Creating embeddings...")
        start_time = time.time()
        faq_data, index = faq_loader.create_embeddings(force_rebuild=True)
        embedding_time = time.time() - start_time
        
        logger.info(f"✅ Embeddings created and saved")
        logger.info(f"⏱️  Embedding creation time: {embedding_time:.2f} seconds")
        logger.info(f"📊 Vector dimension: {index.d if index else 'N/A'}")
        logger.info(f"📊 Number of vectors: {index.ntotal if index else 'N/A'}")
        
        # Show final statistics
        if stats.embedding_time > 0:
            logger.info(f"⏱️  Total embedding time: {stats.embedding_time:.2f} seconds")
        
        logger.info("🎉 Model training completed successfully!")
        logger.info("📁 Model files saved in cache/ directory")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Model training error: {e}")
        logger.exception("Error details:")
        return 1

if __name__ == "__main__":
    sys.exit(main())