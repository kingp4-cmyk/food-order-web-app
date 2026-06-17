# ==========================================================
# PERSON 1 - CUSTOMER & ORDER MODULE
# ==========================================================
# Bu dosya 1. kişinin sorumlu olduğu route'ları içerir.
#
# Bu versiyonda:
# - Sepette ürünler gösterilir
# - Cart sayfasında müşteri bilgisi, ödeme bilgisi ve kurye seçimi yapılır
# - Sipariş oluşturulur
# - Payment kaydı oluşturulur
# - Delivery kaydı oluşturulur
# - Seçilen kurye siparişe atanır
# - Order success sayfasında sipariş, ödeme ve kurye bilgisi gösterilir
# - Sipariş durumu "On the Way" ve "Delivered" olarak güncellenebilir
# ==========================================================

from flask import Blueprint, render_template, request, redirect, session
from db import get_db_connection
import mysql.connector

customer_order_bp = Blueprint("customer_order", __name__)


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def get_table_columns(cursor, table_name):
    cursor.execute(f"SHOW COLUMNS FROM {table_name}")
    return cursor.fetchall()


def get_column_value(column, key_name, index_number):
    if isinstance(column, dict):
        return column[key_name]
    return column[index_number]


def get_column_names(cursor, table_name):
    columns = get_table_columns(cursor, table_name)
    return [get_column_value(column, "Field", 0) for column in columns]


def is_auto_increment(cursor, table_name, column_name):
    columns = get_table_columns(cursor, table_name)

    for column in columns:
        field_name = get_column_value(column, "Field", 0)
        extra_info = get_column_value(column, "Extra", 5)

        if field_name == column_name and "auto_increment" in str(extra_info).lower():
            return True

    return False


def get_next_id(cursor, table_name, id_column):
    cursor.execute(f"SELECT COALESCE(MAX({id_column}), 0) + 1 AS next_id FROM {table_name}")
    result = cursor.fetchone()

    if isinstance(result, dict):
        return result["next_id"]

    return result[0]


# ==========================================================
# CUSTOMERS PAGE
# ==========================================================

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
    cursor = connection.cursor(dictionary=True)

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


# ==========================================================
# ORDERS LIST PAGE
# ==========================================================

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

    return redirect("/cart")


@customer_order_bp.route("/cart")
def cart():
    cart_items = session.get("cart", [])
    total_amount = sum(item["subtotal"] for item in cart_items)

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            CourierID,
            CourierName,
            Phone,
            VehicleType,
            AvailabilityStatus
        FROM Couriers
        ORDER BY CourierName
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
# Burada müşteri, sipariş, order items, payment ve delivery oluşturulur.
# Kurye seçimi cart sayfasındaki formdan gelir.
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
        # --------------------------------------------------
        # CUSTOMER
        # --------------------------------------------------
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
            """, (first_name, last_name, phone, address, customer_id))

        else:
            cursor.execute("""
                INSERT INTO Customers
                (FirstName, LastName, Phone, Email, Address, RegistrationDate)
                VALUES (%s, %s, %s, %s, %s, CURDATE())
            """, (first_name, last_name, phone, email, address))

            customer_id = cursor.lastrowid

        # --------------------------------------------------
        # ORDER
        # --------------------------------------------------
        cursor.execute("""
            INSERT INTO Orders
            (CustomerID, RestaurantID, OrderDate, TotalAmount, OrderStatus)
            VALUES (%s, %s, NOW(), %s, %s)
        """, (customer_id, restaurant_id, total_amount, "Assigned to Courier"))

        order_id = cursor.lastrowid

        # --------------------------------------------------
        # ORDER ITEMS
        # --------------------------------------------------
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

        # --------------------------------------------------
        # PAYMENT
        # --------------------------------------------------
        payment_columns = get_column_names(cursor, "Payments")

        payment_insert_columns = []
        payment_insert_values = []

        if "PaymentID" in payment_columns:
            if not is_auto_increment(cursor, "Payments", "PaymentID"):
                payment_insert_columns.append("PaymentID")
                payment_insert_values.append(get_next_id(cursor, "Payments", "PaymentID"))

        if "OrderID" in payment_columns:
            payment_insert_columns.append("OrderID")
            payment_insert_values.append(order_id)

        if "PaymentMethod" in payment_columns:
            payment_insert_columns.append("PaymentMethod")
            payment_insert_values.append(payment_method)

        if "PaymentStatus" in payment_columns:
            payment_insert_columns.append("PaymentStatus")
            payment_insert_values.append("Tamamlandı")

        if "PaymentDate" in payment_columns:
            payment_insert_columns.append("PaymentDate")
            payment_insert_values.append("NOW()")

        payment_columns_sql = []
        payment_placeholders = []
        real_payment_values = []

        for column, value in zip(payment_insert_columns, payment_insert_values):
            payment_columns_sql.append(column)

            if value == "NOW()":
                payment_placeholders.append("NOW()")
            else:
                payment_placeholders.append("%s")
                real_payment_values.append(value)

        cursor.execute(f"""
            INSERT INTO Payments
            ({", ".join(payment_columns_sql)})
            VALUES ({", ".join(payment_placeholders)})
        """, tuple(real_payment_values))

        # --------------------------------------------------
        # DELIVERY / COURIER ASSIGNMENT
        # --------------------------------------------------
        delivery_columns = get_column_names(cursor, "Deliveries")

        delivery_insert_columns = []
        delivery_insert_values = []

        if "DeliveryID" in delivery_columns:
            if not is_auto_increment(cursor, "Deliveries", "DeliveryID"):
                delivery_insert_columns.append("DeliveryID")
                delivery_insert_values.append(get_next_id(cursor, "Deliveries", "DeliveryID"))

        if "OrderID" in delivery_columns:
            delivery_insert_columns.append("OrderID")
            delivery_insert_values.append(order_id)

        if "CourierID" in delivery_columns:
            delivery_insert_columns.append("CourierID")
            delivery_insert_values.append(courier_id)

        if "DeliveryStatus" in delivery_columns:
            delivery_insert_columns.append("DeliveryStatus")
            delivery_insert_values.append("Assigned")

        if "AssignedTime" in delivery_columns:
            delivery_insert_columns.append("AssignedTime")
            delivery_insert_values.append("NOW()")

        delivery_columns_sql = []
        delivery_placeholders = []
        real_delivery_values = []

        for column, value in zip(delivery_insert_columns, delivery_insert_values):
            delivery_columns_sql.append(column)

            if value == "NOW()":
                delivery_placeholders.append("NOW()")
            else:
                delivery_placeholders.append("%s")
                real_delivery_values.append(value)

        cursor.execute(f"""
            INSERT INTO Deliveries
            ({", ".join(delivery_columns_sql)})
            VALUES ({", ".join(delivery_placeholders)})
        """, tuple(real_delivery_values))

        # --------------------------------------------------
        # COURIER STATUS UPDATE
        # --------------------------------------------------
        cursor.execute("""
            UPDATE Couriers
            SET AvailabilityStatus = %s
            WHERE CourierID = %s
        """, ("Busy", courier_id))

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


# ==========================================================
# ORDER SUCCESS PAGE
# Sipariş, ödeme ve kurye bilgisini gösterir.
# ==========================================================

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

            p.PaymentMethod,
            p.PaymentStatus,
            p.PaymentDate,

            d.DeliveryStatus,
            d.AssignedTime,

            co.CourierID,
            co.CourierName,
            co.Phone AS CourierPhone,
            co.VehicleType,
            co.AvailabilityStatus AS CourierAvailability
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


# ==========================================================
# UPDATE DELIVERY STATUS
# Burada sipariş durumu "On the Way" veya "Delivered" yapılır.
# ==========================================================

@customer_order_bp.route("/update_delivery_status/<int:order_id>", methods=["POST"])
def update_delivery_status(order_id):
    new_status = request.form["new_status"]

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            UPDATE Orders
            SET OrderStatus = %s
            WHERE OrderID = %s
        """, (new_status, order_id))

        cursor.execute("""
            UPDATE Deliveries
            SET DeliveryStatus = %s
            WHERE OrderID = %s
        """, (new_status, order_id))

        if new_status == "Delivered":
            cursor.execute("""
                SELECT CourierID
                FROM Deliveries
                WHERE OrderID = %s
                ORDER BY DeliveryID DESC
                LIMIT 1
            """, (order_id,))

            delivery = cursor.fetchone()

            if delivery:
                cursor.execute("""
                    UPDATE Couriers
                    SET AvailabilityStatus = %s
                    WHERE CourierID = %s
                """, ("Available", delivery["CourierID"]))

        connection.commit()

    except mysql.connector.Error as error:
        connection.rollback()
        print("Delivery status update error:", error)

    cursor.close()
    connection.close()

    return redirect(f"/order_success/{order_id}")