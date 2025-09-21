# app.py
import os
import uuid
import json
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models.cart import Cart
from flask import send_from_directory
from models.database import get_cursor
from models.database import get_connection
# load env
load_dotenv()

# create app
app = Flask(__name__)
app.config.from_object('config.Config')
app.config['UPLOAD_FOLDER'] = os.path.join(app.config['STATIC_FOLDER'], 'uploads')




# Now import your models (they import models.database, not app - avoids circular import)
from models.user import User
from models.product import Product
from models.cart import Cart
from models.order import Order
from models.message import Message
from models.payment import Payment
from models.tutorial import Tutorial

# Configure Gemini API (optional)
import google.generativeai as genai
GEMINI_API_KEY = app.config.get('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Ensure upload directories exist
def create_upload_dirs():
    upload_dirs = ['products', 'profiles']
    for directory in upload_dirs:
        path = os.path.join(app.config['UPLOAD_FOLDER'], directory)
        os.makedirs(path, exist_ok=True)

create_upload_dirs()

# Helper functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'mp4'}

# Add this function after your imports but before your routes
def create_tables_if_not_exist():
    """Create database tables if they don't exist"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Create tables (PostgreSQL version)
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
        
        conn.commit()
        print("✅ Tables created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
    finally:
        if cursor:
            cursor.close()

# Call this function when the app starts (add this line)
create_tables_if_not_exist()

# Provide a generic /login endpoint so url_for('login') calls resolve (redirects to buyer login)
@app.route('/login', methods=['GET'])
def login():
    """Simple redirect to buyer login (keeps compat with code that references 'login'). 
       You can replace with a combined login view if desired."""
    return redirect(url_for('buyer_login'))


# Routes
@app.route('/')
def index():
    """Home page"""
    featured_products = Product.get_featured_products(limit=8)
    local_artisans = User.get_sellers_with_products(limit=4)
    return render_template('index.html', featured_products=featured_products, local_artisans=local_artisans)


# ---------------- Buyer Login ----------------
@app.route('/buyer_login', methods=['GET', 'POST'])
def buyer_login():
    if request.method == 'POST':
        is_ajax = request.is_json
        data = request.get_json() if is_ajax else request.form

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            msg = "Email and password are required"
            if is_ajax:
                return jsonify({"message": msg}), 400
            flash(msg, "error")
            return redirect(url_for('buyer_login'))

        cur = get_cursor()
        try:
            cur.execute(
                "SELECT id, username, password_hash, user_type FROM users WHERE email = %s",
                (email,)
            )
            user = cur.fetchone()

            if user and check_password_hash(user['password_hash'], password):
                if user['user_type'] != 'buyer':
                    msg = "This account is not registered as a buyer. Please use the seller login."
                    if is_ajax:
                        return jsonify({"message": msg}), 403
                    flash(msg, "error")
                    return redirect(url_for('seller_login'))

                # Login success
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['user_type'] = 'buyer'

                redirect_url = url_for('buyer_dashboard')
                if is_ajax:
                    return jsonify({"message": "Login successful", "redirect": redirect_url}), 200
                flash("Login successful!", "success")
                return redirect(redirect_url)

            else:
                msg = "Invalid email or password"
                if is_ajax:
                    return jsonify({"message": msg}), 401
                flash(msg, "error")
                return redirect(url_for('buyer_login'))

        finally:
            cur.close()

    # GET → show login form
    return render_template('buyer_login.html')


# ---------------- Seller Login ----------------
@app.route('/seller_login', methods=['GET', 'POST'])
def seller_login():
    if request.method == 'POST':
        is_ajax = request.is_json
        data = request.get_json() if is_ajax else request.form

        email = data.get('email')
        password = data.get('password')
        verification_code = data.get('verification_code')

        if not email or not password:
            msg = "Email and password are required"
            if is_ajax:
                return jsonify({"message": msg}), 400
            flash(msg, "error")
            return redirect(url_for('seller_login'))

        if not verification_code:
            msg = "Verification code is required for seller login"
            if is_ajax:
                return jsonify({"message": msg}), 400
            flash(msg, "error")
            return redirect(url_for('seller_login'))

        cur = get_cursor()
        try:
            cur.execute(
                "SELECT id, username, password_hash, user_type FROM users WHERE email = %s",
                (email,)
            )
            user = cur.fetchone()

            if user and check_password_hash(user['password_hash'], password):
                if user['user_type'] != 'seller':
                    msg = "This account is not registered as a seller. Please use the buyer login."
                    if is_ajax:
                        return jsonify({"message": msg}), 403
                    flash(msg, "error")
                    return redirect(url_for('buyer_login'))

                # TODO: Properly validate verification_code from DB or OTP system
                if verification_code != "123456":  # temporary check
                    msg = "Invalid verification code"
                    if is_ajax:
                        return jsonify({"message": msg}), 403
                    flash(msg, "error")
                    return redirect(url_for('seller_login'))

                # Login success
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['user_type'] = 'seller'

                redirect_url = url_for('seller_dashboard')
                if is_ajax:
                    return jsonify({"message": "Login successful", "redirect": redirect_url}), 200
                flash("Login successful!", "success")
                return redirect(redirect_url)

            else:
                msg = "Invalid email or password"
                if is_ajax:
                    return jsonify({"message": msg}), 401
                flash(msg, "error")
                return redirect(url_for('seller_login'))

        finally:
            cur.close()

    # GET → show login form
    return render_template('seller_login.html')


# ---------------- Buyer Registration ----------------
@app.route('/register_buyer', methods=['GET', 'POST'])
def register_buyer():
    """Registration page for buyers"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']

        # Password validation
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('buyer_register.html')

        hashed_password = generate_password_hash(password)

        cur = get_cursor()
        try:
            cur.execute("""
                INSERT INTO users (username, email, password_hash, first_name, last_name, user_type)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (username, email, hashed_password, first_name, last_name, "buyer"))
            get_connection().commit() 
            flash('Buyer account created! Please login.', 'success')
            return redirect(url_for('buyer_login'))
        except Exception as e:
            get_connection().rollback() 
            if "Duplicate entry" in str(e):
                flash('Username or email already exists', 'error')
            else:
                flash('An error occurred while creating your account', 'error')
        finally:
            cur.close()

    return render_template('buyer_register.html')


# ---------------- Seller Registration ----------------
@app.route('/register_seller', methods=['GET', 'POST'])  # ← Correct route
def register_seller():  # ← Correct function name
    """Registration page for sellers"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        bio = request.form.get('bio', '')

        # Password validation
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('seller_register.html')

        hashed_password = generate_password_hash(password)

        cursor = None
        try:
            cursor = get_cursor()
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, first_name, last_name, user_type, bio)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (username, email, hashed_password, first_name, last_name, "seller", bio))
            
            get_connection().commit()
            flash('Seller account created! Please login.', 'success')
            return redirect(url_for('seller_login'))
            
        except Exception as e:
            error_msg = str(e)
            print(f"Seller registration error: {error_msg}")
            
            if get_connection():
                get_connection().rollback()
            
            if "duplicate key" in error_msg.lower() or "unique_violation" in error_msg.lower():
                flash('Username or email already exists', 'error')
            elif "null value" in error_msg.lower():
                flash('Please fill all required fields', 'error')
            else:
                flash('An error occurred while creating your account', 'error')
                
        finally:
            if cursor:
                cursor.close()
    
    return render_template('seller_register.html')

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))


@app.route('/products')
def products():
    """Products listing page"""
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = 12

    filters = {}
    if category:
        filters['category'] = category
    if search:
        filters['search'] = search

    products_list = Product.get_products(filters=filters, page=page, per_page=per_page)
    total_products = Product.get_products_count(filters=filters)
    total_pages = (total_products + per_page - 1) // per_page

    return render_template('products.html',
                           products=products_list,
                           category=category,
                           search=search,
                           page=page,
                           total_pages=total_pages)


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """Product detail page"""
    product = Product.get_product_by_id(product_id)

    if not product:
        flash('Product not found', 'error')
        return redirect(url_for('products'))

    related_products = Product.get_related_products(
        product_id, product.get('category'), limit=4
    )

    return render_template('product_detail.html',
                           product=product,
                           related_products=related_products)


@app.route('/cart/add', methods=['POST'])
def add_to_cart():
    if 'user_id' not in session or session.get('user_type') != 'buyer':
        return jsonify({'success': False, 'error': 'Authentication required'}), 401

    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)

    if not product_id:
        return jsonify({'success': False, 'error': 'Product ID is required'}), 400

    try:
        Cart.add_to_cart(session['user_id'], product_id, quantity)
        return jsonify({'success': True, 'message': 'Item added to cart'})
    except Exception as e:
        print("Error adding to cart:", e)
        return jsonify({'success': False, 'error': 'Failed to add item to cart'}), 500



@app.route('/cart')
def cart():
    if 'user_id' not in session or session.get('user_type') != 'buyer':
        flash('Please login as a buyer to view your cart', 'error')
        return redirect(url_for('login'))

    return render_template('cart.html', user_id=session['user_id'])


# ---------------- API: Get Cart ----------------
@app.route('/api/cart')
def api_cart():
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'error': 'Missing user_id'}), 400

    cart_items = Cart.get_cart_items(user_id)
    items = [{
        'cart_item_id': item['cart_item_id'] if 'cart_item_id' in item else item.get('id'),
        'product_id': item.get('product_id'),
        'name': item.get('name'),
        'quantity': item.get('quantity'),
        'price': float(item.get('price') or 0),
        'total_price': float(item.get('total_price') or 0)
    } for item in cart_items]

    return jsonify({'items': items})


# ---------------- Remove Item ----------------
@app.route('/cart/remove', methods=['POST'])
def remove_from_cart():
    if 'user_id' not in session or session.get('user_type') != 'buyer':
        return jsonify({'success': False, 'error': 'Authentication required'}), 401

    data = request.get_json()
    cart_item_id = data.get('cart_item_id')
    if not cart_item_id:
        return jsonify({'success': False, 'error': 'Cart item ID is required'}), 400

    success = Cart.remove_from_cart(cart_item_id)
    if success:
        return jsonify({'success': True, 'message': 'Item removed from cart'})
    else:
        return jsonify({'success': False, 'error': 'Failed to remove item from cart'}), 500


@app.route('/checkout')
def checkout():
    """Checkout page"""
    if 'user_id' not in session or session.get('user_type') != 'buyer':
        flash('Please login as a buyer to checkout', 'error')
        return redirect(url_for('login'))

    cart_items = Cart.get_cart_items(session['user_id'])

    if not cart_items:
        flash('Your cart is empty', 'error')
        return redirect(url_for('cart'))

    total_amount = sum(item['quantity'] * item['price'] for item in cart_items)

    return render_template('checkout.html',
                           cart_items=cart_items,
                           total_amount=total_amount)


@app.route('/order/create', methods=['POST'])
def create_order():
    """Create a new order"""
    if 'user_id' not in session or session.get('user_type') != 'buyer':
        return jsonify({'success': False, 'error': 'Authentication required'}), 401

    cart_items = Cart.get_cart_items(session['user_id'])

    if not cart_items:
        return jsonify({'success': False, 'error': 'Cart is empty'}), 400

    total_amount = sum(item['quantity'] * item['price'] for item in cart_items)

    # Create order
    order_id = Order.create_order(session['user_id'], total_amount)

    if not order_id:
        return jsonify({'success': False, 'error': 'Failed to create order'}), 500

    # Add order items
    for item in cart_items:
        Order.add_order_item(
            order_id, item.get('product_id'), item.get('quantity'), item.get('price')
        )

    # Clear cart
    Cart.clear_cart(session['user_id'])

    return jsonify({
        'success': True,
        'order_id': order_id,
        'redirect': url_for('payment', order_id=order_id)
    })


@app.route('/payment/<int:order_id>')
def payment(order_id):
    """Payment page"""
    if 'user_id' not in session:
        flash('Please login to complete payment', 'error')
        return redirect(url_for('login'))

    order = Order.get_order_by_id(order_id)

    if not order or order.get('buyer_id') != session['user_id']:
        flash('Order not found', 'error')
        return redirect(url_for('index'))

    return render_template('payment.html', order=order)


@app.route('/payment/process', methods=['POST'])
def process_payment():
    """Process payment"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401

    order_id = request.form.get('order_id')
    payment_method = request.form.get('payment_method')
    amount = request.form.get('amount', type=float)

    if not all([order_id, payment_method, amount]):
        return jsonify({'success': False, 'error': 'Missing payment details'}), 400

    # Create payment record
    payment_id = Payment.create_payment(order_id, amount, payment_method, status='completed')

    if not payment_id:
        return jsonify({'success': False, 'error': 'Payment failed'}), 500

    # Update order status
    Order.update_order_status(order_id, 'confirmed')

    return jsonify({
        'success': True,
        'redirect': url_for('order_confirmation', order_id=order_id)
    })


@app.route('/order/confirmation/<int:order_id>')
def order_confirmation(order_id):
    """Order confirmation page"""
    if 'user_id' not in session:
        flash('Please login to view order confirmation', 'error')
        return redirect(url_for('login'))

    order = Order.get_order_by_id(order_id)

    if not order or order.get('buyer_id') != session['user_id']:
        flash('Order not found', 'error')
        return redirect(url_for('index'))

    order_items = Order.get_order_items(order_id)

    return render_template('order_confirmation.html',
                           order=order,
                           order_items=order_items)


@app.route('/buyer/dashboard')
def buyer_dashboard():
    """Buyer dashboard"""
    if 'user_id' not in session or session.get('user_type') != 'buyer':
        flash('Please login as a buyer to access the dashboard', 'error')
        return redirect(url_for('login'))

    # Get buyer's orders
    orders = Order.get_orders_by_user(session['user_id'])

    # Get unread messages count
    unread_count = Message.get_unread_count(session['user_id'])

    # Get recommended products
    recommended_products = Product.get_products(page=1, per_page=4)

    # Get recent messages
    recent_conversations = Message.get_user_conversations(session['user_id'])

    return render_template('buyer_dashboard.html',
                           orders=orders,
                           unread_messages=unread_count,
                           recommended_products=recommended_products,
                           recent_conversations=recent_conversations)


@app.route('/seller/dashboard')
def seller_dashboard():
    """Seller dashboard"""
    if 'user_id' not in session or session.get('user_type') != 'seller':
        flash('Please login as a seller to access the dashboard', 'error')
        return redirect(url_for('login'))

    # Get seller's products
    products = Product.get_products(filters={'seller_id': session['user_id']}, page=1, per_page=50)

    # Get seller stats
    stats = Order.get_seller_stats(session['user_id'])

    # Temporarily disable messages to fix dashboard
    recent_messages = []

    return render_template('seller_dashboard.html',
                           products=products,
                           stats=stats,
                           recent_messages=recent_messages)

@app.route('/seller/product/add', methods=['GET', 'POST'])
def add_product():
    """Add a new product (seller only)"""
    if 'user_id' not in session or session.get('user_type') != 'seller':
        flash('Please login as a seller to add products', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        # ... [your existing form data handling] ...
        
        # Handle image upload
        image = request.files.get('image')
        if not image or not allowed_file(image.filename):
            flash('Valid product image is required', 'error')
            return render_template('add_product.html')

        # Debug: Print upload folder path
        print(f"UPLOAD_FOLDER: {app.config['UPLOAD_FOLDER']}")
        print(f"Image filename: {image.filename}")

        # secure + unique filename
        filename = secure_filename(image.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"

        # save inside static/uploads/products/
        image_path = os.path.join('products', unique_filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], image_path)
        
        print(f"Image will be saved to: {save_path}")
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)  # ensure folder exists
        image.save(save_path)

        # Verify the file was actually saved
        if os.path.exists(save_path):
            print(f"✅ Image successfully saved to: {save_path}")
            print(f"✅ File size: {os.path.getsize(save_path)} bytes")
        else:
            print(f"❌ Image was NOT saved to: {save_path}")
            flash('Failed to save image', 'error')
            return render_template('add_product.html')

        # Create product
        product_id = Product.create_product(
            seller_id=session['user_id'],
            name=name,
            description=description,
            category=category,
            price=price,
            image_path=image_path,  # stored relative path
            materials=materials,
            dimensions=dimensions,
            weight=weight,
            quantity=quantity
        )

        if product_id:
            flash('Product added successfully!', 'success')
            return redirect(url_for('seller_dashboard'))
        else:
            flash('Failed to add product', 'error')

    # GET request → just show the form
    return render_template('add_product.html')



@app.route('/messages')
def messages():
    """Messages page"""
    if 'user_id' not in session:
        flash('Please login to view messages', 'error')
        return redirect(url_for('login'))

    conversations = Message.get_user_conversations(session['user_id'])

    return render_template('messages.html', conversations=conversations)


@classmethod
def get_user_conversations(cls, user_id):
    """Get all unique conversations for a user with last message details"""
    query = """
        WITH convo AS (
            SELECT DISTINCT ON (
                CASE 
                    WHEN sender_id = %s THEN receiver_id
                    ELSE sender_id
                END
            )
                CASE 
                    WHEN sender_id = %s THEN receiver_id
                    ELSE sender_id
                END AS other_user_id,
                id AS message_id,
                content,
                timestamp,
                sender_id,
                receiver_id
            FROM messages
            WHERE sender_id = %s OR receiver_id = %s
            ORDER BY 
                CASE 
                    WHEN sender_id = %s THEN receiver_id
                    ELSE sender_id
                END,
                timestamp DESC
        ),
        unread_counts AS (
            SELECT sender_id, COUNT(*) AS unread_count
            FROM messages
            WHERE receiver_id = %s AND is_read = false
            GROUP BY sender_id
        )
        SELECT 
            u.id AS other_user_id,
            u.username AS other_username,
            u.profile_picture AS other_profile_picture,
            c.content AS last_message,
            c.timestamp AS last_message_time,
            COALESCE(uc.unread_count, 0) AS unread_count
        FROM convo c
        JOIN users u ON u.id = c.other_user_id
        LEFT JOIN unread_counts uc ON u.id = uc.sender_id
        ORDER BY c.timestamp DESC;
    """
    
    cursor = get_db_cursor()
    cursor.execute(query, (user_id, user_id, user_id, user_id, user_id, user_id))
    conversations = cursor.fetchall()
    
    result = []
    for conv in conversations:
        result.append({
            'other_user_id': conv[0],
            'other_username': conv[1],
            'other_profile_picture': conv[2],
            'last_message': conv[3],
            'last_message_time': conv[4],
            'unread_count': conv[5]
        })
    
    return result



@app.route('/messages/send', methods=['POST'])
def send_message():
    """Send a message"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401

    receiver_id = request.form.get('receiver_id')
    message_text = request.form.get('message')
    product_id = request.form.get('product_id')

    if not receiver_id or not message_text:
        return jsonify({'success': False, 'error': 'Receiver ID and message are required'}), 400

    message_id = Message.create_message(
        session['user_id'], receiver_id, message_text, product_id
    )

    if message_id:
        return jsonify({'success': True, 'message_id': message_id})
    else:
        return jsonify({'success': False, 'error': 'Failed to send message'}), 500


@app.route('/product/<int:product_id>/tutorial/generate')
def generate_tutorial(product_id):
    """Generate AI tutorial for a product"""
    if 'user_id' not in session or session.get('user_type') != 'seller':
        return jsonify({'success': False, 'error': 'Authentication required'}), 401

    # Verify product belongs to seller
    product = Product.get_product_by_id(product_id)

    if not product or product.get('seller_id') != session['user_id']:
        return jsonify({'success': False, 'error': 'Product not found'}), 404

    # Generate tutorial using AI
    tutorial_data = Tutorial.generate_tutorial_description(product)

    if not tutorial_data:
        return jsonify({'success': False, 'error': 'Failed to generate tutorial'}), 500

    # Save tutorial
    tutorial_id = Tutorial.create_tutorial(
        product_id,
        f"tutorial_{product_id}_{uuid.uuid4().hex[:8]}.mp4",  # Placeholder for video
        json.dumps(tutorial_data)
    )

    if tutorial_id:
        return jsonify({
            'success': True,
            'tutorial': tutorial_data,
            'redirect': url_for('view_tutorial', product_id=product_id)
        })
    else:
        return jsonify({'success': False, 'error': 'Failed to save tutorial'}), 500


@app.route('/product/<int:product_id>/tutorial')
def view_tutorial(product_id):
    """View tutorial for a product"""
    product = Product.get_product_by_id(product_id)

    if not product:
        flash('Product not found', 'error')
        return redirect(url_for('products'))

    tutorials = Tutorial.get_tutorials_by_product(product_id)

    return render_template('aitutorial.html', product=product,tutorials=tutorials)


@app.route('/api/check-user-type', methods=['POST'])
def check_user_type():
    """Check if a user exists and return their type"""
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    cursor = get_cursor()
    try:
        cursor.execute("SELECT user_type FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if user:
            return jsonify({'user_type': user['user_type']})
        else:
            return jsonify({'user_type': None})
    except Exception as e:
        print(f"Error checking user type: {e}")
        return jsonify({'error': 'Server error'}), 500
    finally:
        cursor.close()


# Add this debug route to check your database schema
@app.route('/debug/schema')
def debug_schema():
    """Debug route to check database schema"""
    try:
        cursor = get_cursor()
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'users'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        cursor.close()
        return jsonify({'users_columns': columns})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/static/uploads/<path:filename>')
def serve_uploaded_file(filename):
    """Serve uploaded files from static/uploads"""
    return send_from_directory(os.path.join(app.root_path, 'static', 'uploads'), filename)


@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)























