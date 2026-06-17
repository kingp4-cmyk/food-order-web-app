
from flask import Blueprint, render_template, request, redirect, url_for
from db import get_db_connection
from datetime import date
import mysql.connector

admin_bp = Blueprint("admin", __name__)


def get_next_id(cursor, table_name, id_column):
    cursor.execute(f"SELECT COALESCE(MAX({id_column}), 0) + 1 AS next_id FROM {table_name}")
    result = cursor.fetchone()
    return result["next_id"]


@admin_bp.route("/admin")
def admin_panel():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            RestaurantID,
            RestaurantName,
            Address,
            Phone,
            Rating
        FROM Restaurants
        ORDER BY RestaurantName
    """)
    restaurants = cursor.fetchall()

    cursor.execute("""
        SELECT 
            CategoryID,
            CategoryName
        FROM Categories
        ORDER BY CategoryName
    """)
    categories = cursor.fetchall()

    cursor.execute("""
        SELECT 
            mi.ItemID,
            mi.RestaurantID,
            mi.CategoryID,
            mi.ItemName,
            mi.Price,
            mi.AvailabilityStatus,
            r.RestaurantName,
            c.CategoryName
        FROM MenuItems mi
        JOIN Restaurants r ON mi.RestaurantID = r.RestaurantID
        JOIN Categories c ON mi.CategoryID = c.CategoryID
        ORDER BY r.RestaurantName, mi.ItemName
    """)
    menu_items = cursor.fetchall()

    cursor.execute("""
        SELECT *
        FROM Customers
        ORDER BY CustomerID DESC
    """)
    customers = cursor.fetchall()

    cursor.execute("""
        SELECT
            CourierID,
            FullName,
            Phone,
            VehicleType,
            IsActive
        FROM Couriers
        ORDER BY FullName
    """)
    couriers = cursor.fetchall()

    cursor.execute("""
        SELECT
            o.OrderID,
            o.OrderDate,
            o.TotalAmount,
            o.OrderStatus,

            c.FirstName,
            c.LastName,
            c.Phone AS CustomerPhone,
            c.Email,

            r.RestaurantName,

            d.DeliveryID,
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
        LEFT JOIN Deliveries d ON o.OrderID = d.OrderID
        LEFT JOIN Couriers co ON d.CourierID = co.CourierID
        ORDER BY o.OrderID DESC
    """)
    delivery_orders = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "admin.html",
        restaurants=restaurants,
        categories=categories,
        menu_items=menu_items,
        customers=customers,
        couriers=couriers,
        delivery_orders=delivery_orders
    )


@admin_bp.route("/admin/add_restaurant", methods=["POST"])
def add_restaurant():
    restaurant_name = request.form["restaurant_name"]
    address = request.form["address"]
    phone = request.form["phone"]

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        new_restaurant_id = get_next_id(cursor, "Restaurants", "RestaurantID")

        cursor.execute("""
            INSERT INTO Restaurants 
            (RestaurantID, RestaurantName, Address, Phone, Rating)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            new_restaurant_id,
            restaurant_name,
            address,
            phone,
            0.0
        ))

        connection.commit()

    except mysql.connector.Error as error:
        connection.rollback()
        print("Restaurant insert error:", error)

    cursor.close()
    connection.close()

    return redirect(url_for("admin.admin_panel"))


@admin_bp.route("/admin/add_menu_item", methods=["POST"])
def add_menu_item():
    restaurant_id = request.form["restaurant_id"]
    category_id = request.form["category_id"]
    item_name = request.form["item_name"]
    price = request.form["price"]

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        new_item_id = get_next_id(cursor, "MenuItems", "ItemID")

        cursor.execute("""
            INSERT INTO MenuItems 
            (ItemID, RestaurantID, CategoryID, ItemName, Price, AvailabilityStatus)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            new_item_id,
            restaurant_id,
            category_id,
            item_name,
            price,
            "Available"
        ))

        connection.commit()

    except mysql.connector.Error as error:
        connection.rollback()
        print("Menu item insert error:", error)

    cursor.close()
    connection.close()

    return redirect(url_for("admin.admin_panel"))


@admin_bp.route("/admin/add_customer", methods=["POST"])
def add_customer():
    customer_name = request.form["customer_name"]
    phone = request.form["phone"]
    address = request.form["address"]
    email = request.form.get("email", "")

    name_parts = customer_name.split(" ", 1)
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else ""

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            INSERT INTO Customers
            (FirstName, LastName, Phone, Email, Address, RegistrationDate)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            first_name,
            last_name,
            phone,
            email,
            address,
            date.today()
        ))

        connection.commit()

    except mysql.connector.Error as error:
        connection.rollback()
        print("Customer insert error:", error)

    cursor.close()
    connection.close()

    return redirect(url_for("admin.admin_panel"))


@admin_bp.route("/admin/update_price", methods=["POST"])
def update_price():
    item_id = request.form["item_id"]
    new_price = request.form["new_price"]

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            UPDATE MenuItems
            SET Price = %s
            WHERE ItemID = %s
        """, (
            new_price,
            item_id
        ))

        connection.commit()

    except mysql.connector.Error as error:
        connection.rollback()
        print("Price update error:", error)

    cursor.close()
    connection.close()

    return redirect(url_for("admin.admin_panel"))


@admin_bp.route("/admin/delete_menu_item/<int:item_id>", methods=["POST"])
def delete_menu_item(item_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            DELETE FROM MenuItems
            WHERE ItemID = %s
        """, (item_id,))

        connection.commit()

    except mysql.connector.Error as error:
        connection.rollback()
        print("Menu item delete error:", error)

    cursor.close()
    connection.close()

    return redirect(url_for("admin.admin_panel"))


@admin_bp.route("/admin/update_delivery_status", methods=["POST"])
def admin_update_delivery_status():
    order_id = request.form["order_id"]
    new_status = request.form["new_status"]

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            UPDATE Orders
            SET OrderStatus = %s
            WHERE OrderID = %s
        """, (
            new_status,
            order_id
        ))

        if new_status == "Yolda":
            cursor.execute("""
                UPDATE Deliveries
                SET DeliveryStatus = %s,
                    PickupTime = NOW()
                WHERE OrderID = %s
            """, (
                "Yolda",
                order_id
            ))

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
                    SET IsActive = FALSE
                    WHERE CourierID = %s
                """, (delivery["CourierID"],))

        elif new_status == "Teslim Edildi":
            cursor.execute("""
                UPDATE Deliveries
                SET DeliveryStatus = %s,
                    DeliveryTime = NOW()
                WHERE OrderID = %s
            """, (
                "Teslim Edildi",
                order_id
            ))

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
                    SET IsActive = TRUE
                    WHERE CourierID = %s
                """, (delivery["CourierID"],))

        elif new_status == "Kurye Bekleniyor":
            cursor.execute("""
                UPDATE Deliveries
                SET DeliveryStatus = %s
                WHERE OrderID = %s
            """, (
                "Kurye Bekleniyor",
                order_id
            ))

        connection.commit()

    except mysql.connector.Error as error:
        connection.rollback()
        print("Admin delivery status update error:", error)

    cursor.close()
    connection.close()

    return redirect(url_for("admin.admin_panel"))


@admin_bp.route("/admin/update_courier_status", methods=["POST"])
def update_courier_status():
    courier_id = request.form["courier_id"]
    is_active = request.form["is_active"]

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            UPDATE Couriers
            SET IsActive = %s
            WHERE CourierID = %s
        """, (
            is_active,
            courier_id
        ))

        connection.commit()

    except mysql.connector.Error as error:
        connection.rollback()
        print("Courier status update error:", error)

    cursor.close()
    connection.close()

    return redirect(url_for("admin.admin_panel"))