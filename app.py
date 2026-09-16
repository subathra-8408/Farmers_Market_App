from flask import Flask, render_template, request, redirect, session

import mysql.connector

from flask_mail import Mail, Message
import random

import os
from werkzeug.utils import secure_filename

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Suba_pr0",
    database="farmers_market"
)

cursor = db.cursor(buffered=True)

app = Flask(__name__)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'subathrachidambaram07@gmail.com'
app.config['MAIL_PASSWORD'] = 'zmpyprvirfbjjego'

mail = Mail(app)

app.secret_key = "farmers_market_secret"

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    return render_template('welcome.html')

@app.route('/farmer')
def farmer():
    return render_template('farmer.html')

@app.route('/buyer')
def buyer():
    return render_template('buyer.html')

@app.route('/farmer_register', methods=['GET', 'POST'])
def farmer_register():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        mobile = request.form['mobile']
        password = request.form['password']

        sql = """
        INSERT INTO farmers(name,email,mobile,password)
        VALUES(%s,%s,%s,%s)
        """

        values = (name, email, mobile, password)

        cursor.execute(sql, values)
        db.commit()

        return "Registration Successful"

    return render_template('farmer_register.html')

@app.route('/farmer_login', methods=['GET', 'POST'])
def farmer_login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        sql = """
        SELECT * FROM farmers
        WHERE email=%s AND password=%s
        """

        values = (email, password)

        cursor.execute(sql, values)

        farmer = cursor.fetchone()

        if farmer:

            session['farmer_id'] = farmer[0]
            session['farmer_name'] = farmer[1]   # Farmer name save

            return redirect('/farmer_dashboard')

        else:

            return "Invalid Email or Password"

    return render_template('farmer_login.html')

@app.route('/farmer_dashboard')
def farmer_dashboard():

    cursor.execute(

    "SELECT COUNT(*) FROM products WHERE stock<=5"

    )

    low_stock=cursor.fetchone()[0]

    return render_template(

    "farmer_dashboard.html",

    low_stock=low_stock

    )

@app.route('/buyer_register', methods=['GET', 'POST'])
def buyer_register():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        mobile = request.form['mobile']
        password = request.form['password']

        sql = """
        INSERT INTO buyers(name,email,mobile,password)
        VALUES(%s,%s,%s,%s)
        """

        values = (name, email, mobile, password)

        cursor.execute(sql, values)
        db.commit()

        return "Buyer Registration Successful"

    return render_template('buyer_register.html')

@app.route('/buyer_login', methods=['GET', 'POST'])
def buyer_login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        sql = """
        SELECT * FROM buyers
        WHERE email=%s AND password=%s
        """

        values = (email, password)

        cursor.execute(sql, values)

        buyer = cursor.fetchone()

        if buyer:
            session['buyer_name'] = buyer[1]
            session['buyer_email'] = buyer[2]
            return render_template('buyer_dashboard.html')
        else:
            return "Invalid Email or Password"

    return render_template('buyer_login.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        cursor.execute(
            """
            SELECT * FROM admin
            WHERE username=%s AND password=%s
            """,
            (username, password)
        )

        admin = cursor.fetchone()

        if admin:

            return redirect('/admin_dashboard')

        else:

            return "Invalid Username or Password"

    return render_template('admin_login.html')

@app.route('/buyer_dashboard')
def buyer_dashboard():

    buyer_name = session['buyer_name']

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM wishlist
        WHERE buyer_name=%s
        """,
        (buyer_name,)
    )

    wishlist_count = cursor.fetchone()[0]

    return render_template(
        "buyer_dashboard.html",
        wishlist_count=wishlist_count
    )

@app.route('/admin_dashboard')
def admin_dashboard():

    cursor.execute("SELECT COUNT(*) FROM farmers")
    total_farmers = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM buyers")
    total_buyers = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM orders")
    total_orders = cursor.fetchone()[0]

    return render_template(
        "admin_dashboard.html",
        total_farmers=total_farmers,
        total_buyers=total_buyers,
        total_products=total_products,
        total_orders=total_orders
    )

@app.route('/admin_view_farmers')
def admin_view_farmers():

    cursor.execute("SELECT * FROM farmers")

    farmers = cursor.fetchall()

    return render_template(
        'admin_view_farmers.html',
        farmers=farmers
    )

@app.route('/view_farmers')
def view_farmers():

    cursor.execute("""

    SELECT *

    FROM farmers

    ORDER BY farmer_id DESC

    """)

    farmers = cursor.fetchall()

    return render_template(

        "view_farmers.html",

        farmers=farmers

    )

@app.route('/admin_view_buyers')
def admin_view_buyers():

    cursor.execute("SELECT * FROM buyers")

    buyers = cursor.fetchall()

    return render_template(
        "admin_view_buyers.html",
        buyers=buyers
    )

@app.route('/view_buyers')
def view_buyers():

    cursor.execute("""

    SELECT *

    FROM buyers

    ORDER BY buyer_id DESC

    """)

    buyers = cursor.fetchall()

    return render_template(

        "view_buyers.html",

        buyers=buyers

    )

@app.route('/delete_buyer/<int:buyer_id>')
def delete_buyer(buyer_id):

    cursor.execute(
        "DELETE FROM buyers WHERE buyer_id=%s",
        (buyer_id,)
    )

    db.commit()

    return redirect('/admin_view_buyers')

@app.route('/delete_farmer/<int:farmer_id>')
def delete_farmer(farmer_id):

    cursor.execute(
        "DELETE FROM farmers WHERE farmer_id=%s",
        (farmer_id,)
    )

    db.commit()

    return redirect('/admin_view_farmers')

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():

    if request.method == 'POST':
        farmer_id = session['farmer_id']
        product_name = request.form['product_name']
        category = request.form['category']
        stock = request.form['stock']
        unit = request.form['unit']
        price = request.form['price']

        # Get uploaded image
        image = request.files['image']

        # Safe filename
        filename = secure_filename(image.filename)

        # Save image in static/uploads
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        sql = """
        INSERT INTO products(product_name, category, stock, unit, price, image,farmer_id)
        VALUES(%s, %s, %s, %s, %s, %s, %s)
        """

        values = (product_name, category, stock, unit, price, filename,farmer_id)

        cursor.execute(sql, values)
        db.commit()

        return "Product Added Successfully"

    return render_template('add_product.html')

@app.route('/view_products')
def view_products():

    farmer_id=session['farmer_id']

    cursor.execute("""

    SELECT *

    FROM products

    WHERE farmer_id=%s

    """,(farmer_id,))

    products=cursor.fetchall()

    return render_template(

        "view_products.html",

        products=products

    )

@app.route('/admin_view_products')
def admin_view_products():

    cursor.execute("""

    SELECT
        p.*,
        f.name

    FROM products p

    LEFT JOIN farmers f

    ON p.farmer_id = f.farmer_id

    """)

    products = cursor.fetchall()

    return render_template(

        "admin_view_products.html",

        products=products

    )

@app.route('/admin_view_orders')
def admin_view_orders():

    cursor.execute("""

    SELECT
        orders.*,
        farmers.name

    FROM orders

    JOIN products
    ON orders.product_id = products.product_id

    JOIN farmers
    ON products.farmer_id = farmers.farmer_id

    ORDER BY orders.order_id DESC

    """)

    orders = cursor.fetchall()

    return render_template(

        "admin_view_orders.html",

        orders=orders

    )

@app.route('/low_stock')
def low_stock():

    farmer_id=session['farmer_id']

    cursor.execute("""

    SELECT *

    FROM products

    WHERE

    farmer_id=%s

    AND stock<=5

    """,(farmer_id,))

    products=cursor.fetchall()

    return render_template(

        "low_stock.html",

        products=products

    )

@app.route('/delete_product/<int:product_id>')
def delete_product(product_id):

    cursor.execute(
        "DELETE FROM products WHERE product_id=%s",
        (product_id,)
    )

    db.commit()

    return redirect('/view_products')

@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):

    if request.method == 'POST':

        product_name = request.form['product_name']
        category = request.form['category']
        stock = request.form['stock']
        unit = request.form['unit']
        price = request.form['price']

        image = request.files['image']

        # If new image selected
        if image.filename != "":

            filename = secure_filename(image.filename)

            image.save(
                os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    filename
                )
            )

            sql = """
            UPDATE products
            SET product_name=%s,
                category=%s,
                stock=%s,
                unit=%s,
                price=%s,
                image=%s
            WHERE product_id=%s
            """

            values = (
                product_name,
                category,
                stock,
                unit,
                price,
                filename,
                product_id
            )

        # If image not selected
        else:

            sql = """
            UPDATE products
            SET product_name=%s,
                category=%s,
                stock=%s,
                unit=%s,
                price=%s
            WHERE product_id=%s
            """

            values = (
                product_name,
                category,
                stock,
                unit,
                price,
                product_id
            )

        cursor.execute(sql, values)
        db.commit()

        return redirect('/view_products')

    cursor.execute(
        "SELECT * FROM products WHERE product_id=%s",
        (product_id,)
    )

    product = cursor.fetchone()

    return render_template(
        'edit_product.html',
        product=product
    )

@app.route('/view_orders')
def view_orders():

    farmer_id = session['farmer_id']

    cursor.execute("""

    SELECT orders.*

    FROM orders

    JOIN products

    ON orders.product_id = products.product_id

    WHERE products.farmer_id=%s

    ORDER BY orders.order_id DESC

    """,(farmer_id,))

    orders = cursor.fetchall()

    return render_template(

        "view_orders.html",

        orders=orders

    )

@app.route('/sales_report')
def sales_report():

    farmer_id = session['farmer_id']

    cursor.execute("""

    SELECT

    orders.product_name,

    SUM(orders.quantity),

    orders.unit,

    orders.price,

    SUM(orders.quantity*orders.price)

    FROM orders

    JOIN products

    ON orders.product_id=products.product_id

    WHERE

    orders.status='Delivered'

    AND products.farmer_id=%s

    GROUP BY

    orders.product_name,

    orders.unit,

    orders.price

    """,(farmer_id,))

    report=cursor.fetchall()


    cursor.execute("""

    SELECT

    IFNULL(SUM(orders.quantity),0),

    IFNULL(SUM(orders.quantity*orders.price),0)

    FROM orders

    JOIN products

    ON orders.product_id=products.product_id

    WHERE

    orders.status='Delivered'

    AND products.farmer_id=%s

    """,(farmer_id,))

    summary=cursor.fetchone()


    return render_template(

        "sales_report.html",

        report=report,

        summary=summary

    )

@app.route('/buyer_view_products')
def buyer_view_products():

    search=request.args.get('search')

    if search:

        cursor.execute("""

        SELECT *

        FROM products

        WHERE product_name LIKE %s

        """,('%'+search+'%',))

    else:

        cursor.execute("""

        SELECT *

        FROM products

        """)

    products=cursor.fetchall()

    return render_template(

        "buyer_view_products.html",

        products=products

    )

@app.route('/place_order/<int:product_id>', methods=['GET','POST'])
def place_order(product_id):

    cursor.execute(
        "SELECT * FROM products WHERE product_id=%s",
        (product_id,)
    )

    product = cursor.fetchone()

    if not product:
        return "Product Not Found"

    if request.method=="POST":

        buyer_name=session['buyer_name']

        quantity=float(request.form['quantity'])

        address=request.form['address']

        payment_mode=request.form['payment_mode']

        available_stock=float(product[3])

        if quantity>available_stock:

            return f"Only {available_stock} {product[6]} available."

        total_price=quantity*float(product[4])

        cursor.execute("""

        INSERT INTO orders
        (
        product_id,
        product_name,
        buyer_name,
        quantity,
        unit,
        price,
        status,
        address,
        payment_mode
        )

        VALUES
        (%s,%s,%s,%s,%s,%s,%s,%s,%s)

        """,(

        product_id,
        product[1],
        buyer_name,
        quantity,
        product[6],
        total_price,
        "Pending",
        address,
        payment_mode

        ))

        new_stock=available_stock-quantity

        cursor.execute(

        "UPDATE products SET stock=%s WHERE product_id=%s",

        (new_stock,product_id)

        )

        db.commit()

        return redirect('/my_orders')

    return render_template(

        "place_order.html",

        product=product

    )

@app.route('/accept_order/<int:order_id>')
def accept_order(order_id):

    cursor.execute(
        """
        UPDATE orders
        SET status='Accepted'
        WHERE order_id=%s
        """,
        (order_id,)
    )

    db.commit()

    return redirect('/view_orders')

@app.route('/packed_order/<int:order_id>')
def packed_order(order_id):

    cursor.execute(
        "UPDATE orders SET status='Packed' WHERE order_id=%s",
        (order_id,)
    )

    db.commit()

    return redirect('/view_orders')

@app.route('/out_delivery/<int:order_id>')
def out_delivery(order_id):

    cursor.execute(
        "UPDATE orders SET status='Out for Delivery' WHERE order_id=%s",
        (order_id,)
    )

    db.commit()

    return redirect('/view_orders')

@app.route('/delivered_order/<int:order_id>')
def delivered_order(order_id):

    cursor.execute(
        "UPDATE orders SET status='Delivered' WHERE order_id=%s",
        (order_id,)
    )

    db.commit()

    return redirect('/view_orders')

@app.route('/next_status/<int:order_id>')
def next_status(order_id):

    cursor.execute(
        "SELECT status FROM orders WHERE order_id=%s",
        (order_id,)
    )

    status = cursor.fetchone()

    if status:

        current = status[0]

        if current == "Pending":
            new_status = "Accepted"

        elif current == "Accepted":
            new_status = "Packed"

        elif current == "Packed":
            new_status = "Out for Delivery"

        elif current == "Out for Delivery":
            new_status = "Delivered"

        else:
            new_status = current

        cursor.execute(
            "UPDATE orders SET status=%s WHERE order_id=%s",
            (new_status, order_id)
        )

        db.commit()

    return redirect('/view_orders')

@app.route('/reject_order/<int:order_id>')
def reject_order(order_id):

    cursor.execute(
        """
        UPDATE orders
        SET status='Rejected'
        WHERE order_id=%s
        """,
        (order_id,)
    )

    db.commit()

    return redirect('/view_orders')

@app.route('/my_orders')
def my_orders():

    buyer_name = session['buyer_name']

    cursor.execute("""

    SELECT *

    FROM orders

    WHERE buyer_name=%s

    ORDER BY order_id DESC

    """,(buyer_name,))

    orders = cursor.fetchall()

    return render_template(

        "my_orders.html",

        orders=orders

    )

@app.route('/add_review/<int:order_id>', methods=['GET','POST'])
def add_review(order_id):

    buyer_name = session['buyer_name']

    # Already reviewed?
    cursor.execute(
        "SELECT * FROM reviews WHERE order_id=%s",
        (order_id,)
    )

    existing_review = cursor.fetchone()

    if existing_review:
        return "You have already reviewed this order."

    if request.method == 'POST':

        rating = request.form['rating']

        review = request.form['review']

        # Get Product Details
        cursor.execute(
            """
            SELECT product_id, product_name
            FROM orders
            WHERE order_id=%s
            """,
            (order_id,)
        )

        product = cursor.fetchone()

        product_id = product[0]
        product_name = product[1]

        cursor.execute(
            """
            INSERT INTO reviews
            (
            product_id,
            order_id,
            product_name,
            buyer_name,
            rating,
            review
            )

            VALUES
            (%s,%s,%s,%s,%s,%s)
            """,
            (
                product_id,
                order_id,
                product_name,
                buyer_name,
                rating,
                review
            )
        )

        db.commit()

        return redirect('/my_orders')

    cursor.execute(
        "SELECT * FROM orders WHERE order_id=%s",
        (order_id,)
    )

    order = cursor.fetchone()

    return render_template(
        "review.html",
        order=order
    )

@app.route('/view_reviews')
def view_reviews():

    farmer_id = session['farmer_id']

    cursor.execute("""

    SELECT

        r.product_name,

        r.buyer_name,

        r.rating,

        r.review,

        r.review_date,

        ROUND(AVG(r2.rating),1) AS average_rating,

        COUNT(r2.review_id) AS total_reviews

    FROM reviews r

    JOIN reviews r2
        ON r.product_id = r2.product_id

    JOIN products p
        ON r.product_id = p.product_id

    WHERE p.farmer_id=%s

    GROUP BY

        r.review_id,
        r.product_name,
        r.buyer_name,
        r.rating,
        r.review,
        r.review_date

    ORDER BY r.review_date DESC

    """,(farmer_id,))

    reviews = cursor.fetchall()

    return render_template(

        "view_reviews.html",

        reviews=reviews

    )

@app.route('/product_ratings')
def product_ratings():

    cursor.execute("""

    SELECT

    product_name,

    ROUND(AVG(rating),1) AS average_rating,

    COUNT(review_id) AS total_reviews

    FROM reviews

    GROUP BY product_name

    ORDER BY average_rating DESC

    """)

    ratings = cursor.fetchall()

    return render_template(
        "product_ratings.html",
        ratings=ratings
    )

@app.route('/product_reviews/<product_name>')
def product_reviews(product_name):

    cursor.execute(
        """
        SELECT
        buyer_name,
        rating,
        review,
        review_date
        FROM reviews
        WHERE product_name=%s
        ORDER BY review_date DESC
        """,
        (product_name,)
    )

    reviews = cursor.fetchall()

    return render_template(
        "product_reviews.html",
        product_name=product_name,
        reviews=reviews
    )

@app.route('/invoice/<int:order_id>')
def invoice(order_id):

    cursor.execute("""
        SELECT
            order_id,
            product_name,
            buyer_name,
            quantity,
            unit,
            price,
            status,
            address,
            payment_mode,
            order_date
        FROM orders
        WHERE order_id=%s
    """, (order_id,))

    invoice = cursor.fetchone()

    if invoice is None:
        return "Invoice not found."

    total = float(invoice[3]) * float(invoice[5])

    return render_template(
        "invoice.html",
        invoice=invoice,
        total=total
    )

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):

    buyer_name = session['buyer_name']
    quantity = float(request.form['quantity'])

    cursor.execute(
        "SELECT * FROM products WHERE product_id=%s",
        (product_id,)
    )

    product = cursor.fetchone()

    sql = """
    INSERT INTO cart
    (buyer_name, product_id, product_name, quantity, unit, price)
    VALUES(%s,%s,%s,%s,%s,%s)
    """

    values = (
        buyer_name,
        product[0],
        product[1],
        quantity,
        product[6],
        product[4]
    )

    cursor.execute(sql, values)

    db.commit()

    return redirect('/buyer_view_products')

@app.route('/add_to_wishlist/<int:product_id>')
def add_to_wishlist(product_id):

    buyer_name = session['buyer_name']

    cursor.execute(
        "SELECT * FROM wishlist WHERE buyer_name=%s AND product_id=%s",
        (buyer_name, product_id)
    )

    item = cursor.fetchone()

    if item:

        return "Product already in Wishlist"

    cursor.execute(
        "SELECT * FROM products WHERE product_id=%s",
        (product_id,)
    )

    product = cursor.fetchone()

    cursor.execute(
        """
        INSERT INTO wishlist
        (buyer_name, product_id, product_name, price, image)
        VALUES(%s,%s,%s,%s,%s)
        """,
        (
            buyer_name,
            product[0],
            product[1],
            product[4],
            product[5]
        )
    )

    db.commit()

    return redirect('/buyer_view_products')

@app.route('/wishlist')
def wishlist():

    buyer_name = session['buyer_name']

    cursor.execute(
        """
        SELECT *
        FROM wishlist
        WHERE buyer_name=%s
        ORDER BY wishlist_id DESC
        """,
        (buyer_name,)
    )

    wishlist = cursor.fetchall()

    return render_template(
        "wishlist.html",
        wishlist=wishlist
    )

@app.route('/remove_wishlist/<int:wishlist_id>')
def remove_wishlist(wishlist_id):

    cursor.execute(
        "DELETE FROM wishlist WHERE wishlist_id=%s",
        (wishlist_id,)
    )

    db.commit()

    return redirect('/wishlist')

@app.route('/move_to_cart/<int:wishlist_id>', methods=['POST'])
def move_to_cart(wishlist_id):

    buyer_name = session['buyer_name']

    quantity = float(request.form['quantity'])

    # Wishlist Item
    cursor.execute(
        "SELECT * FROM wishlist WHERE wishlist_id=%s",
        (wishlist_id,)
    )

    item = cursor.fetchone()

    if not item:
        return "Wishlist Item Not Found"

    product_id = item[2]

    # Duplicate Cart Check
    cursor.execute(
        """
        SELECT *
        FROM cart
        WHERE buyer_name=%s
        AND product_id=%s
        """,
        (buyer_name, product_id)
    )

    already = cursor.fetchone()

    if already:
        return "Product Already Exists In Cart"

    # Product Details
    cursor.execute(
        """
        SELECT
        product_name,
        stock,
        unit,
        price
        FROM products
        WHERE product_id=%s
        """,
        (product_id,)
    )

    product = cursor.fetchone()

    product_name = product[0]
    stock = float(product[1])
    unit = product[2]
    price = product[3]

    # Stock Validation
    if quantity > stock:

        return f"❌ Only {stock} {unit} Available"

    # Insert Into Cart
    cursor.execute(
        """
        INSERT INTO cart
        (buyer_name,product_id,product_name,quantity,unit,price)

        VALUES(%s,%s,%s,%s,%s,%s)
        """,
        (
            buyer_name,
            product_id,
            product_name,
            quantity,
            unit,
            price
        )
    )

    # Remove Wishlist Item
    cursor.execute(
        """
        DELETE FROM wishlist
        WHERE wishlist_id=%s
        """,
        (wishlist_id,)
    )

    db.commit()

    return redirect('/wishlist')

@app.route('/view_cart')
def view_cart():

    buyer_name = session['buyer_name']

    cursor.execute(
        "SELECT * FROM cart WHERE buyer_name=%s",
        (buyer_name,)
    )

    cart = cursor.fetchall()

    return render_template(
        'view_cart.html',
        cart=cart
    )

@app.route('/cart_checkout', methods=['GET', 'POST'])
def cart_checkout():

    if request.method == 'POST':

        buyer_name = session['buyer_name']

        address = request.form['address']
        payment_mode = request.form['payment_mode']

        # Get all cart items
        cursor.execute(
            "SELECT * FROM cart WHERE buyer_name=%s",
            (buyer_name,)
        )

        cart_items = cursor.fetchall()

        # Save each cart item as an order
        for item in cart_items:

            product_id = item[2]
            product_name = item[3]
            quantity = item[4]
            unit = item[5]
            price = item[6]

            # Save Order
            cursor.execute(
                """
                INSERT INTO orders
                (product_name, buyer_name, quantity, unit, price, status, address, payment_mode)
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    product_name,
                    buyer_name,
                    quantity,
                    unit,
                    price,
                    "Pending",
                    address,
                    payment_mode
                )
            )

            # Get Current Stock
            cursor.execute(
                "SELECT stock FROM products WHERE product_id=%s",
                (product_id,)
            )

            stock = cursor.fetchone()

            if stock:

                new_stock = float(stock[0]) - float(quantity)

                cursor.execute(
                    "UPDATE products SET stock=%s WHERE product_id=%s",
                    (new_stock, product_id)
                )

        # Clear Cart
        cursor.execute(
            "DELETE FROM cart WHERE buyer_name=%s",
            (buyer_name,)
        )

        db.commit()

        return "Order Placed Successfully"

    return render_template("cart_checkout.html")

@app.route('/remove_cart/<int:cart_id>')
def remove_cart(cart_id):

    cursor.execute(
        "DELETE FROM cart WHERE cart_id=%s",
        (cart_id,)
    )

    db.commit()

    return redirect('/view_cart')

@app.route('/forgot_password', methods=['GET','POST'])
def forgot_password():

    if request.method=='POST':

        email=request.form['email']

        role=request.form['role']

        if role=="buyer":

            cursor.execute(
                "SELECT * FROM buyers WHERE email=%s",
                (email,)
            )

        elif role=="farmer":

            cursor.execute(
                "SELECT * FROM farmers WHERE email=%s",
                (email,)
            )

        else:

            cursor.execute(
                "SELECT * FROM admin WHERE email=%s",
                (email,)
            )

        user=cursor.fetchone()

        if not user:

            return "Email Not Registered"

        otp=random.randint(100000,999999)

        session['otp']=str(otp)
        session['email']=email
        session['role']=role

        msg=Message(

            "Password Reset OTP",

            sender=app.config['MAIL_USERNAME'],

            recipients=[email]

        )

        msg.body=f"""Your OTP is:{otp}Do not share this OTP."""

        mail.send(msg)

        return redirect('/verify_otp')

    return render_template(
        "forgot_password.html"
    )

@app.route('/verify_otp', methods=['GET','POST'])
def verify_otp():

    if request.method == 'POST':

        entered_otp = request.form['otp']

        if entered_otp == session.get('otp'):

            return redirect('/reset_password')

        else:

            return "Invalid OTP"

    return render_template("verify_otp.html")

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():

    if request.method == 'POST':

        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:

            return "Passwords do not match"

        email = session.get('email')
        role = session.get('role')

        if role == "buyer":

            cursor.execute(
                "UPDATE buyers SET password=%s WHERE email=%s",
                (password, email)
            )

            login_page = "/buyer_login"

        elif role == "farmer":

            cursor.execute(
                "UPDATE farmers SET password=%s WHERE email=%s",
                (password, email)
            )

            login_page = "/farmer_login"

        else:

            cursor.execute(
                "UPDATE admin SET password=%s WHERE email=%s",
                (password, email)
            )

            login_page = "/admin_login"

        db.commit()

        session.pop('otp', None)
        session.pop('email', None)
        session.pop('role', None)

        return redirect(login_page)

    return render_template("reset_password.html")

@app.route('/logout')
def logout():

    session.clear()

    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)