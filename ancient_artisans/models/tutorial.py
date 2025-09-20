from .database import get_cursor, get_connection
import json

class Tutorial:
    @staticmethod
    def create_tutorial(product_id, video_path, description):
        """Create a new tutorial"""
        cursor = get_connection().cursor(dictionary=True)
        
        # If description is a dictionary, convert to JSON string
        if isinstance(description, dict):
            description = json.dumps(description)
        
        query = "INSERT INTO tutorials (product_id, video_path, description) VALUES (%s, %s, %s)"
        
        try:
            cursor.execute(query, (product_id, video_path, description))
            get_connection().commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error creating tutorial: {e}")
            get_connection().rollback()
            return None
        finally:
            cursor.close()
    
    @staticmethod
    def get_tutorial_by_id(tutorial_id):
        """Get tutorial by ID"""
        cursor = get_connection().cursor(dictionary=True)
        query = "SELECT * FROM tutorials WHERE id = %s"
        cursor.execute(query, (tutorial_id,))
        tutorial = cursor.fetchone()
        cursor.close()
        
        # Try to parse description as JSON
        if tutorial and tutorial.get('description'):
            try:
                tutorial['description'] = json.loads(tutorial['description'])
            except:
                pass  # Keep as string if not valid JSON
                
        return tutorial
    
    @staticmethod
    def get_tutorials_by_product(product_id):
        """Get tutorials for a product"""
        cursor = get_connection().cursor(dictionary=True)
        query = "SELECT * FROM tutorials WHERE product_id = %s ORDER BY created_at DESC"
        cursor.execute(query, (product_id,))
        tutorials = cursor.fetchall()
        cursor.close()
        
        # Try to parse description as JSON for each tutorial
        for tutorial in tutorials:
            if tutorial.get('description'):
                try:
                    tutorial['description'] = json.loads(tutorial['description'])
                except:
                    pass  # Keep as string if not valid JSON
                    
        return tutorials
    
    @staticmethod
    def update_tutorial(tutorial_id, **kwargs):
        """Update tutorial information"""
        cursor = get_connection().cursor(dictionary=True)
        
        # Handle description if it's a dictionary
        if 'description' in kwargs and isinstance(kwargs['description'], dict):
            kwargs['description'] = json.dumps(kwargs['description'])
        
        # Build dynamic update query
        fields = []
        values = []
        for key, value in kwargs.items():
            if value is not None:
                fields.append(f"{key} = %s")
                values.append(value)
        
        if not fields:
            return False
            
        values.append(tutorial_id)
        query = f"UPDATE tutorials SET {', '.join(fields)} WHERE id = %s"
        
        try:
            cursor.execute(query, values)
            get_connection().commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating tutorial: {e}")
            get_connection().rollback()
            return False
        finally:
            cursor.close()
    
    @staticmethod
    def delete_tutorial(tutorial_id):
        """Delete a tutorial"""
        cursor = get_connection().cursor()
        query = "DELETE FROM tutorials WHERE id = %s"
        
        try:
            cursor.execute(query, (tutorial_id,))
            get_connection().commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting tutorial: {e}")
            get_connection().rollback()
            return False
        finally:
            cursor.close()


