from .database import mysql

class Order:
    @staticmethod
    def create_order(buyer_id, total_amount, status='pending'):
        """Create a new order"""
        cursor = mysql.connection.cursor(dictionary=True)
        query = "INSERT INTO orders (buyer_id, total_amount, status) VALUES (%s, %s, %s)"
        
        try:
            cursor.execute(query, (buyer_id, total_amount, status))
            mysql.connection.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error creating order: {e}")
            return None
        finally:
            cursor.close()
    
    @staticmethod
    def get_order_by_id(order_id):
        """Get order by ID"""
        cursor = mysql.connection.cursor(dictionary=True)
        query = "SELECT * FROM orders WHERE id = %s"
        cursor.execute(query, (order_id,))
        order = cursor.fetchone()
        cursor.close()
        return order
    
    @staticmethod
    def get_orders_by_user(buyer_id):
        """Get all orders for a buyer"""
        cursor = mysql.connection.cursor(dictionary=True)
        query = "SELECT * FROM orders WHERE buyer_id = %s ORDER BY created_at DESC"
        cursor.execute(query, (buyer_id,))
        orders = cursor.fetchall()
        cursor.close()
        return orders
    
    @staticmethod
    def update_order_status(order_id, status):
        """Update order status"""
        cursor = mysql.connection.cursor()
        query = "UPDATE orders SET status = %s WHERE id = %s"
        
        try:
            cursor.execute(query, (status, order_id))
            mysql.connection.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating order status: {e}")
            return False
        finally:
            cursor.close()
    
    @staticmethod
    def add_order_item(order_id, product_id, quantity, price):
        """Add item to order"""
        cursor = mysql.connection.cursor()
        query = "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)"
        
        try:
            cursor.execute(query, (order_id, product_id, quantity, price))
            mysql.connection.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error adding order item: {e}")
            return None
        finally:
            cursor.close()
    
    @staticmethod
    def get_order_items(order_id):
        """Get items for an order"""
        cursor = mysql.connection.cursor(dictionary=True)
        query = """
            SELECT oi.*, p.name, p.image_path 
            FROM order_items oi 
            JOIN products p ON oi.product_id = p.id 
            WHERE oi.order_id = %s
        """
        cursor.execute(query, (order_id,))
        items = cursor.fetchall()
        cursor.close()
        return items
    
    @staticmethod
    def get_seller_stats(seller_id):
        """Get order statistics for a seller"""
        cursor = mysql.connection.cursor(dictionary=True)
        query = """
            SELECT 
                COUNT(DISTINCT o.id) as total_orders, 
                SUM(oi.quantity) as total_items_sold,
                SUM(oi.quantity * oi.price) as total_revenue
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            JOIN orders o ON oi.order_id = o.id
            WHERE p.seller_id = %s AND o.status != 'cancelled'
        """
        cursor.execute(query, (seller_id,))
        stats = cursor.fetchone()
        cursor.close()
        return stats
