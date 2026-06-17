import mysql.connector


# ==========================================================
# DATABASE CONNECTION FILE
# ==========================================================
# Bu dosya Flask uygulamasını MySQL veritabanına bağlar.
#
# ÖNEMLİ:
# - Herkes aynı database adını kullanmalıdır: food_order_db
# - MySQL kullanıcı adı genelde "root" olur.
# - Password kısmı herkesin kendi bilgisayarındaki MySQL şifresidir.
# - Herkes kendi bilgisayarında password değerini kendi MySQL şifresine göre değiştirmelidir.
#
# ÖRNEK:
# Eğer senin MySQL şifren 12345 ise kendi bilgisayarında şöyle yazarsın:
#
# password="12345"
#
# Ama projeyi GitHub'a yüklemeden önce şifreyi tekrar şu hale getirmek daha güvenlidir:
#
# password="YOUR_MYSQL_PASSWORD"
#
# Çünkü gerçek MySQL şifrenizi GitHub'a koymamanız gerekir.
#
# Daha profesyonel yöntemde şifre .env dosyasına koyulur.
# Ancak bu proje için karışıklık olmaması adına şimdilik bu yöntem yeterlidir.
#
# Route dosyalarında veritabanına bağlanmak için şu satır kullanılacak:
# from db import get_db_connection
# ==========================================================


def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Pelin1234hpher",  # Buraya kendi MySQL şifreni .yaz.
        database="food_order_db"
    )

    return connection