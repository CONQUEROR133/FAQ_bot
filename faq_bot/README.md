# FAQ Bot

A Telegram bot for answering frequently asked questions with AI-powered search capabilities.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. Clone or download the repository
2. Navigate to the project directory:
   ```bash
   cd faq_bot
   ```

3. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Create a `.env` file in the project root directory
2. Add the following environment variables to the `.env` file:
   ```
   BOT_TOKEN=your_telegram_bot_token
   ADMIN_ID=your_telegram_user_id
   DB_PATH=data/analytics.db
   FAQ_FILE=data/faq.json
   EMBEDDINGS_FILE=cache/embeddings.pkl
   INDEX_FILE=cache/faiss_index.bin
   ```

## Running the Bot

```bash
python src/main.py
```

## Project Structure

- `src/` - Source code
  - `main.py` - Entry point
  - `config.py` - Configuration management
  - `database.py` - Database operations
  - `faq_loader.py` - FAQ data loading and search
  - `handlers.py` - Telegram message handlers
  - `auth_middleware.py` - Authentication middleware
  - `security_middleware.py` - Security middleware
  - `performance_manager.py` - Performance tracking
- `data/` - Data files (faq.json, analytics.db)
- `cache/` - Cache files (embeddings, FAISS index)
- `templates/` - Response templates

## Dependencies

- aiogram - Telegram Bot API framework
- faiss-cpu - Similarity search library
- numpy - Numerical computing
- sentence-transformers - Sentence embeddings