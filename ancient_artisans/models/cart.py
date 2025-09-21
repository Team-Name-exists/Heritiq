# models/cart.py
from .database import get_cursor, get_connection

class Cart:
    @staticmethod
    def get_cart_id(user_id):
        """Get or create a cart ID for a user"""
        cursor = get_cursor()
        
        # Check if user already has a cart
        cursor.execute("SELECT id FROM carts WHERE user_id = %s", (user_id,))
        cart = cursor.fetchone()
        
        if cart:
            cart_id = cart['id']
        else:
            # Create a new cart
            cursor.execute("INSERT INTO carts (user_id) VALUES (%s)", (user_id,))
            get_connection().commit()
            cart_id = cursor.lastrowid
        
        cursor.close()
        return cart_id
    
    @staticmethod
    def get_cart_items(user_id):
     """Get all items in a user's cart"""
     cursor = get_cursor()
    
     query = """
         SELECT 
            ci.id as cart_item_id, 
            p.id as product_id, 
            p.name, 
            p.image_path,
            ci.quantity, 
            p.price,
            (ci.quantity * p.price) as total_price
        FROM cart_items ci
        JOIN carts c ON ci.cart_id = c.id
        JOIN products p ON ci.product_id = p.id
        WHERE c.user_id = %s
     """
    
     cursor.execute(query, (user_id,))
     items = cursor.fetchall()
     cursor.close()
    
    # Convert Decimal to float for JSON serialization and ensure quantity is int
     for item in items:
         if 'quantity' in item and item['quantity']:
             item['quantity'] = int(item['quantity'])
         if 'price' in item and item['price']:
             item['price'] = float(item['price'])
         if 'total_price' in item and item['total_price']:
             item['total_price'] = float(item['total_price'])
    
     return items
    
    @staticmethod
    def add_to_cart(user_id, product_id, quantity=1):
        """Add an item to the cart"""
        cursor = get_cursor()

        cart_id = Cart.get_cart_id(user_id)
        print(f"[DEBUG] Cart ID for user {user_id}: {cart_id}")

        # Check if item already exists
        cursor.execute(
            "SELECT id, quantity FROM cart_items WHERE cart_id = %s AND product_id = %s",
            (cart_id, product_id)
        )
        existing_item = cursor.fetchone()
        print(f"[DEBUG] Existing item for product {product_id}: {existing_item}")

        if existing_item:
            # Update quantity
            new_quantity = int(existing_item['quantity']) + int(quantity)
            cursor.execute(
                "UPDATE cart_items SET quantity = %s WHERE id = %s",
                (new_quantity, existing_item['id'])
            )
            print(f"[DEBUG] Updated product {product_id} to quantity {new_quantity}")
        else:
            # Add new item
            cursor.execute(
                "INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (%s, %s, %s)",
                (cart_id, product_id, quantity)
            )
            print(f"[DEBUG] Inserted product {product_id} with quantity {quantity}")

        get_connection().commit()
        cursor.close()
        return True
    
    @staticmethod
    def update_cart_item(cart_item_id, quantity):
        """Update cart item quantity"""
        cursor = get_cursor()
        
        if quantity <= 0:
            # Remove item if quantity is 0 or less
            cursor.execute("DELETE FROM cart_items WHERE id = %s", (cart_item_id,))
        else:
            # Update quantity
            cursor.execute(
                "UPDATE cart_items SET quantity = %s WHERE id = %s",
                (quantity, cart_item_id)
            )
        
        get_connection().commit()
        cursor.close()
        return True
    
    @staticmethod
    def remove_from_cart(cart_item_id):
        """Remove an item from the cart"""
        cursor = get_cursor()
        cursor.execute("DELETE FROM cart_items WHERE id = %s", (cart_item_id,))
        get_connection().commit()
        cursor.close()
        return True
    
    @staticmethod
    def clear_cart(user_id):
        """Clear all items from a user's cart"""
        cursor = get_cursor()
        
        # Get cart ID
        cart_id = Cart.get_cart_id(user_id)
        
        # Remove all items
        cursor.execute("DELETE FROM cart_items WHERE cart_id = %s", (cart_id,))
        get_connection().commit()
        cursor.close()
        return True
    
    @staticmethod
    def get_cart_total(user_id):
        """Calculate the total value of the cart"""
        items = Cart.get_cart_items(user_id)

        return sum(item['total_price'] for item in items) if items else 0



