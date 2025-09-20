# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'gG9Yt#7eZ@1wR$Lp8*BvQk2nX!mF^3sJ')
     host="dpg-d37dv6mr433s73em4si0-a.oregon-postgres.render.com",
      database="heritiq",
      user="heritiq_user",
      password="0WPsDiNnqavzeyDGtgInjEXXG9yzc5WI",
      port=5432,
      sslmode="require"
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyC2PhmUXUxTTQnpqSVl1jhVu8nEPlTpji4')
