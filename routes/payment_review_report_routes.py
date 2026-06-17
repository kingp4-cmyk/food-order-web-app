# ==========================================================
# PERSON 4 - REVIEW & REPORT MODULE
# ==========================================================
# Bu dosya 4. kişinin sorumlu olduğu review ve report route'larını içerir.
#
# Payment işlemi cart.html sayfasında yapılır.
# Bu dosyada sadece review ve reports işlemleri bulunur.
#
# ÖNEMLİ:
# Kullanıcı yıldız seçmeden yorum yapamaz.
# Kullanıcı review sayfasına order_success sayfasından gelir.
# Bu yüzden müşteri ve restoran otomatik olarak siparişten alınır.
# ==========================================================

from flask import Blueprint, render_template, request, redirect
from db import get_db_connection
import mysql.connector

payment_review_report_bp = Blueprint("payment_review_report", __name__)


# ----------------------------------------------------------
# REVIEW PAGE
# ----------------------------------------------------------
@payment_review_report_bp.route("/payments-reviews")
def payments_reviews():
    order_id = request.args.get("order_id")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    selected_order = None

    # Eğer kullanıcı order_success sayfasından geldiyse,
    # order_id ile müşteri ve restoran bilgileri otomatik alınır.
    if order_id:
        cursor.execute("""
            SELECT
                o.OrderID,
                c.CustomerID,
                c.FirstName,
                c.LastName,
                c.Email,
                r.RestaurantID,
                r.RestaurantName
            FROM Orders o
            JOIN Customers c ON o.CustomerID = c.CustomerID
            JOIN Restaurants r ON o.RestaurantID = r.RestaurantID
            WHERE o.OrderID = %s
        """, (order_id,))

        selected_order = cursor.fetchone()

    # Review listesi
    cursor.execute("""
        SELECT
            rv.ReviewID,
            rv.Rating,
            rv.Comment,
            rv.ReviewDate,
            c.FirstName,
            c.LastName,
            r.RestaurantName
        FROM Reviews rv
        JOIN Customers c ON rv.CustomerID = c.CustomerID
        JOIN Restaurants r ON rv.RestaurantID = r.RestaurantID
        ORDER BY rv.ReviewID DESC
    """)
    reviews = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "payments_reviews.html",
        selected_order=selected_order,
        reviews=reviews
    )


# ----------------------------------------------------------
# ADD REVIEW
# ----------------------------------------------------------
@payment_review_report_bp.route("/add_review", methods=["POST"])
def add_review():
    order_id = request.form["order_id"]
    customer_id = request.form["customer_id"]
    restaurant_id = request.form["restaurant_id"]
    rating = request.form.get("rating")
    comment = request.form["comment"]

    # Kullanıcı yıldız seçmeden yorum yapamaz.
    if rating is None or rating == "":
        return redirect(f"/payments-reviews?order_id={order_id}")

    rating = int(rating)

    if rating < 1 or rating > 5:
        return redirect(f"/payments-reviews?order_id={order_id}")

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO Reviews
            (CustomerID, RestaurantID, Rating, Comment)
            VALUES (%s, %s, %s, %s)
        """, (
            customer_id,
            restaurant_id,
            rating,
            comment
        ))

        connection.commit()

    except mysql.connector.Error as error:
        connection.rollback()
        print("Review insert error:", error)

    cursor.close()
    connection.close()

    return redirect("/payments-reviews")


# ----------------------------------------------------------
# REPORTS PAGE
# ----------------------------------------------------------
@payment_review_report_bp.route("/reports")
def reports():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            r.RestaurantName,
            COUNT(o.OrderID) AS TotalOrders,
            SUM(o.TotalAmount) AS TotalRevenue
        FROM Orders o
        JOIN Restaurants r ON o.RestaurantID = r.RestaurantID
        GROUP BY r.RestaurantID, r.RestaurantName
        ORDER BY TotalRevenue DESC
    """)
    revenue_by_restaurant = cursor.fetchall()

    cursor.execute("""
        SELECT
            mi.ItemName,
            r.RestaurantName,
            SUM(oi.Quantity) AS TotalQuantitySold
        FROM OrderItems oi
        JOIN MenuItems mi ON oi.ItemID = mi.ItemID
        JOIN Restaurants r ON mi.RestaurantID = r.RestaurantID
        GROUP BY mi.ItemID, mi.ItemName, r.RestaurantName
        ORDER BY TotalQuantitySold DESC
    """)
    top_selling_items = cursor.fetchall()

    cursor.execute("""
        SELECT
            c.FirstName,
            c.LastName,
            COUNT(o.OrderID) AS TotalOrders,
            SUM(o.TotalAmount) AS TotalSpent
        FROM Orders o
        JOIN Customers c ON o.CustomerID = c.CustomerID
        GROUP BY c.CustomerID, c.FirstName, c.LastName
        ORDER BY TotalSpent DESC
    """)
    top_customers = cursor.fetchall()

    cursor.execute("""
        SELECT
            r.RestaurantName,
            COUNT(rv.ReviewID) AS ReviewCount,
            AVG(rv.Rating) AS AverageRating
        FROM Reviews rv
        JOIN Restaurants r ON rv.RestaurantID = r.RestaurantID
        GROUP BY r.RestaurantID, r.RestaurantName
        ORDER BY AverageRating DESC
    """)
    average_ratings = cursor.fetchall()

    cursor.execute("""
        SELECT
            OrderStatus,
            COUNT(OrderID) AS OrderCount
        FROM Orders
        GROUP BY OrderStatus
        ORDER BY OrderCount DESC
    """)
    order_status_counts = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "reports.html",
        revenue_by_restaurant=revenue_by_restaurant,
        top_selling_items=top_selling_items,
        top_customers=top_customers,
        average_ratings=average_ratings,
        order_status_counts=order_status_counts
    )