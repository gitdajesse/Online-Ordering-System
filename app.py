from cs50 import SQL
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

app = Flask(__name__)
# Creates the web application

app.config["SESSION_PERMANENT"] = False
# Session expires when browser closes

app.config["SESSION_TYPE"] = "filesystem"
# Stores session data on my server

Session(app)
# Initializes session management

db = SQL("sqlite:///project.db")
# Connects to my SQLite database known as project.db
# Database has three tables: menu table, orders table and order_items table
# Menu table - Stores the food items
# Orders table - Stores each completed order
# Order_items - Stores individual items with an order


@app.route('/', methods = ["GET", "POST"])
def index():
    # User visits my website, sees food picture and "start button"
    # Clicking the button sends the user to the menu page

    return render_template("index.html")


@app.route('/menu', methods = ["GET", "POST"])
def menu():
    # User visits the menu page

    # Sees all the food items from the database
    menu_item = db.execute("SELECT * FROM menu ORDER BY category")

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
    menu_items = db.execute(query, *item_ids)

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
    menu_items = db.execute(query, *item_ids)

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
        menu_items = db.execute(query, *item_ids)

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
        db.execute("INSERT INTO orders (order_number, total_amount, status) VALUES (?, ?, ?)", order_number, total_amount, 'COMPLETED')

        # Gets the new order id from the database above
        order_result = db.execute("SELECT last_insert_rowid() as id")
        order_id = order_result[0]['id']

        # Insert each item into order_items table
        for item in order_items_data:
            db.execute("INSERT INTO order_items (order_id, menu_item_id, quantity, price_at_time) VALUES (?, ?, ?, ?)", order_id, item['menu_item_id'], item['quantity'], item['price_at_time'])

        # Clears the cart from session
        session['cart'] = {}


        # Adds order number to order history in session
        order_history = session.get('order_history', [])

        order_history.append(order_number)

        session['order_history'] = order_history

        order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return render_template("receipt.html", order_number = order_number, order_date = order_date, items = receipt_items, total = total_amount, is_past_order = False)

    else:
        # Looks up order by order number in the database
        orders = db.execute("SELECT * FROM orders WHERE order_number = ?", order_number)

        # Checks if order exists
        if not orders:
            return render_template("error.html", message = "Order not found"), 404

        order = orders[0]

        # Fetches order items with menu details from the database
        order_items = db.execute("SELECT oi.*, m.name, m.image_url FROM order_items oi JOIN menu m ON oi.menu_item_id = m.id WHERE oi.order_id = ?", order['id'])

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
    flash("Item is successfully added to cart!", "order")

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
        flash("Error: No item specified. Please try again." , "remove")
        return redirect("/cart")

    try:
        item_id = int(item_id)
    except (ValueError, TypeError):
        flash("Error: Invalid item ID. Please try again." , "remove")
        return redirect("/cart")

    # Gets current cart from session or creates empty dictionary
    cart = session.get('cart', {})

    # Check if item exists in cart for remove/decrement operations
    if action in ['decrement', 'remove'] and item_id not in cart:
        flash("Error: Item not found in cart.", "remove")
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
        flash("Error: Invalid action.", "remove")
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

    # Gets list of order numbers from session
    order_numbers = session.get('order_history', [])

    # Checks if there are any orders in the order history
    if not order_numbers:
        return render_template("order_history.html", orders = [], has_orders = False)

    # Fetches all orders from database that match the order number
    placeholders = ','.join(['?'] * len(order_numbers))
    query = f"SELECT * FROM orders WHERE order_number IN ({placeholders}) ORDER BY created_at DESC"
    orders = db.execute(query, *order_numbers)

    if not orders:
        return render_template("order_history.html", orders=[], has_orders=False)

    return render_template("order_history.html", orders = orders, has_orders = True)


