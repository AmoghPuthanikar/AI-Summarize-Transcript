import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev_key_secret')
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/ai_transcription_db')
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500 MB limit
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
