# models/database.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

# Global connection variable
_connection = None

def init_db(app):
    """Initialize the database connection"""
    # This function is kept for compatibility but doesn't do much now
    return None

def get_connection():
    """Get or create a database connection"""
    global _connection
    if _connection is None or _connection.closed:
        # Use Render's external database URL with SSL
        database_url = os.environ.get('postgresql://heritiq_user:0WPsDiNnqavzeyDGtgInjEXXG9yzc5WI@dpg-d37dv6mr433s73em4si0-a/heritiq')
        
        # Fix the connection string format if needed
        if database_url and database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        
        # If DATABASE_URL is not set, use individual environment variables
        if not database_url:
            database_url = f"postgresql://{os.environ.get('heritiq_user')}:{os.environ.get('0WPsDiNnqavzeyDGtgInjEXXG9yzc5WI')}@{os.environ.get('dpg-d37dv6mr433s73em4si0-a')}:{os.environ.get(' 5432')}/{os.environ.get('heritiq')}"
        
        _connection = psycopg2.connect(
            database_url,
            sslmode="require"
        )
    return _connection

def get_cursor(dictionary=True):
    """Return a cursor, optionally as a DictCursor for dictionary-like results"""
    conn = get_connection()
    if dictionary:
        return conn.cursor(cursor_factory=RealDictCursor)
    else:
        return conn.cursor()
