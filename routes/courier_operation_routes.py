from flask import Blueprint, render_template, request, redirect, url_for
from db import get_db_connection
from datetime import datetime

courier_operation_bp = Blueprint("courier_operation", __name__)


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def get_next_id(cursor, table_name, id_column):
    cursor.execute(f"SELECT COALESCE(MAX({id_column}), 0) + 1 AS next_id FROM {table_name}")
    result = cursor.fetchone()

    if isinstance(result, dict):
        return result["next_id"]

    return result[0]


# ==========================================================
# COURIER OPERATION PAGE
# Kullanıcı sipariş verdikten sonra açılacak operasyon sayfası.
# ==========================================================

@courier_operation_bp.route("/courier_operations")
def courier_operations():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Kurye listesi
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

    # Sipariş listesi
    cursor.execute("""
        SELECT 
            o.OrderID,
            o.CustomerID,
            o.RestaurantID,
            o.OrderDate,
            o.TotalAmount,
            o.OrderStatus,
            c.CustomerName,
            r.RestaurantName
        FROM Orders o
        JOIN Customers c ON o.CustomerID = c.CustomerID
        JOIN Restaurants r ON o.RestaurantID = r.RestaurantID
        ORDER BY o.OrderID DESC
    """)
    orders = cursor.fetchall()

    # Teslimat / kurye atama listesi
    cursor.execute("""
        SELECT
            d.DeliveryID,
            d.OrderID,
            d.CourierID,
            d.DeliveryStatus,
            d.AssignedTime,
            co.CourierName
        FROM Deliveries d
        JOIN Couriers co ON d.CourierID = co.CourierID
        ORDER BY d.DeliveryID DESC
    """)
    deliveries = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "courier_operations.html",
        couriers=couriers,
        orders=orders,
        deliveries=deliveries
    )


# ==========================================================
# ASSIGN COURIER TO ORDER
# Siparişi seçilen kuryeye atar.
# ==========================================================

@courier_operation_bp.route("/assign_courier", methods=["POST"])
def assign_courier():
    order_id = request.form["order_id"]
    courier_id = request.form["courier_id"]

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Yeni DeliveryID oluştur
    delivery_id = get_next_id(cursor, "Deliveries", "DeliveryID")

    # Teslimat kaydı oluştur
    cursor.execute("""
        INSERT INTO Deliveries
        (DeliveryID, OrderID, CourierID, DeliveryStatus, AssignedTime)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        delivery_id,
        order_id,
        courier_id,
        "Assigned",
        datetime.now()
    ))

    # Sipariş durumunu güncelle
    cursor.execute("""
        UPDATE Orders
        SET OrderStatus = %s
        WHERE OrderID = %s
    """, (
        "Assigned to Courier",
        order_id
    ))

    # Kurye durumunu güncelle
    cursor.execute("""
        UPDATE Couriers
        SET AvailabilityStatus = %s
        WHERE CourierID = %s
    """, (
        "Busy",
        courier_id
    ))

    connection.commit()
    cursor.close()
    connection.close()

    return redirect(url_for("courier_operation.courier_operations"))


# ==========================================================
# UPDATE ORDER STATUS
# Sipariş durumunu Yolda veya Delivered yapar.
# ==========================================================

@courier_operation_bp.route("/update_order_status", methods=["POST"])
def update_order_status():
    order_id = request.form["order_id"]
    new_status = request.form["new_status"]

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        UPDATE Orders
        SET OrderStatus = %s
        WHERE OrderID = %s
    """, (
        new_status,
        order_id
    ))

    cursor.execute("""
        UPDATE Deliveries
        SET DeliveryStatus = %s
        WHERE OrderID = %s
    """, (
        new_status,
        order_id
    ))

    # Eğer teslim edildiyse kuryeyi tekrar Available yap
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
            """, (
                "Available",
                delivery["CourierID"]
            ))

    connection.commit()
    cursor.close()
    connection.close()

    return redirect(url_for("courier_operation.courier_operations"))