# models/database.py
from flask_mysqldb import MySQL
from MySQLdb.cursors import DictCursor
import os
from dotenv import load_dotenv

load_dotenv()

mysql = MySQL()

def init_db(app):
    """Initialize the database with the Flask app"""
    app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
    app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
    app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', '8194')
    app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'artisan')
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
    
    mysql.init_app(app)
    return mysql

def get_cursor(dictionary=True):
    """Return a cursor, optionally as a DictCursor for dictionary-like results"""
    if dictionary:
        return mysql.connection.cursor(DictCursor)
    else:
        return mysql.connection.cursor()