import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def create_database():
    """Create the database and tables if they don't exist."""
    connection = None
    cursor = None
    try:
        # Connect to PostgreSQL (without specifying a database first)
        connection = psycopg2.connect(
            host=os.getenv('DB_HOST', 'dpg-d37dv6mr433s73em4si0-a.oregon-postgres.render.com'),
            user=os.getenv('DB_USER', 'heritiq_user'),
            password=os.getenv('DB_PASSWORD', '0WPsDiNnqavzeyDGtgInjEXXG9yzc5WI'),
            port=os.getenv('DB_PORT', 5432),
            sslmode="require"
        )
        
        connection.autocommit = True
        cursor = connection.cursor()
        
        # Create database if it doesn't exist
        db_name = os.getenv('DB_NAME', 'heritiq')
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f"CREATE DATABASE {db_name}")
            print(f"✅ Database '{db_name}' created successfully!")
        
        # Close initial connection and reconnect to the new database
        cursor.close()
        connection.close()
        
        # Reconnect to the specific database
        connection = psycopg2.connect(
            host=os.getenv('DB_HOST', 'dpg-d37dv6mr433s73em4si0-a.oregon-postgres.render.com'),
            database=db_name,
            user=os.getenv('DB_USER', 'heritiq_user'),
            password=os.getenv('DB_PASSWORD', '0WPsDiNnqavzeyDGtgInjEXXG9yzc5WI'),
            port=os.getenv('DB_PORT', 5432),
            sslmode="require"
        )
        
        cursor = connection.cursor()
        
        # Create tables
        tables = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                user_type VARCHAR(10) CHECK (user_type IN ('buyer', 'seller')) NOT NULL,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                address TEXT,
                city VARCHAR(50),
                country VARCHAR(50),
                profile_picture VARCHAR(255),
                bio TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                seller_id INT NOT NULL,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                category VARCHAR(50) NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                ai_suggested_price DECIMAL(10, 2),
                image_path VARCHAR(255) NOT NULL,
                materials TEXT,
                dimensions VARCHAR(100),
                weight DECIMAL(10, 2),
                quantity INT DEFAULT 1,
                is_available BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (seller_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS carts (
                id SERIAL PRIMARY KEY,
                user_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS cart_items (
                id SERIAL PRIMARY KEY,
                cart_id INT NOT NULL,
                product_id INT NOT NULL,
                quantity INT NOT NULL DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cart_id) REFERENCES carts(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                sender_id INT NOT NULL,
                receiver_id INT NOT NULL,
                product_id INT,
                message TEXT NOT NULL,
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                buyer_id INT NOT NULL,
                total_amount DECIMAL(10, 2) NOT NULL,
                status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'shipped', 'delivered', 'cancelled')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (buyer_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS order_items (
                id SERIAL PRIMARY KEY,
                order_id INT NOT NULL,
                product_id INT NOT NULL,
                quantity INT NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS payments (
                id SERIAL PRIMARY KEY,
                order_id INT NOT NULL,
                amount DECIMAL(10, 2) NOT NULL,
                payment_method VARCHAR(50) NOT NULL,
                transaction_id VARCHAR(255),
                status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'failed')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS tutorials (
                id SERIAL PRIMARY KEY,
                product_id INT NOT NULL,
                video_path VARCHAR(255) NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            )
            """
        ]
        
        for table in tables:
            cursor.execute(table)
        
        # Create a function to update the updated_at timestamp
        cursor.execute("""
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ language 'plpgsql';
        """)
        
        # Create triggers for updated_at
        for table in ['users', 'products']:
            cursor.execute(f"""
                DROP TRIGGER IF EXISTS set_updated_at ON {table};
                CREATE TRIGGER set_updated_at
                    BEFORE UPDATE ON {table}
                    FOR EACH ROW
                    EXECUTE FUNCTION update_updated_at_column();
            """)
        
        connection.commit()
        print("✅ Database and tables created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
    finally:
        if connection:
            if cursor:
                cursor.close()
            connection.close()

if __name__ == '__main__':
    create_database()
