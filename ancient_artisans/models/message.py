from .database import get_cursor, get_connection
from datetime import datetime

class Message:
    @staticmethod
    def send_message(sender_id, receiver_id, message_content):
        """Send a new message"""
        cursor = get_cursor()
        try:
            cursor.execute(
                "INSERT INTO messages (sender_id, receiver_id, message_content) VALUES (%s, %s, %s)",
                (sender_id, receiver_id, message_content)
            )
            get_connection().commit()
            return True
        except Exception as e:
            print(f"Error sending message: {e}")
            return False
        finally:
            cursor.close()

    @staticmethod
    def get_conversation(user1_id, user2_id):
        """Get all messages between two users"""
        cursor = get_cursor()
        try:
            cursor.execute(
                """SELECT m.*, u1.username as sender_username, u2.username as receiver_username 
                   FROM messages m 
                   JOIN users u1 ON m.sender_id = u1.id 
                   JOIN users u2 ON m.receiver_id = u2.id 
                   WHERE (sender_id = %s AND receiver_id = %s) 
                      OR (sender_id = %s AND receiver_id = %s) 
                   ORDER BY created_at ASC""",
                (user1_id, user2_id, user2_id, user1_id)
            )
            messages = cursor.fetchall()
            return messages
        except Exception as e:
            print(f"Error fetching conversation: {e}")
            return []
        finally:
            cursor.close()

    @staticmethod
    def mark_as_read(message_ids):
        """Mark messages as read"""
        if not message_ids:
            return
        
        cursor = get_cursor()
        try:
            placeholders = ', '.join(['%s'] * len(message_ids))
            query = f"UPDATE messages SET is_read = TRUE WHERE id IN ({placeholders})"
            cursor.execute(query, tuple(message_ids))
            get_connection().commit()
        except Exception as e:
            print(f"Error marking messages as read: {e}")
        finally:
            cursor.close()

    @staticmethod
    def get_unread_count(user_id):
        """Get count of unread messages for a user"""
        cursor = get_cursor()
        try:
            cursor.execute(
                "SELECT COUNT(*) as count FROM messages WHERE receiver_id = %s AND is_read = FALSE",
                (user_id,)
            )
            result = cursor.fetchone()
            return result['count'] if result else 0
        except Exception as e:
            print(f"Error getting unread count: {e}")
            return 0
        finally:
            cursor.close()

    @staticmethod
    def get_user_conversations(user_id):
        """Get all conversations for a user with last message and unread count"""
        cursor = get_cursor()
        
        try:
            # First, get all unique conversation partners
            partners_query = """
                SELECT DISTINCT 
                    CASE WHEN sender_id = %s THEN receiver_id ELSE sender_id END as partner_id
                FROM messages 
                WHERE sender_id = %s OR receiver_id = %s
            """
            cursor.execute(partners_query, (user_id, user_id, user_id))
            partners = cursor.fetchall()
            
            conversations = []
            
            for partner in partners:
                partner_id = partner['partner_id']
                
                # Get partner info
                cursor.execute("SELECT id, username FROM users WHERE id = %s", (partner_id,))
                partner_info = cursor.fetchone()
                
                if not partner_info:
                    continue
                
                # Get last message
                last_msg_query = """
                    SELECT message_content, created_at
                    FROM messages 
                    WHERE (sender_id = %s AND receiver_id = %s) 
                       OR (sender_id = %s AND receiver_id = %s)
                    ORDER BY created_at DESC 
                    LIMIT 1
                """
                cursor.execute(last_msg_query, (user_id, partner_id, partner_id, user_id))
                last_message = cursor.fetchone()
                
                # Count unread messages
                unread_query = """
                    SELECT COUNT(*) as count
                    FROM messages 
                    WHERE sender_id = %s AND receiver_id = %s AND is_read = FALSE
                """
                cursor.execute(unread_query, (partner_id, user_id))
                unread_result = cursor.fetchone()
                unread_count = unread_result['count'] if unread_result else 0
                
                conversations.append({
                    'other_user_id': partner_info['id'],
                    'other_username': partner_info['username'],
                    'last_message': last_message['message_content'] if last_message else 'No messages yet',
                    'last_message_time': last_message['created_at'] if last_message else None,
                    'unread_count': unread_count
                })
            
            # Sort by last message time (newest first)
            conversations.sort(key=lambda x: x['last_message_time'] or datetime.min, reverse=True)
            
            return conversations
            
        except Exception as e:
            print(f"Error fetching conversations: {e}")
            return []
            
        finally:
            cursor.close()
