# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'gG9Yt#7eZ@1wR$Lp8*BvQk2nX!mF^3sJ')
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '8194')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'artisan')
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyC2PhmUXUxTTQnpqSVl1jhVu8nEPlTpji4')