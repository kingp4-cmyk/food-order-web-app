# ==========================================================
# PERSON 2 - RESTAURANT & MENU MODULE
# ==========================================================
# Bu dosya 2. kişinin sorumlu olduğu route'ları içerir.
#
# Sorumlu sayfa:
# - restaurants.html
#
# Sorumlu tablolar:
# - Restaurants
# - Categories
# - MenuItems
#
# Bu dosyada yapılan işlemler:
# - Restoran listeleme
# - Restoran ekleme
# - Kategori listeleme
# - Kategori ekleme
# - Menü ürünlerini listeleme
# - Menü ürünü ekleme
#
# NOT:
# Diğer kişiler bu dosyayı düzenlememelidir.
# Herkes sadece kendi route dosyasında çalışmalıdır.
# ==========================================================

from flask import Blueprint, render_template, request, redirect
from db import get_db_connection
import mysql.connector

restaurant_menu_bp = Blueprint("restaurant_menu", __name__)


@restaurant_menu_bp.route("/restaurants")
def restaurants():
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
        ORDER BY RestaurantID DESC
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
            mi.ItemName,
            mi.Price,
            mi.AvailabilityStatus,
            r.RestaurantID,
            r.RestaurantName,
            c.CategoryID,
            c.CategoryName
        FROM MenuItems mi
        JOIN Restaurants r ON mi.RestaurantID = r.RestaurantID
        JOIN Categories c ON mi.CategoryID = c.CategoryID
        ORDER BY r.RestaurantName, mi.ItemName
    """)
    menu_items = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "restaurants.html",
        restaurants=restaurants,
        categories=categories,
        menu_items=menu_items
    )


@restaurant_menu_bp.route("/add_restaurant", methods=["POST"])
def add_restaurant():
    restaurant_name = request.form["restaurant_name"]
    address = request.form["address"]
    phone = request.form["phone"]
    rating = request.form["rating"]

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT COALESCE(MAX(RestaurantID), 0) + 1 AS NewRestaurantID
            FROM Restaurants
        """)
        result = cursor.fetchone()
        new_restaurant_id = result["NewRestaurantID"]

        cursor.execute("""
            INSERT INTO Restaurants
            (RestaurantID, RestaurantName, Address, Phone, Rating)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            new_restaurant_id,
            restaurant_name,
            address,
            phone,
            rating
        ))

        connection.commit()

    except mysql.connector.Error as error:
        connection.rollback()
        print("Restaurant insert error:", error)

    cursor.close()
    connection.close()

    return redirect("/restaurants")


@restaurant_menu_bp.route("/add_category", methods=["POST"])
def add_category():
    category_name = request.form["category_name"]

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT COALESCE(MAX(CategoryID), 0) + 1 AS NewCategoryID
            FROM Categories
        """)
        result = cursor.fetchone()
        new_category_id = result["NewCategoryID"]

        cursor.execute("""
            INSERT INTO Categories
            (CategoryID, CategoryName)
            VALUES (%s, %s)
        """, (
            new_category_id,
            category_name
        ))

        connection.commit()

    except mysql.connector.Error as error:
        connection.rollback()
        print("Category insert error:", error)

    cursor.close()
    connection.close()

    return redirect("/restaurants")


@restaurant_menu_bp.route("/add_menu_item", methods=["POST"])
def add_menu_item():
    restaurant_id = request.form["restaurant_id"]
    category_id = request.form["category_id"]
    item_name = request.form["item_name"]
    price = request.form["price"]
    availability_status = request.form["availability_status"]

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT COALESCE(MAX(ItemID), 999) + 1 AS NewItemID
            FROM MenuItems
        """)
        result = cursor.fetchone()
        new_item_id = result["NewItemID"]

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
            availability_status
        ))

        connection.commit()

    except mysql.connector.Error as error:
        connection.rollback()
        print("Menu item insert error:", error)

    cursor.close()
    connection.close()

    return redirect("/restaurants")