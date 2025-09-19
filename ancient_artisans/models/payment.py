from .database import mysql
from datetime import datetime
import uuid

class Payment:
    @staticmethod
    def create_payment(order_id, amount, payment_method, status='pending'):
        """Create a new payment record"""
        cursor = mysql.get_cursor()
        transaction_id = f"txn_{uuid.uuid4().hex[:16]}"
        
        query = "INSERT INTO payments (order_id, amount, payment_method, transaction_id, status) VALUES (%s, %s, %s, %s, %s)"
        
        try:
            cursor.execute(query, (order_id, amount, payment_method, transaction_id, status))
            mysql.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error creating payment: {e}")
            return None
        finally:
            cursor.close()
    
    @staticmethod
    def get_payment_by_id(payment_id):
        """Get payment by ID"""
        cursor = mysql.get_cursor()
        query = "SELECT * FROM payments WHERE id = %s"
        cursor.execute(query, (payment_id,))
        payment = cursor.fetchone()
        cursor.close()
        return payment
    
    @staticmethod
    def get_payment_by_order_id(order_id):
        """Get payment by order ID"""
        cursor = mysql.get_cursor()
        query = "SELECT * FROM payments WHERE order_id = %s"
        cursor.execute(query, (order_id,))
        payment = cursor.fetchone()
        cursor.close()
        return payment
    
    @staticmethod
    def update_payment_status(payment_id, status):
        """Update payment status"""
        cursor = mysql.get_cursor()
        query = "UPDATE payments SET status = %s WHERE id = %s"
        
        try:
            cursor.execute(query, (status, payment_id))
            mysql.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating payment status: {e}")
            return False
        finally:
            cursor.close()
    
    @staticmethod
    def update_payment_status_by_order(order_id, status):
        """Update payment status by order ID"""
        cursor = mysql.get_cursor()
        query = "UPDATE payments SET status = %s WHERE order_id = %s"
        
        try:
            cursor.execute(query, (status, order_id))
            mysql.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating payment status: {e}")
            return False
        finally:
            cursor.close()