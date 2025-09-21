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
        """Get all conversations for a user with last message and unread count"""
        cursor = get_cursor()
    
    # Fixed SQL query with proper grouping
        query = """
            SELECT 
                u.id as other_user_id,
                u.username as other_username,
                COALESCE(last_msg.message_content, 'No messages yet') as last_message,
                COALESCE(last_msg.created_at, NOW()) as last_message_time,
                COALESCE(unread.count, 0) as unread_count
            FROM users u
            JOIN (
                -- Get all unique conversation partners
                SELECT DISTINCT 
                CASE WHEN sender_id = %s THEN receiver_id ELSE sender_id END as partner_id
            FROM messages 
            WHERE sender_id = %s OR receiver_id = %s
        ) partners ON u.id = partners.partner_id
        LEFT JOIN LATERAL (
            -- Get the last message for each conversation
            SELECT message_content, created_at
            FROM messages 
            WHERE (sender_id = %s AND receiver_id = u.id) 
               OR (sender_id = u.id AND receiver_id = %s)
            ORDER BY created_at DESC 
            LIMIT 1
        ) last_msg ON TRUE
        LEFT JOIN (
            -- Count unread messages from each partner
            SELECT sender_id, COUNT(*) as count
            FROM messages 
            WHERE receiver_id = %s AND is_read = FALSE
            GROUP BY sender_id
        ) unread ON u.id = unread.sender_id
        WHERE u.id != %s
        ORDER BY last_message_time DESC
    """
    
    try:
        cursor.execute(query, (
            user_id, user_id, user_id,  # For partners subquery
            user_id, user_id,           # For last_msg subquery
            user_id,                    # For unread subquery
            user_id                     # For final WHERE clause
        ))
        
        conversations = cursor.fetchall()
        return conversations
        
    except Exception as e:
        print(f"Error fetching conversations: {e}")
        return []
        
    finally:
        cursor.close()
    
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

