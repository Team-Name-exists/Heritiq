# models/database.py
import os
from dotenv import load_dotenv

load_dotenv()

# Global connection variable
_connection = None

def init_db(app):
    """Initialize the database connection (kept for compatibility)"""
    return None

def get_connection():
    """Get or create a database connection"""
    global _connection
    if _connection is None or _connection.closed:
        try:
            import psycopg
            from psycopg.rows import dict_row
            
            # Use environment variables or fallback to your credentials
            database_url = os.environ.get('DATABASE_URL')
            
            if database_url:
                # Fix the connection string format if needed
                if database_url.startswith("postgres://"):
                    database_url = database_url.replace("postgres://", "postgresql://", 1)
                _connection = psycopg.connect(database_url, autocommit=True)
            else:
                # Fallback to individual environment variables
                _connection = psycopg.connect(
                    host="dpg-d37dv6mr433s73em4si0-a.oregon-postgres.render.com",
                    dbname="heritiq",
                    user="heritiq_user",
                    password="0WPsDiNnqavzeyDGtgInjEXXG9yzc5WI",
                    port=5432,
                    sslmode="require",
                    autocommit=True
                )
        except ImportError:
            print("Error: psycopg is not installed. Install it with: pip install psycopg")
            raise
    
    return _connection

def get_cursor(dictionary=True):
    """Return a cursor, optionally as a DictCursor for dictionary-like results"""
    conn = get_connection()
    if dictionary:
        from psycopg.rows import dict_row
        return conn.cursor(row_factory=dict_row)
    else:
        return conn.cursor()
