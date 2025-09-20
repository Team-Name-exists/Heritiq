# models/user.py
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session
from .database import get_cursor, get_connection


class User:
    @staticmethod
    def create_user(username, email, password, user_type, first_name, last_name, **kwargs):
        """Create a new user"""
        cursor = get_cursor()
        hashed_password = generate_password_hash(password)

        query = """
            INSERT INTO users (username, email, password_hash, user_type, first_name, last_name, 
                             address, city, country, profile_picture, bio)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            username, email, hashed_password, user_type, first_name, last_name,
            kwargs.get('address'), kwargs.get('city'), kwargs.get('country'),
            kwargs.get('profile_picture'), kwargs.get('bio')
        )

        try:
            cursor.execute(query, values)
            get_connection()n.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error creating user: {e}")
            get_connection().rollback()
            return None
        finally:
            cursor.close()

    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        cursor = get_cursor()
        query = "SELECT * FROM users WHERE id = %s"
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()
        cursor.close()
        return user

    @staticmethod
    def get_user_by_email(email):
        """Get user by email"""
        cursor = get_cursor()
        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()
        cursor.close()
        return user

    @staticmethod
    def get_user_by_username(username):
        """Get user by username"""
        cursor = get_cursor()
        query = "SELECT * FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        cursor.close()
        return user

    @staticmethod
    def update_user(user_id, **kwargs):
        """Update user information"""
        cursor = get_cursor()

        fields = []
        values = []
        for key, value in kwargs.items():
            if value is not None:
                fields.append(f"{key} = %s")
                values.append(value)

        if not fields:
            return False

        values.append(user_id)
        query = f"UPDATE users SET {', '.join(fields)}, updated_at = NOW() WHERE id = %s"

        try:
            cursor.execute(query, values)
            get_connection().commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating user: {e}")
            mysql.connection.rollback()
            return False
        finally:
            cursor.close()

    @staticmethod
    def verify_password(stored_password, provided_password):
        """Verify password against hash"""
        return check_password_hash(stored_password, provided_password)

    @staticmethod
    def get_sellers_with_products(limit=10):
        """Get sellers with their product counts"""
        cursor = get_cursor()
        query = """
            SELECT u.*, COUNT(p.id) as product_count 
            FROM users u 
            LEFT JOIN products p ON u.id = p.seller_id 
            WHERE u.user_type = 'seller' 
            GROUP BY u.id 
            ORDER BY product_count DESC 
            LIMIT %s
        """
        cursor.execute(query, (limit,))
        sellers = cursor.fetchall()
        cursor.close()
        return sellers

    @staticmethod
    def login_user(email, password):
        """Login user and return user data if successful"""
        user = User.get_user_by_email(email)
        if user and User.verify_password(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['user_type'] = user['user_type']
            session['email'] = user['email']
            return user
        return None


