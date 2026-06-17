# ==========================================================
# PERSON 3 - COURIER & DELIVERY MODULE
# ==========================================================
# Bu dosya 3. kişinin sorumlu olduğu route'ları içerir.
#
# Sorumlu sayfa:
# - deliveries.html
#
# Sorumlu tablolar:
# - Couriers
# - Deliveries
#
# Bu dosyada yapılacak işlemler:
# - Kurye listeleme
# - Kurye ekleme
# - Siparişe kurye atama
# - Teslimat durumu güncelleme
#
# NOT:
# Diğer kişiler bu dosyayı düzenlememelidir.
# Herkes sadece kendi route dosyasında çalışmalıdır.
# ==========================================================
from flask import Blueprint, render_template, request, redirect

delivery_bp = Blueprint("delivery", __name__)


@delivery_bp.route("/deliveries")
def deliveries():
    return render_template("deliveries.html")