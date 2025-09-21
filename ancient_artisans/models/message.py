# models/message.py
from .database import get_connection, get_cursor
from psycopg.rows import dict_row  # Add this import

class Message:
    @staticmethod
    def create_message(sender_id, receiver_id, message, product_id=None):
        """Create a new message"""
        cursor = get_cursor()  # ✅ Use get_cursor() instead of direct connection
        query = "INSERT INTO messages (sender_id, receiver_id, product_id, message) VALUES (%s, %s, %s, %s)"
        
        try:
            cursor.execute(query, (sender_id, receiver_id, product_id, message))
            get_connection().commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error creating message: {e}")
            get_connection().rollback()
            return None
        finally:
            cursor.close()
    
    @staticmethod
    def get_message_by_id(message_id):
        """Get message by ID"""
        cursor = get_cursor()  # ✅ Use get_cursor()
        query = "SELECT * FROM messages WHERE id = %s"
        cursor.execute(query, (message_id,))
        message = cursor.fetchone()
        cursor.close()
        return message
    
    @staticmethod
    def get_conversation(user1_id, user2_id, page=1, per_page=20):
        """Get conversation between two users"""
        cursor = get_cursor()  # ✅ Use get_cursor()
        query = """
            SELECT m.*, u.username as sender_name 
            FROM messages m 
            JOIN users u ON m.sender_id = u.id 
            WHERE (m.sender_id = %s AND m.receiver_id = %s) 
               OR (m.sender_id = %s AND m.receiver_id = %s) 
            ORDER BY m.created_at ASC 
            LIMIT %s OFFSET %s
        """
        offset = (page - 1) * per_page
        cursor.execute(query, (user1_id, user2_id, user2_id, user1_id, per_page, offset))
        messages = cursor.fetchall()
        cursor.close()
        return messages
    
    @staticmethod
    def get_user_conversations(user_id):
        """Get all conversations for a user (with last message + unread count)"""
        cursor = get_cursor()  # ✅ Use get_cursor() instead of direct connection
        query = """
            SELECT 
                CASE 
                    WHEN m.sender_id = %s THEN m.receiver_id 
                    ELSE m.sender_id 
                END as other_user_id,
                u.username as other_username,
                MAX(m.created_at) as last_message_time,
                SUBSTRING(
                    (SELECT message FROM messages 
                     WHERE (sender_id = %s AND receiver_id = u.id) 
                        OR (sender_id = u.id AND receiver_id = %s) 
                     ORDER BY created_at DESC LIMIT 1),
                    1, 50
                ) as last_message,
                SUM(CASE WHEN m.receiver_id = %s AND m.is_read = FALSE THEN 1 ELSE 0 END) as unread_count
            FROM messages m
            JOIN users u ON u.id = CASE 
                WHEN m.sender_id = %s THEN m.receiver_id 
                ELSE m.sender_id 
            END
            WHERE m.sender_id = %s OR m.receiver_id = %s
            GROUP BY other_user_id, other_username
            ORDER BY last_message_time DESC
        """
        cursor.execute(query, (user_id, user_id, user_id, user_id, user_id, user_id, user_id))
        conversations = cursor.fetchall()
        cursor.close()
        return conversations
    
    @staticmethod
    def mark_as_read(sender_id, receiver_id):
        """Mark messages as read"""
        cursor = get_cursor()  # ✅ Use get_cursor()
        query = "UPDATE messages SET is_read = TRUE WHERE sender_id = %s AND receiver_id = %s AND is_read = FALSE"
        
        try:
            cursor.execute(query, (sender_id, receiver_id))
            get_connection().commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error marking messages as read: {e}")
            get_connection().rollback()
            return False
        finally:
            cursor.close()
    
    @staticmethod
    def get_unread_count(user_id):
        """Get count of unread messages for a user"""
        cursor = get_cursor()  # ✅ Use get_cursor()
        query = "SELECT COUNT(*) as count FROM messages WHERE receiver_id = %s AND is_read = FALSE"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        cursor.close()
        return result['count'] if result else 0
