import sqlite3
# Simple way to interact with SQLite database.

from flask import Flask, redirect, render_template, session, request, url_for
# Flask - Web framework that creates the application
# Redirect - Sends the user to different pages.
# Render_template - Displays HTML files from the templates folder
# Session - Remembers user data across page visits.
# Request - Gets data sent form forms
# URL_for - Createscorrect URL's for static files.

from flask import flash
# Flash - Displays messages to the user

from flask_session import Session
# Manages server side sessions

from datetime import datetime
# Gets current date and time

from collections import defaultdict
# Creates a dictionary with default values

from werkzeug.security import check_password_hash, generate_password_hash
# Provides functions to hash passwords and check hashed passwords

app = Flask(__name__)
# Creates the web application

app.secret_key = "supersecretkey"

app.config["SESSION_PERMANENT"] = False
# Session expires when browser closes

app.config["SESSION_TYPE"] = "filesystem"
# Stores session data on my server

Session(app)
# Initializes session management

def get_db():
    conn = sqlite3.connect('project.db')  # Removed sqlite:/// prefix
    conn.row_factory = sqlite3.Row  # This allows dictionary-like access to rows
    return conn
    # Connects to my SQLite database known as project.db
    # Database has three tables: menu table, orders table and order_items table
    # Menu table - Stores the food items
    # Orders table - Stores each completed order
    # Order_items - Stores individual items with an order
    # Users - Stores users information when registering an account


@app.route('/', methods = ["GET", "POST"])
def index():
    # User visits my website, sees food picture and "start button"
    # Clicking the button sends the user to the menu page

    return render_template("index.html")


@app.route('/menu', methods = ["GET", "POST"])
def menu():
    # User visits the menu page

    # Sees all the food items from the database
    db = get_db()
    menu_item = db.execute("SELECT * FROM menu ORDER BY category").fetchall()

    db.close()

    # Groups items by category using defaultdict
    grouped_items = defaultdict(list)

    # Iterates through menu items and appends each item to the appropriate category list in grouped_items
    for item in menu_item:
        grouped_items[item['category']].append(item)

    return render_template("menu.html", grouped_items = grouped_items)

@app.route('/cart', methods = ["GET", "POST"])
def cart():
    # Shopping cart page
    # Create session - cart

    # Gets cart from session
    cart = session.get('cart', {})

    # Check if cart is empty
    if not cart:
        return render_template("cart.html", cart_items = [], cart_empty = True)

    # If cart exists, extracts item IDs from cart keys
    item_ids = list(cart.keys())

    # Query database for all items in cart
    # Placeholder - Comes out like (1, 2, 3)
    placeholders = ','.join(['?'] * len(item_ids))
    # Query - Executed by the SQLite command below
    query = f"SELECT * FROM menu WHERE id IN ({placeholders})"
    # Outcome - ("SELECT * FROM menu WHERE id IN (1, 2, 3)")
    db = get_db()
    menu_items = db.execute(query, item_ids).fetchall()
    db.close()

    # Create a new list
    combined_list = []

    total_amount  = 0

    for menu_item in menu_items:
        item_id = menu_item['id']
        quantity = cart[item_id]
        subtotal = menu_item['price'] * quantity

        combined_item = {
            'id': menu_item['id'],
            'name': menu_item['name'],
            'description': menu_item['description'],
            'price': menu_item['price'],
            'category': menu_item['category'],
            'image_url': menu_item['image_url'],
            'quantity': quantity,
            'subtotal': subtotal
        }

        combined_list.append(combined_item)

        for item in combined_list:
            total_amount = total_amount + item['subtotal']


    return render_template("cart.html", cart_items = combined_list, total = total_amount, cart_empty = False)


@app.route('/summary', methods = ["GET", "POST"])
def summary():
    # Order summary page
    # Has button ("confirm") that sends the user to the receipt page

    # Gets cart from session
    cart = session.get('cart', {})

    # Check if cart is empty
    if not cart:
        return redirect("/cart")

    # If cart exists, extracts item IDs from cart keys
    item_ids = list(cart.keys())

    # Query database for all items in cart
    # Placeholder - Comes out like (1, 2, 3)
    placeholders = ','.join(['?'] * len(item_ids))
    # Query - Executed by the SQLite command below
    query = f"SELECT * FROM menu WHERE id IN ({placeholders})"
    # Outcome - ("SELECT * FROM menu WHERE id IN (1, 2, 3)")
    db = get_db()
    menu_items = db.execute(query, item_ids).fetchall()
    db.close()

    # Create a new list
    combined_list = []

    for menu_item in menu_items:
        item_id = menu_item['id']
        quantity = cart[item_id]
        subtotal = menu_item['price'] * quantity

        combined_item = {
            'id': menu_item['id'],
            'name': menu_item['name'],
            'description': menu_item['description'],
            'price': menu_item['price'],
            'category': menu_item['category'],
            'image_url': menu_item['image_url'],
            'quantity': quantity,
            'subtotal': subtotal
        }

        combined_list.append(combined_item)

        total_amount  = 0

        for item in combined_list:
            total_amount = total_amount + item['subtotal']

    return render_template("summary.html", cart_items = combined_list, total = total_amount)


@app.route('/receipt', methods = ["GET", "POST"])
@app.route('/receipt/<order_number>', methods = ["GET", "POST"])
def receipt(order_number = None):
    # Receipt page
    if request.method == "POST":
        # ADD THIS AUTHENTICATION CHECK RIGHT HERE
        if not session.get('user_id'):
            flash("Please sign in to confirm your order", "warning")
            return redirect("/checkout-start?return_to=/receipt")

        # Gets cart from sesjsion
        cart = session.get('cart', {})

        # Check if cart is empty
        if not cart:
            return redirect("/cart")

        # If cart exists, extracts item IDs from cart keys
        item_ids = list(cart.keys())

        # Query database for all items in cart
        # Placeholder - Comes out like (1, 2, 3)
        placeholders = ','.join(['?'] * len(item_ids))
        # Query - Executed by the SQLite command below
        query = f"SELECT * FROM menu WHERE id IN ({placeholders})"
        # Outcome - ("SELECT * FROM menu WHERE id IN (1, 2, 3)")
        db = get_db()
        menu_items = db.execute(query, item_ids).fetchall()

        total_amount = 0

        # Creates a new list
        order_items_data = []

        # Creates a new list
        receipt_items = []

        for menu_item in menu_items:
            item_id = menu_item['id']
            quantity = cart[item_id]
            price = menu_item['price']
            subtotal = price * quantity
            total_amount += subtotal

            order_items_data.append({
                'menu_item_id': item_id,
                'quantity': quantity,
                'price_at_time': price
            })

            receipt_items.append({
                'name': menu_item['name'],
                'quantity': quantity,
                'price': price,
                'subtotal': subtotal,
                'image_url': menu_item['image_url']
            })

        # Generates unique order number
        order_number = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Inserts order into orders table
        db.execute("INSERT INTO orders (order_number, total_amount, status, user_id) VALUES (?, ?, ?, ?)", (order_number, total_amount, 'COMPLETED', session.get('user_id')))

        # Gets the new order id from the database above
        order_result = db.execute("SELECT last_insert_rowid() as id").fetchone()
        order_id = order_result['id']

        # Insert each item into order_items table
        for item in order_items_data:
            db.execute("INSERT INTO order_items (order_id, menu_item_id, quantity, price_at_time) VALUES (?, ?, ?, ?)", (order_id, item['menu_item_id'], item['quantity'], item['price_at_time']))

        db.commit()
        db.close()

        # Clears the cart from session
        session['cart'] = {}

        order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return render_template("receipt.html", order_number = order_number, order_date = order_date, items = receipt_items, total = total_amount, is_past_order = False)

    else:
        # Looks up order by order number in the database
        db = get_db()
        orders = db.execute("SELECT * FROM orders WHERE order_number = ?", (order_number,)).fetchall()

        # Checks if order exists
        if not orders:
            db.close()
            return render_template("error.html", message = "Order not found"), 404

        order = orders[0]

        # Fetches order items with menu details from the database
        order_items = db.execute("SELECT oi.*, m.name, m.image_url FROM order_items oi JOIN menu m ON oi.menu_item_id = m.id WHERE oi.order_id = ?", (order['id'],)).fetchall()

        db.close()

        total_amount = order['total_amount']

        receipt = []

        for item in order_items:
            receipt.append({
                'name': item['name'],
                'quantity': item['quantity'],
                'price': item['price_at_time'],
                'subtotal': item['quantity'] * item['price_at_time'],
                'image_url': item['image_url']
            })

        order_date = order['created_at']

        return render_template("receipt.html", order_number = order['order_number'], order_date = order_date, items = receipt, total = total_amount, is_past_order = True)


@app.route('/add_to_cart', methods = ['POST'])
def add_cart():
    # Has a button ("order") which sends the user to the Shopping cart page

    # Receives POST request with item_id from the form
    item_id = request.form.get('item_id')
    item_id = int(item_id)

    # Gets current cart from session or creates empty dictionary
    cart = session.get('cart', {})

    # If item already in cart, increases quantity by 1
    if item_id in cart:
        cart[item_id] = cart[item_id] + 1
    # If item not in cart, adds it with quantity 1
    else:
        cart[item_id] = 1

    # Saves cart back to session
    session['cart'] = cart

    session.modified = True

    # Displays flash message to user
    flash("Item is successfully added to cart!", "success")

    return redirect("/cart")


@app.route('/add_more_items')
def add_more():
    # Has button ("add more items") which sends the user back to the menu and add more items

    return redirect ("/menu")


@app.route('/update_cart', methods = ['GET', 'POST'])
def update():
    # Has button ("+")  to add quantity of items
    # Has button ("-")  to add quantity of items
    # Has button ("remove") to remove the items from the shopping cart page


    # Receives POST request with item_id from the form
    item_id = request.form.get('item_id')
    # Receives POST request with action from the form
    action = request.form.get('action')

    if not item_id:
        flash("Error: No item specified. Please try again." , "danger")
        return redirect("/cart")

    try:
        item_id = int(item_id)
    except (ValueError, TypeError):
        flash("Error: Invalid item ID. Please try again." , "danger")
        return redirect("/cart")

    # Gets current cart from session or creates empty dictionary
    cart = session.get('cart', {})

    # Check if item exists in cart for remove/decrement operations
    if action in ['decrement', 'remove'] and item_id not in cart:
        flash("Error: Item not found in cart.", "danger")
        return redirect("/cart")

    # Adds 1 to quantity
    if action == 'increment':
        cart[item_id] = cart.get(item_id, 0) + 1

    # Subtracts 1 from quantity, removes if it becomes 0
    elif action == 'decrement':
        if cart.get(item_id, 0) > 1:
            cart[item_id] -= 1
        else:
            cart.pop(item_id, None)

    # Deletes item completely from cart
    elif action == 'remove':
        cart.pop(item_id, None)
    else:
        flash("Error: Invalid action.", "danger")
        return redirect("/cart")

    session['cart'] = cart

    session.modified = True

    return redirect("/cart")


@app.route('/checkout')
def checkout():
    # Has button ("checkout") that sends the user to the summary page.
    return render_template("summary.html")


@app.route('/order_history', methods = ["GET", "POST"])
def order_history():
    # Order history page

    #Check if user is logged in
    if not session.get('user_id'):
        flash("Please log in to view your order history.", "warning")
        return redirect("/login?return_to=/order_history")
    
    # Get user's orders from database
    db = get_db()

    try:
        orders = db.execute("SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC", (session.get('user_id'),)).fetchall()
    finally:
        db.close()

    # Check if user has any orders
    if not orders:
        return render_template("order_history.html", orders = [], has_orders = False)

    return render_template("order_history.html", orders = orders, has_orders = True)

@app.route('/checkout-start', methods = ["GET", "POST"])
def checkout_start():
    # Gateway page - user chooses login or registration
    return_to = request.args.get('return_to', '/receipt')
    return render_template("gateway.html", return_to = return_to)


@app.route('/login')
def login_page():
    # Display login page
    # If user is already logged in, redirect to menu
    if session.get('user_id'):
        flash("You are already logged in!", "info")
        return redirect("/menu")
    
    return_to = request.args.get('return_to', '/receipt')
    return render_template("login.html", return_to=return_to)


@app.route('/register')
def register_page():
    # Display registration page
    # If user is already logged in, redirect to menu
    if session.get('user_id'):
        flash("You are already logged in!", "info")
        return redirect("/menu")
    
    return_to = request.args.get('return_to', '/receipt')
    return render_template("registration.html", return_to=return_to)

@app.route('/login/submit', methods = ['GET','POST'])
def login_submit():
    # Process login form submission
    # POST request logic
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password') 
        return_to = request.form.get('return_to', '/receipt')

        # Validate input exists
        if not username:
            flash("Username is required.", "danger")
            return redirect("/login")
        if not password:
            flash("Password is required.", "danger")
            return redirect("/login")
        
        # Look Up User in Database
        db = get_db()

        try:
            user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        finally:
            db.close()

        if not user:
            flash("Invalid username or password.", "danger")
            return redirect("/login")
        
        # Verify the Password
        if not check_password_hash(user['password_hash'], password):
            flash("Invalid username or password.", "danger")
            return redirect("/login")
        
        # Create user session
        session ["user_id"] = user['id']
        session["username"] = username

        flash("Successfully logged in!", "success")

        if return_to == '/receipt':
            return redirect("/summary")
        else:
            return redirect(return_to)

    # GET request logic
    else:
        return_to = request.args.get('return_to', '/receipt')
        return render_template("login.html", return_to = return_to)


@app.route('/register/submit', methods = ['POST'])
def register_submit():
    # Process registration form submission
    # POST request logic
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password') 
        confirm_password = request.form.get('confirm_password') 
        return_to = request.form.get('return_to', '/receipt')

        # Validate input exists
        if not username:
            flash("Username is required.", "danger")
            return redirect("/register")
        if not password:
            flash("Password is required.", "danger")
            return redirect("/register")
        if not confirm_password:
            flash("Please confirm your password!.", "danger")
            return redirect("/register")
        
        # Check That Passwords Match
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect("/register")
        
        # Check Password Length
        if len(password) < 6:
            flash("Password must be at least 6 characters", "danger")
            return redirect("/register")

        # Check If Username Already Exists
        db = get_db()

        try:
            user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        finally:
            db.close()

        if user:
            flash("Username already taken. Please choose another.", "danger")
            return redirect("/register")
        
        # Hash the Password
        hashed_password = generate_password_hash(password)

        # Insert the New User
        db = get_db()

        try:
            registered = db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed_password))

            db.commit()
        finally:
            db.close()

        # Verify Insertion Worked
        if registered.rowcount == 0:
            flash("Registration failed. Please try again.", "danger")
        else:
            flash("Account created successfully! Please log in.", "success")

        return redirect(f"/login?return_to={return_to}")
    
    # GET request logic
    else:
        return_to = request.args.get('return_to', '/receipt')
        return render_template("registration.html", return_to = return_to)

if __name__ == '__main__':
    app.run(debug = True)
