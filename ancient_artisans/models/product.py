# models/product.py
from .database import get_cursor, get_connection
from datetime import datetime

class Product:
    @staticmethod
    def create_product(seller_id, name, description, category, price, image_path, **kwargs):
        """Create a new product"""
        cursor = get_cursor()

        query = """
            INSERT INTO products (seller_id, name, description, category, price, image_path,
                                materials, dimensions, weight, quantity, ai_suggested_price)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        values = (
            seller_id, name, description, category, price, image_path,
            kwargs.get('materials'), kwargs.get('dimensions'), kwargs.get('weight'),
            kwargs.get('quantity', 1), kwargs.get('ai_suggested_price')
        )

        try:
            cursor.execute(query, values)
            result = cursor.fetchone()
            product_id = result['id'] if result else None
            return product_id
        except Exception as e:
            print(f"Error creating product: {e}")
            return None
        finally:
            cursor.close()

    @staticmethod
    def get_product_by_id(product_id):
        """Get product by ID"""
        cursor = get_cursor()
        query = """
            SELECT p.*, u.username as seller_name, u.bio as seller_bio
            FROM products p 
            JOIN users u ON p.seller_id = u.id 
            WHERE p.id = %s
        """
        cursor.execute(query, (product_id,))
        product = cursor.fetchone()
        cursor.close()
        return product

    @staticmethod
    def get_products(filters=None, page=1, per_page=10):
        """Get paginated list of products with optional filters"""
        query = "SELECT * FROM products WHERE 1=1"
        params = []

        if filters and 'category' in filters:
            query += " AND category=%s"
            params.append(filters['category'])

        # Pagination
        offset = (page - 1) * per_page
        query += " LIMIT %s OFFSET %s"
        params.extend([per_page, offset])

        cursor = get_cursor()
        cursor.execute(query, params)
        products = cursor.fetchall()
        cursor.close()

        return products

    @staticmethod
    def get_products_count(filters=None):
        """Get count of products with optional filters"""
        cursor = get_cursor()
        query = "SELECT COUNT(*) as total FROM products p WHERE p.is_available = TRUE"
        params = []

        if filters:
            if filters.get('category'):
                query += " AND p.category = %s"
                params.append(filters['category'])
            if filters.get('search'):
                query += " AND (p.name LIKE %s OR p.description LIKE %s)"
                params.extend([f"%{filters['search']}%", f"%{filters['search']}%"])
            if filters.get('seller_id'):
                query += " AND p.seller_id = %s"
                params.append(filters['seller_id'])

        cursor.execute(query, params)
        result = cursor.fetchone()
        cursor.close()
        return result['total'] if result else 0

    @staticmethod
    def update_product(product_id, **kwargs):
        """Update product information"""
        cursor = get_cursor()

        fields = []
        values = []
        for key, value in kwargs.items():
            if value is not None:
                fields.append(f"{key} = %s")
                values.append(value)

        if not fields:
            return False

        values.append(product_id)
        query = f"UPDATE products SET {', '.join(fields)}, updated_at = NOW() WHERE id = %s"

        try:
            cursor.execute(query, values)
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating product: {e}")
            return False
        finally:
            cursor.close()

    @staticmethod
    def delete_product(product_id):
        """Soft delete a product (set is_available = False)"""
        cursor = get_cursor()
        query = "UPDATE products SET is_available = FALSE WHERE id = %s"

        try:
            cursor.execute(query, (product_id,))
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting product: {e}")
            return False
         finally:
            cursor.close()
    
   @staticmethod
    def get_related_products(product_id, category, limit=4):
        """Get related products by category"""
        cursor = get_cursor()
        query = """
            SELECT p.*, u.username as seller_name 
            FROM products p 
            JOIN users u ON p.seller_id = u.id 
            WHERE p.category = %s AND p.id != %s AND p.is_available = TRUE 
            ORDER BY RANDOM() 
            LIMIT %s
        """
        cursor.execute(query, (category, product_id, limit))
        products = cursor.fetchall()
        cursor.close()
        return products

    @staticmethod
    def update_ai_suggested_price(product_id, suggested_price):
        """Update AI suggested price for a product"""
        cursor = get_cursor()
        query = "UPDATE products SET ai_suggested_price = %s WHERE id = %s"

        try:
            cursor.execute(query, (suggested_price, product_id))
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating AI suggested price: {e}")
            return False
        finally:
            cursor.close()

    @staticmethod
    def get_featured_products(limit=8):
        """Get featured products (latest available)"""
        cursor = get_cursor()
        query = """
            SELECT p.*, u.username as seller_name 
            FROM products p 
            JOIN users u ON p.seller_id = u.id 
            WHERE p.is_available = TRUE
            ORDER BY p.created_at DESC 
            LIMIT %s
        """
        cursor.execute(query, (limit,))
        products = cursor.fetchall()
        cursor.close()
        return products
