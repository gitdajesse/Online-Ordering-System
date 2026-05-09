# African Cafe - Online Food Ordering System

#### Video Demo: <https://youtu.be/EUQgwZZL4ls>

## Description

African Cafe is a full-stack web application that allows customers to browse a restaurant menu, add items to a shopping cart, manage quantities, checkout, and view order history. The application is built using Flask (Python backend), SQLite (database), HTML/CSS with Bootstrap (frontend), and JavaScript for interactive features.

## Project Structure

### Backend Files

**app.py** - Main Flask application containing all route handlers:
- `/` - Home page route displaying welcome screen
- `/menu` - Displays menu items grouped by category from database
- `/cart` - Shopping cart page with quantity management
- `/summary` - Order summary before final confirmation
- `/receipt` - Generates unique order receipt after checkout
- `/add_to_cart` - Handles adding items to session cart
- `/update_cart` - Processes increment/decrement/remove actions
- `/order_history` - Displays past orders from database

**Key Functions in app.py:**
- `index()` - Renders home page
- `menu()` - Queries menu table, groups items by category using defaultdict
- `cart()` - Retrieves session cart, joins with menu table to get item details
- `update()` - Handles cart modifications with proper error checking
- `receipt()` - Creates order record, inserts into orders and order_items tables, generates unique order number using timestamp

### Database Schema (project.db)

**menu table:** Stores food items with columns: id, name, description, price, category, image_url

**orders table:** Stores completed orders with columns: id, order_number, total_amount, status, created_at

**order_items table:** Links orders to menu items with columns: id, order_id, menu_item_id, quantity, price_at_time (preserves price at purchase time)

### Frontend Templates

**layout.html** - Base template with Bootstrap CDN links, CSS/JS includes, and main content block

**index.html** - Home page with hero image and Start Order button

**menu.html** - Menu display with navbar (Cart, Order History), items grouped by category, each item has an Order button

**cart.html** - Shopping cart with:
- Flash messages for successful additions
- Quantity controls (+/- buttons)
- Remove button with Bootstrap modal confirmation
- Total price calculation
- Add More Items and Checkout buttons

**summary.html** - Pre-checkout summary showing all items and total

**receipt.html** - Order confirmation page with:
- Unique order number (format: ORD-YYYYMMDDHHMMSS)
- Timestamp
- Itemized list with quantities and prices
- Different display for past orders vs new orders

**order_history.html** - Grid display of past orders with View Receipt links

**error.html** - Error page template

### Static Files

**styles.css** - Custom styling for:
- Hero image overlay and positioning
- Menu title formatting
- Responsive card layouts

**index.js** - JavaScript functionality for:
- Remove button confirmation modal
- Dynamic modal population with item IDs
- Bootstrap modal initialization

## Design Choices

### Session-Based Cart
I chose Flask session (server-side filesystem) over client-side cookies because session data is more secure and can handle larger cart sizes without size limitations. The cart is stored as a dictionary mapping item_id to quantity.

### Database Price Tracking
The order_items table stores `price_at_time` rather than relying on the current menu price. This preserves the exact price a customer paid even if menu prices change later - critical for financial records.

### Unique Order Numbers
Order numbers use timestamp format `ORD-20241201143022` which guarantees uniqueness without needing database sequences and makes orders human-readable and sortable by time.

### Category Grouping
Used Python's `defaultdict(list)` to dynamically group menu items by category rather than hardcoding categories. This makes adding new categories easy without code changes.

### Price Storage
All prices stored in cents (integers) in database to avoid floating-point precision errors. Display formatting divides by 100 and uses `"%.2f"` for proper dollar/cents display.

### Modal Confirmation
Added Bootstrap modal for remove action to prevent accidental deletions - better user experience than browser's default confirm dialog.

### Flash Messages
Used Flask's flash system for "Item added to cart" feedback with Bootstrap alert styling for clear user communication.

## Challenges Overcome

1. **Cart data structure** - Needed dictionary mapping item_id to quantity; implemented with session persistence
2. **SQL placeholder generation** - Dynamic `?` placeholders for IN queries based on cart size
3. **Order history retrieval** - Store order numbers in session but fetch full details from database using JOIN with menu table
4. **Receipt for past orders** - Single receipt route handles both new orders (POST) and viewing past orders (GET with order_number parameter)

## Running the Application

1. Install dependencies: `pip install Flask Flask-Session cs50`
2. Initialize database with menu items
3. Run: `flask run`
4. Access at `http://127.0.0.1:5000`

## Technologies Used

- Python/Flask - Backend framework
- SQLite - Database
- Flask-Session - Server-side session management
- CS50 Library - SQL database wrapper
- Bootstrap 5 - Responsive frontend styling
- JavaScript - Modal interactions
- HTML/CSS - Structure and custom styling
