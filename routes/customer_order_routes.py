# ==========================================================
# PERSON 1 - CUSTOMER & ORDER MODULE
# ==========================================================

from flask import Blueprint, render_template, request, redirect, session
from db import get_db_connection
import mysql.connector

customer_order_bp = Blueprint("customer_order", __name__)


@customer_order_bp.route("/customers")
def customers():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            CustomerID,
            FirstName,
            LastName,
            Phone,
            Email,
            Address,
            RegistrationDate
        FROM Customers
        ORDER BY CustomerID DESC
    """)

    customers = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template("customers.html", customers=customers)


@customer_order_bp.route("/add_customer", methods=["POST"])
def add_customer():
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    phone = request.form["phone"]
    email = request.form["email"]
    address = request.form["address"]

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO Customers 
            (FirstName, LastName, Phone, Email, Address, RegistrationDate)
            VALUES (%s, %s, %s, %s, %s, CURDATE())
        """, (first_name, last_name, phone, email, address))

        connection.commit()

    except mysql.connector.Error as error:
        connection.rollback()
        print("Customer insert error:", error)

    cursor.close()
    connection.close()

    return redirect("/customers")


@customer_order_bp.route("/orders")
def orders():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            o.OrderID,
            o.OrderDate,
            o.TotalAmount,
            o.OrderStatus,
            c.FirstName,
            c.LastName,
            c.Phone,
            c.Email,
            c.Address AS CustomerAddress,
            r.RestaurantName,
            mi.ItemName,
            oi.Quantity,
            oi.UnitPrice,
            oi.Subtotal
        FROM Orders o
        JOIN Customers c ON o.CustomerID = c.CustomerID
        JOIN Restaurants r ON o.RestaurantID = r.RestaurantID
        JOIN OrderItems oi ON o.OrderID = oi.OrderID
        JOIN MenuItems mi ON oi.ItemID = mi.ItemID
        ORDER BY o.OrderID DESC
    """)

    orders = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template("orders.html", orders=orders)


# ==========================================================
# MY ORDERS
# Sadece bu tarayıcı oturumunda sipariş veren kullanıcının siparişlerini gösterir.
# ==========================================================

@customer_order_bp.route("/my_orders")
def my_orders():
    customer_id = session.get("customer_id")

    # Kullanıcı bu oturumda henüz sipariş vermediyse boş liste gösterilir.
    if not customer_id:
        return render_template("my_orders.html", orders=[])

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            o.OrderID,
            o.OrderDate,
            o.TotalAmount,
            o.OrderStatus,

            c.FirstName,
            c.LastName,
            c.Phone,
            c.Email,
            c.Address AS CustomerAddress,

            r.RestaurantName,

            p.Amount,
            p.PaymentMethod,
            p.PaymentStatus,
            p.PaymentDate,

            d.DeliveryStatus,
            d.PickupTime,
            d.DeliveryTime,

            co.FullName AS CourierName,
            co.Phone AS CourierPhone,
            co.VehicleType,
            co.IsActive

        FROM Orders o
        JOIN Customers c ON o.CustomerID = c.CustomerID
        JOIN Restaurants r ON o.RestaurantID = r.RestaurantID
        LEFT JOIN Payments p ON o.OrderID = p.OrderID
        LEFT JOIN Deliveries d ON o.OrderID = d.OrderID
        LEFT JOIN Couriers co ON d.CourierID = co.CourierID
        WHERE o.CustomerID = %s
        ORDER BY o.OrderID DESC
    """, (customer_id,))

    orders = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template("my_orders.html", orders=orders)


# ==========================================================
# CART OPERATIONS
# ==========================================================

@customer_order_bp.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    restaurant_id = int(request.form["restaurant_id"])
    restaurant_name = request.form["restaurant_name"]
    item_id = int(request.form["item_id"])
    item_name = request.form["item_name"]
    price = float(request.form["price"])
    quantity = int(request.form["quantity"])

    cart = session.get("cart", [])

    cart_item = {
        "restaurant_id": restaurant_id,
        "restaurant_name": restaurant_name,
        "item_id": item_id,
        "item_name": item_name,
        "price": price,
        "quantity": quantity,
        "subtotal": price * quantity
    }

    cart.append(cart_item)
    session["cart"] = cart

    # Ürün sepete eklenince kullanıcı aynı restoran sayfasında kalır.
    return redirect(f"/restaurant/{restaurant_id}?added=1")


@customer_order_bp.route("/cart")
def cart():
    cart_items = session.get("cart", [])
    total_amount = sum(item["subtotal"] for item in cart_items)

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            CourierID,
            FullName,
            Phone,
            VehicleType,
            IsActive
        FROM Couriers
        WHERE IsActive = TRUE
        ORDER BY FullName
    """)
    couriers = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "cart.html",
        cart_items=cart_items,
        total_amount=total_amount,
        couriers=couriers
    )


@customer_order_bp.route("/remove_from_cart/<int:item_id>")
def remove_from_cart(item_id):
    cart_items = session.get("cart", [])

    updated_cart = []
    removed = False

    for item in cart_items:
        if item["item_id"] == item_id and not removed:
            removed = True
            continue

        updated_cart.append(item)

    session["cart"] = updated_cart

    return redirect("/cart")


@customer_order_bp.route("/clear_cart")
def clear_cart():
    session["cart"] = []
    return redirect("/cart")


# ==========================================================
# PLACE ORDER
# Sipariş verildiğinde customer_id session'a kaydedilir.
# Böylece My Orders sayfası sadece o müşterinin siparişlerini gösterir.
# ==========================================================

@customer_order_bp.route("/place_order", methods=["POST"])
def place_order():
    cart_items = session.get("cart", [])

    if not cart_items:
        return redirect("/cart")

    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    phone = request.form["phone"]
    email = request.form["email"]
    address = request.form["address"]
    payment_method = request.form["payment_method"]
    courier_id = request.form["courier_id"]

    restaurant_id = cart_items[0]["restaurant_id"]
    total_amount = sum(item["subtotal"] for item in cart_items)

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT CustomerID
            FROM Customers
            WHERE Email = %s
        """, (email,))

        existing_customer = cursor.fetchone()

        if existing_customer:
            customer_id = existing_customer["CustomerID"]

            cursor.execute("""
                UPDATE Customers
                SET FirstName = %s,
                    LastName = %s,
                    Phone = %s,
                    Address = %s
                WHERE CustomerID = %s
            """, (
                first_name,
                last_name,
                phone,
                address,
                customer_id
            ))

        else:
            cursor.execute("""
                INSERT INTO Customers
                (FirstName, LastName, Phone, Email, Address, RegistrationDate)
                VALUES (%s, %s, %s, %s, %s, CURDATE())
            """, (
                first_name,
                last_name,
                phone,
                email,
                address
            ))

            customer_id = cursor.lastrowid

        # Kullanıcıyı session'a kaydediyoruz.
        # My Orders sayfası artık sadece bu customer_id'nin siparişlerini gösterecek.
        session["customer_id"] = customer_id

        cursor.execute("""
            INSERT INTO Orders
            (CustomerID, RestaurantID, OrderDate, TotalAmount, OrderStatus)
            VALUES (%s, %s, NOW(), %s, %s)
        """, (
            customer_id,
            restaurant_id,
            total_amount,
            "Kurye Bekleniyor"
        ))

        order_id = cursor.lastrowid

        for item in cart_items:
            cursor.execute("""
                INSERT INTO OrderItems
                (OrderID, ItemID, Quantity, UnitPrice, Subtotal)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                order_id,
                item["item_id"],
                item["quantity"],
                item["price"],
                item["subtotal"]
            ))

        cursor.execute("""
            INSERT INTO Payments
            (OrderID, Amount, PaymentMethod, PaymentStatus)
            VALUES (%s, %s, %s, %s)
        """, (
            order_id,
            total_amount,
            payment_method,
            "Tamamlandı"
        ))

        cursor.execute("""
            INSERT INTO Deliveries
            (OrderID, CourierID, DeliveryStatus, PickupTime, DeliveryTime)
            VALUES (%s, %s, %s, NULL, NULL)
        """, (
            order_id,
            courier_id,
            "Kurye Bekleniyor"
        ))

        cursor.execute("""
            UPDATE Couriers
            SET IsActive = FALSE
            WHERE CourierID = %s
        """, (courier_id,))

        connection.commit()
        session["cart"] = []

    except mysql.connector.Error as error:
        connection.rollback()
        print("Order creation error:", error)
        cursor.close()
        connection.close()
        return redirect("/cart")

    cursor.close()
    connection.close()

    return redirect(f"/order_success/{order_id}")


@customer_order_bp.route("/order_success/<int:order_id>")
def order_success(order_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            o.OrderID,
            o.OrderDate,
            o.TotalAmount,
            o.OrderStatus,

            c.FirstName,
            c.LastName,
            c.Phone,
            c.Email,
            c.Address AS CustomerAddress,

            r.RestaurantID,
            r.RestaurantName,

            p.Amount,
            p.PaymentMethod,
            p.PaymentStatus,
            p.PaymentDate,

            d.DeliveryStatus,
            d.PickupTime,
            d.DeliveryTime,

            co.CourierID,
            co.FullName AS CourierName,
            co.Phone AS CourierPhone,
            co.VehicleType,
            co.IsActive

        FROM Orders o
        JOIN Customers c ON o.CustomerID = c.CustomerID
        JOIN Restaurants r ON o.RestaurantID = r.RestaurantID
        LEFT JOIN Payments p ON o.OrderID = p.OrderID
        LEFT JOIN Deliveries d ON o.OrderID = d.OrderID
        LEFT JOIN Couriers co ON d.CourierID = co.CourierID
        WHERE o.OrderID = %s
        ORDER BY d.DeliveryID DESC
        LIMIT 1
    """, (order_id,))

    order = cursor.fetchone()

    cursor.execute("""
        SELECT 
            mi.ItemName,
            oi.Quantity,
            oi.UnitPrice,
            oi.Subtotal
        FROM OrderItems oi
        JOIN MenuItems mi ON oi.ItemID = mi.ItemID
        WHERE oi.OrderID = %s
    """, (order_id,))

    order_items = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "order_success.html",
        order=order,
        order_items=order_items
    )