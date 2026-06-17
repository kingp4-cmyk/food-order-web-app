# Flask uygulamasını başlatmak.
# Herkesin route dosyasını projeye bağlamak.
# Ana sayfayı, restoran detay sayfasını ve ortak sayfaları açmak.

from routes.courier_operation_routes import courier_operation_bp
from flask import Flask, render_template, request
from db import get_db_connection

from routes.customer_order_routes import customer_order_bp
from routes.restaurant_menu_routes import restaurant_menu_bp
from routes.delivery_routes import delivery_bp
from routes.payment_review_report_routes import payment_review_report_bp
from routes.admin_routes import admin_bp

app = Flask(__name__)

# Session kullanacağımız için secret key gerekiyor.
# Bu, sepet/cart bilgisini geçici olarak tarayıcı oturumunda tutmak için kullanılır.
app.secret_key = "food_order_secret_key"

app.register_blueprint(courier_operation_bp)
app.register_blueprint(customer_order_bp)
app.register_blueprint(restaurant_menu_bp)
app.register_blueprint(delivery_bp)
app.register_blueprint(payment_review_report_bp)
app.register_blueprint(admin_bp)


@app.route("/")
def index():
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
        ORDER BY Rating DESC
    """)
    restaurants = cursor.fetchall()

    cursor.execute("""
        SELECT 
            mi.ItemID,
            mi.RestaurantID,
            mi.ItemName,
            mi.Price,
            mi.AvailabilityStatus,
            r.RestaurantName
        FROM MenuItems mi
        JOIN Restaurants r ON mi.RestaurantID = r.RestaurantID
        WHERE mi.AvailabilityStatus = 'Available'
        ORDER BY mi.ItemName
    """)
    menu_items = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "index.html",
        restaurants=restaurants,
        menu_items=menu_items
    )


@app.route("/restaurant/<int:restaurant_id>")
def restaurant_detail(restaurant_id):
    added = request.args.get("added")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            RestaurantID,
            RestaurantName,
            Address,
            Phone,
            Rating
            ImageURL
        FROM Restaurants
        WHERE RestaurantID = %s
    """, (restaurant_id,))

    restaurant = cursor.fetchone()

    cursor.execute("""
        SELECT 
            ItemID,
            RestaurantID,
            ItemName,
            Price,
            AvailabilityStatus
        FROM MenuItems
        WHERE RestaurantID = %s
          AND AvailabilityStatus = 'Available'
        ORDER BY ItemName
    """, (restaurant_id,))

    menu_items = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "restaurant_detail.html",
        restaurant=restaurant,
        menu_items=menu_items,
        added=added
    )


if __name__ == "__main__":
    app.run(debug=True, port=5001)