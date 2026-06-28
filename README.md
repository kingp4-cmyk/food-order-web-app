# Food Order Web App

A local food ordering and courier management web application built with **Flask, MySQL, HTML and CSS**.

This project simulates a food ordering system where users can browse restaurants, view menus, add food items to the cart, place orders, select payment options, track order status and write restaurant reviews. The system also includes admin and delivery management pages for restaurant, courier and order operations.

## Features

* Restaurant listing
* Restaurant search
* Menu browsing
* Add food items to cart
* Cart and checkout flow
* Customer information form
* Payment method selection
* Courier selection
* Order success page
* My Orders page
* Order and courier status tracking
* Restaurant review and rating system
* Admin panel for restaurant management
* Delivery operation page for updating order status
* MySQL database integration

## Technologies Used

* Python
* Flask
* MySQL
* HTML
* CSS
* Jinja Templates

## Project Structure

```txt
food-order-web-app
├── app.py
├── db.py
├── routes
├── static
├── templates
├── screenshots
├── food_order_database.sql
└── README.md
```

## Screenshots

### Home Page

The home page allows users to browse local restaurants and search for food or restaurant names.

![Home Page](screenshots/home-page.png)

### Restaurant Menu

Users can select a restaurant, view menu items, choose quantities and add food to the cart.

![Restaurant Menu](screenshots/restaurant-menu.png)

### Cart Page

Users can review cart items, see the total amount and continue to checkout.

![Cart Page](screenshots/cart-page.png)

### Order Success Page

After checkout, the system creates an order and displays order, payment and customer information.

![Order Success Page](screenshots/order-success.png)

### Admin Panel

The admin panel allows restaurant, menu, customer, courier and delivery management.

![Admin Panel](screenshots/admin-panel.png)

### Delivery Management

Order and courier statuses can be updated through the delivery operation page.

![Delivery Management](screenshots/delivery-management.png)

## Database

The project uses a MySQL database. The database structure and sample data are included in:

```txt
food_order_database.sql
```

Before running the project, import this SQL file into MySQL and update the database connection settings in `db.py` if necessary.

## How to Run

### 1. Clone the repository

```bash
git clone https://github.com/kingp4-cmyk/food-order-web-app.git
cd food-order-web-app
```

### 2. Install dependencies

```bash
pip install flask mysql-connector-python
```

If your system uses Python 3 separately, use:

```bash
pip3 install flask mysql-connector-python
```

### 3. Import the database

Open MySQL Workbench and import:

```txt
food_order_database.sql
```

### 4. Check database connection

Open `db.py` and make sure the MySQL username, password and database name match your local MySQL settings.

### 5. Run the application

```bash
python app.py
```

or:

```bash
python3 app.py
```

### 6. Open the app

```txt
http://127.0.0.1:5000
```

## What I Learned

While building this project, I practiced:

* Building web applications with Flask
* Creating dynamic pages with Jinja templates
* Connecting Flask to a MySQL database
* Designing cart and checkout logic
* Managing order, payment and delivery status
* Creating admin and delivery management pages
* Structuring a multi-page web application
* Working with relational database tables and queries

## Project Scope

This project was developed as a local food ordering and courier management system. It includes user-facing restaurant and order pages, database-backed order operations, admin management pages and delivery status tracking.

