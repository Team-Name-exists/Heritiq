# models/database.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor
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
        # Use your PostgreSQL connection details
        _connection = psycopg2.connect(
            host="dpg-d37dv6mr433s73em4si0-a.oregon-postgres.render.com",
            database="heritiq",
            user="heritiq_user",
            password="0WPsDiNnqavzeyDGtgInjEXXG9yzc5WI",
            port=5432,
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
