-- ======================================================
-- 0. HAZIRLIK (VERİTABANI OLUŞTURMA)
-- ======================================================
DROP DATABASE IF EXISTS food_order_db;
CREATE DATABASE food_order_db;
USE food_order_db;

-- ======================================================
-- 1. ADIM: ANA TABLOLAR (Bağımsızlar)
-- ======================================================

-- 1. Kişi: Müşteriler
CREATE TABLE Customers (
    CustomerID INT AUTO_INCREMENT PRIMARY KEY,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    Phone VARCHAR(20),
    Email VARCHAR(100) UNIQUE NOT NULL,
    Address TEXT,
    RegistrationDate DATE NOT NULL
);

-- 2. Kişi: Restoranlar
CREATE TABLE Restaurants (
    RestaurantID INT PRIMARY KEY,
    RestaurantName VARCHAR(100) NOT NULL,
    Address VARCHAR(200),
    Phone VARCHAR(20),
    Rating DECIMAL(2,1)
);

-- 2. Kişi: Kategoriler
CREATE TABLE Categories (
    CategoryID INT PRIMARY KEY,
    CategoryName VARCHAR(100) NOT NULL
);

-- 3. Kişi: Kuryeler
CREATE TABLE Couriers (
    CourierID INT AUTO_INCREMENT PRIMARY KEY,
    FullName VARCHAR(100) NOT NULL,
    Phone VARCHAR(20),
    VehicleType ENUM('Motor', 'Bisiklet', 'Araba') DEFAULT 'Motor',
    IsActive BOOLEAN DEFAULT TRUE
);

-- ======================================================
-- 2. ADIM: İŞLEM TABLOLARI (Bağlantılılar)
-- ======================================================

-- 2. Kişi: Menü Ürünleri
CREATE TABLE MenuItems (
    ItemID INT PRIMARY KEY,
    RestaurantID INT NOT NULL,
    CategoryID INT NOT NULL,
    ItemName VARCHAR(100) NOT NULL,
    Price DECIMAL(10,2) NOT NULL,
    AvailabilityStatus VARCHAR(20) DEFAULT 'Available',
    FOREIGN KEY (RestaurantID) REFERENCES Restaurants(RestaurantID),
    FOREIGN KEY (CategoryID) REFERENCES Categories(CategoryID)
);

-- 1. Kişi: Siparişler
CREATE TABLE Orders (
    OrderID INT AUTO_INCREMENT PRIMARY KEY,
    CustomerID INT NOT NULL,
    RestaurantID INT NOT NULL,
    OrderDate DATETIME NOT NULL,
    TotalAmount DECIMAL(10,2) NOT NULL,
    OrderStatus VARCHAR(30) NOT NULL,
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID),
    FOREIGN KEY (RestaurantID) REFERENCES Restaurants(RestaurantID)
);

-- 1. Kişi: Sipariş İçeriği (Cross Table)
CREATE TABLE OrderItems (
    OrderItemID INT AUTO_INCREMENT PRIMARY KEY,
    OrderID INT NOT NULL,
    ItemID INT NOT NULL,
    Quantity INT NOT NULL,
    UnitPrice DECIMAL(10,2) NOT NULL,
    Subtotal DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
    FOREIGN KEY (ItemID) REFERENCES MenuItems(ItemID)
);

-- 3. Kişi: Teslimatlar
CREATE TABLE Deliveries (
    DeliveryID INT AUTO_INCREMENT PRIMARY KEY,
    OrderID INT NOT NULL,
    CourierID INT NOT NULL,
    DeliveryStatus ENUM('Hazırlanıyor', 'Kurye Bekleniyor', 'Yolda', 'Teslim Edildi'),
    PickupTime DATETIME,
    DeliveryTime DATETIME,
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
    FOREIGN KEY (CourierID) REFERENCES Couriers(CourierID)
);

-- ======================================================
-- 3. ADIM: SENİN TABLOLARIN (Person 4 - Ödemeler ve Yorumlar)
-- ======================================================

-- 4. Kişi: Ödemeler
CREATE TABLE Payments (
    PaymentID INT AUTO_INCREMENT PRIMARY KEY,
    OrderID INT NOT NULL UNIQUE,
    Amount DECIMAL(10, 2) NOT NULL,
    PaymentMethod ENUM('Kredi Kartı', 'Nakit', 'Online Ödeme'),
    PaymentStatus ENUM('Beklemede', 'Tamamlandı', 'İptal Edildi'),
    PaymentDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID)
);

-- 4. Kişi: Yorumlar
CREATE TABLE Reviews (
    ReviewID INT AUTO_INCREMENT PRIMARY KEY,
    CustomerID INT NOT NULL,
    RestaurantID INT NOT NULL, 
    Rating INT NOT NULL CHECK (Rating >= 1 AND Rating <= 5),
    Comment TEXT,
    ReviewDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID),
    FOREIGN KEY (RestaurantID) REFERENCES Restaurants(RestaurantID)
);

-- ======================================================
-- 4. ADIM: DEVASA VERİ GİRİŞİ (SİSTEMİ CANLANDIRMA)
-- ======================================================

-- 1. Kategoriler (9 Çeşit)
INSERT INTO Categories (CategoryID, CategoryName) VALUES 
(1, 'Burger'), (2, 'İçecek'), (3, 'Pizza'), (4, 'Dürüm & Kebap'), 
(5, 'Tatlı'), (6, 'Salata'), (7, 'Uzak Doğu / Sushi'), 
(8, 'Ev Yemekleri'), (9, 'Kahvaltı & Fırın');

-- 2. Restoranlar (8 Farklı Restoran)
INSERT INTO Restaurants (RestaurantID, RestaurantName, Address, Phone, Rating) VALUES 
(1, 'Burger House', 'Alanya Merkez', '02425110001', 4.5),
(2, 'Pizza Pizza', 'Alanya Damlataş', '02425110002', 4.2),
(3, 'Dürümle', 'Alanya Sanayi', '02425110003', 4.8),
(4, 'Tatlı Dünyası', 'Alanya Sahil', '02425110004', 4.6),
(5, 'Sushi Express', 'Alanya Mahmutlar', '02425110005', 4.7),
(6, 'Anne Eli Ev Yemekleri', 'Alanya Oba', '02425110006', 4.4),
(7, 'Vegan & Fit', 'Alanya Cikcilli', '02425110007', 4.9),
(8, 'Günaydın Fırın', 'Alanya Tosmur', '02425110008', 4.3);

-- 3. Müşteriler (8 Müşteri)
INSERT INTO Customers (FirstName, LastName, Phone, Email, Address, RegistrationDate) VALUES 
('Ali', 'Yılmaz', '05551234567', 'ali.yilmaz@example.com', 'Alanya/Saray', '2026-04-01'),
('Ayşe', 'Kaya', '05551112233', 'ayse@example.com', 'Alanya/Mahmutlar', '2026-04-02'),
('Fatma', 'Demir', '05552223344', 'fatma@example.com', 'Alanya/Oba', '2026-04-03'),
('Mehmet', 'Çelik', '05553334455', 'mehmet@example.com', 'Alanya/Kestel', '2026-04-05'),
('Zeynep', 'Şahin', '05554445566', 'zeynep@example.com', 'Alanya/Merkez', '2026-04-10'),
('Can', 'Öztürk', '05559998877', 'can@example.com', 'Alanya/Damlataş', '2026-04-12'),
('Elif', 'Aydın', '05557776655', 'elif@example.com', 'Alanya/Cikcilli', '2026-04-15'),
('Burcu', 'Yıldız', '05558889900', 'burcu@example.com', 'Alanya/Tosmur', '2026-04-20');

-- 4. Kuryeler (5 Kurye)
INSERT INTO Couriers (FullName, Phone, VehicleType, IsActive) VALUES 
('Hakan Hızlı', '05449998877', 'Motor', TRUE),
('Burak Yılmaz', '05448887766', 'Motor', TRUE),
('Caner Çevik', '05447776655', 'Bisiklet', TRUE),
('Ahmet Uçar', '05441112233', 'Motor', TRUE),
('Sinan Yılmaz', '05445554433', 'Araba', TRUE);

-- 5. Menü Ürünleri (50+ Çeşit)
INSERT INTO MenuItems (ItemID, RestaurantID, CategoryID, ItemName, Price, AvailabilityStatus) VALUES 
(1001, 1, 1, 'Chicken Burger', 180.00, 'Available'),
(1002, 1, 1, 'Double Cheese Burger', 250.00, 'Available'),
(1003, 1, 1, 'Mushroom Burger', 220.00, 'Available'),
(1004, 1, 1, 'Texas Smoke Burger', 270.00, 'Available'),
(1005, 1, 2, 'Coca Cola 330ml', 45.00, 'Available'),
(1006, 1, 2, 'Patates Kızartması', 75.00, 'Available'),
(2001, 2, 3, 'Margarita Pizza', 200.00, 'Available'),
(2002, 2, 3, 'Karışık Pizza', 280.00, 'Available'),
(2003, 2, 3, 'Pepperoni Pizza', 260.00, 'Available'),
(2004, 2, 3, 'Dört Peynirli Pizza', 290.00, 'Available'),
(2005, 2, 6, 'Sezar Salata', 150.00, 'Available'),
(2006, 2, 2, 'Ev Yapımı Limonata', 55.00, 'Available'),
(3001, 3, 4, 'Adana Dürüm', 190.00, 'Available'),
(3002, 3, 4, 'Urfa Dürüm', 190.00, 'Available'),
(3003, 3, 4, 'Tavuk Şiş Dürüm', 160.00, 'Available'),
(3004, 3, 4, 'Ciğer Dürüm', 200.00, 'Available'),
(3005, 3, 4, 'İskender', 350.00, 'Available'),
(3006, 3, 2, 'Açık Ayran', 35.00, 'Available'),
(4001, 4, 5, 'Fıstıklı Baklava (Porsiyon)', 180.00, 'Available'),
(4002, 4, 5, 'Sütlaç', 90.00, 'Available'),
(4003, 4, 5, 'Kazandibi', 95.00, 'Available'),
(4004, 4, 5, 'Cheesecake (Limonlu)', 140.00, 'Available'),
(4005, 4, 2, 'Filtre Kahve', 70.00, 'Available'),
(5001, 5, 7, 'California Roll (8 Adet)', 320.00, 'Available'),
(5002, 5, 7, 'Philadelphia Roll (8 Adet)', 340.00, 'Available'),
(5003, 5, 7, 'Sake Nigiri (Somon)', 180.00, 'Available'),
(5004, 5, 7, 'Tavuklu Noodle', 210.00, 'Available'),
(5005, 5, 5, 'Mochi Tatlısı', 120.00, 'Available'),
(5006, 5, 2, 'Yeşil Çay', 60.00, 'Available'),
(6001, 6, 8, 'Kuru Fasulye & Pilav', 170.00, 'Available'),
(6002, 6, 8, 'Mercimek Çorbası', 70.00, 'Available'),
(6003, 6, 8, 'Karnıyarık', 190.00, 'Available'),
(6004, 6, 8, 'Zeytinyağlı Sarma', 150.00, 'Available'),
(6005, 6, 2, 'Ev Yoğurdu', 40.00, 'Available'),
(7001, 7, 6, 'Kinoa Salata Kasesi', 220.00, 'Available'),
(7002, 7, 6, 'Izgara Tofu Salata', 240.00, 'Available'),
(7003, 7, 1, 'Vegan Falafel Burger', 210.00, 'Available'),
(7004, 7, 2, 'Yeşil Detox Suyu', 90.00, 'Available'),
(7005, 7, 5, 'Şekersiz Yulaf Bar', 85.00, 'Available'),
(8001, 8, 9, 'Serpme Kahvaltı (Tek Kişilik)', 350.00, 'Available'),
(8002, 8, 9, 'Su Böreği (Porsiyon)', 110.00, 'Available'),
(8003, 8, 9, 'Simit & Kaşar Tabağı', 95.00, 'Available'),
(8004, 8, 9, 'Menemen', 140.00, 'Available'),
(8005, 8, 2, 'Taze Sıkılmış Portakal Suyu', 75.00, 'Available'),
(8006, 8, 2, 'Demleme Çay', 25.00, 'Available');

-- 6. Siparişler (20 Sipariş)
INSERT INTO Orders (CustomerID, RestaurantID, OrderDate, TotalAmount, OrderStatus) VALUES 
(1, 1, '2026-05-09 12:30:00', 360.00, 'Delivered'),
(2, 3, '2026-05-09 13:15:00', 380.00, 'Delivered'),
(3, 2, '2026-05-09 14:00:00', 280.00, 'Delivered'),
(4, 5, '2026-05-09 15:45:00', 530.00, 'Delivered'),
(5, 6, '2026-05-09 18:00:00', 240.00, 'Delivered'),
(6, 8, '2026-05-09 09:30:00', 165.00, 'Delivered'),
(7, 7, '2026-05-09 19:15:00', 310.00, 'Pending'),
(8, 4, '2026-05-09 20:00:00', 270.00, 'Pending'),
(1, 3, '2026-05-09 12:00:00', 190.00, 'Delivered'),
(2, 5, '2026-05-09 12:45:00', 320.00, 'Delivered'),
(3, 7, '2026-05-09 13:30:00', 220.00, 'Delivered'),
(4, 1, '2026-05-09 14:15:00', 450.00, 'Delivered'),
(5, 2, '2026-05-09 15:00:00', 280.00, 'Delivered'),
(6, 4, '2026-05-09 15:45:00', 180.00, 'Delivered'),
(7, 6, '2026-05-09 16:30:00', 170.00, 'Delivered'),
(8, 8, '2026-05-09 17:15:00', 350.00, 'Delivered'),
(1, 5, '2026-05-09 18:00:00', 660.00, 'Delivered'),
(2, 2, '2026-05-09 18:45:00', 560.00, 'Delivered'),
(3, 3, '2026-05-09 19:30:00', 410.00, 'Pending'),
(4, 1, '2026-05-09 20:15:00', 520.00, 'Pending');

-- 7. Sipariş İçerikleri
INSERT INTO OrderItems (OrderID, ItemID, Quantity, UnitPrice, Subtotal) VALUES 
(1, 1001, 2, 180.00, 360.00), 
(2, 3001, 2, 190.00, 380.00), 
(3, 2002, 1, 280.00, 280.00), 
(4, 5001, 1, 320.00, 320.00), 
(4, 5004, 1, 210.00, 210.00), 
(5, 6001, 1, 170.00, 170.00), 
(5, 6002, 1, 70.00, 70.00),   
(6, 8004, 1, 140.00, 140.00), 
(6, 8006, 1, 25.00, 25.00),   
(7, 7001, 1, 220.00, 220.00), 
(7, 7004, 1, 90.00, 90.00),   
(8, 4001, 1, 180.00, 180.00), 
(8, 4002, 1, 90.00, 90.00),
(9, 3001, 1, 190.00, 190.00),
(10, 5001, 1, 320.00, 320.00),
(11, 7001, 1, 220.00, 220.00),
(12, 1002, 1, 250.00, 250.00),
(12, 1001, 1, 200.00, 200.00),
(13, 2002, 1, 280.00, 280.00),
(14, 4001, 1, 180.00, 180.00),
(15, 6001, 1, 170.00, 170.00),
(16, 8001, 1, 350.00, 350.00),
(17, 5002, 2, 330.00, 660.00),
(18, 2002, 2, 280.00, 560.00),
(19, 3004, 2, 205.00, 410.00),
(20, 1004, 2, 260.00, 520.00);

-- 8. Teslimatlar
INSERT INTO Deliveries (OrderID, CourierID, DeliveryStatus, PickupTime, DeliveryTime) VALUES 
(1, 1, 'Teslim Edildi', '2026-05-09 12:45:00', '2026-05-09 13:10:00'),
(2, 2, 'Teslim Edildi', '2026-05-09 13:30:00', '2026-05-09 13:50:00'),
(3, 3, 'Teslim Edildi', '2026-05-09 14:20:00', '2026-05-09 14:40:00'),
(4, 4, 'Teslim Edildi', '2026-05-09 16:05:00', '2026-05-09 16:30:00'),
(5, 1, 'Teslim Edildi', '2026-05-09 18:20:00', '2026-05-09 18:45:00'),
(6, 5, 'Teslim Edildi', '2026-05-09 09:45:00', '2026-05-09 10:05:00'),
(9, 1, 'Teslim Edildi', '2026-05-09 12:10:00', '2026-05-09 12:35:00'),
(10, 2, 'Teslim Edildi', '2026-05-09 12:55:00', '2026-05-09 13:20:00'),
(11, 3, 'Teslim Edildi', '2026-05-09 13:45:00', '2026-05-09 14:10:00'),
(12, 4, 'Teslim Edildi', '2026-05-09 14:30:00', '2026-05-09 14:55:00'),
(13, 5, 'Teslim Edildi', '2026-05-09 15:15:00', '2026-05-09 15:40:00'),
(14, 1, 'Teslim Edildi', '2026-05-09 16:00:00', '2026-05-09 16:25:00'),
(15, 2, 'Teslim Edildi', '2026-05-09 16:45:00', '2026-05-09 17:10:00'),
(16, 3, 'Teslim Edildi', '2026-05-09 17:30:00', '2026-05-09 17:55:00'),
(17, 4, 'Teslim Edildi', '2026-05-09 18:15:00', '2026-05-09 18:40:00'),
(18, 5, 'Teslim Edildi', '2026-05-09 19:00:00', '2026-05-09 19:25:00');

-- 9. Ödemeler
INSERT INTO Payments (OrderID, Amount, PaymentMethod, PaymentStatus) VALUES 
(1, 360.00, 'Kredi Kartı', 'Tamamlandı'),
(2, 380.00, 'Online Ödeme', 'Tamamlandı'),
(3, 280.00, 'Nakit', 'Tamamlandı'),
(4, 530.00, 'Kredi Kartı', 'Tamamlandı'),
(5, 240.00, 'Nakit', 'Tamamlandı'),
(6, 165.00, 'Kredi Kartı', 'Tamamlandı'),
(7, 310.00, 'Online Ödeme', 'Beklemede'),
(8, 270.00, 'Nakit', 'Beklemede'),
(9, 190.00, 'Nakit', 'Tamamlandı'),
(10, 320.00, 'Kredi Kartı', 'Tamamlandı'),
(11, 220.00, 'Online Ödeme', 'Tamamlandı'),
(12, 450.00, 'Kredi Kartı', 'Tamamlandı'),
(13, 280.00, 'Nakit', 'Tamamlandı'),
(14, 180.00, 'Online Ödeme', 'Tamamlandı'),
(15, 170.00, 'Kredi Kartı', 'Tamamlandı'),
(16, 350.00, 'Nakit', 'Tamamlandı'),
(17, 660.00, 'Online Ödeme', 'Tamamlandı'),
(18, 560.00, 'Kredi Kartı', 'Tamamlandı'),
(19, 410.00, 'Nakit', 'Beklemede'),
(20, 520.00, 'Online Ödeme', 'Beklemede');

-- 10. Yorumlar
INSERT INTO Reviews (CustomerID, RestaurantID, Rating, Comment) VALUES 
(1, 3, 5, 'Adana dürüm gerçekten efsaneydi, bölgedeki en iyi yer.'),
(2, 5, 4, 'Sushi sunumu çok şıktı, lezzet de yerinde.'),
(3, 7, 5, 'Vegan seçeneklerin olması harika, salata çok tazeydi.'),
(4, 1, 3, 'Burger lezzetli ama patatesler biraz soğuk gelmişti.'),
(5, 2, 5, 'Karışık pizza bol malzemeli ve hamuru incecikti.'),
(6, 4, 4, 'Sütlaç kıvamı tam istediğim gibi, teşekkürler.'),
(7, 6, 5, 'Kuru fasulye pilav ikilisi tam bir ev yemeği tadında.'),
(8, 8, 4, 'Kahvaltı ürünleri taze ve doyurucu.'),
(1, 5, 5, 'Philadelphia roll mutlaka denenmeli, harika.'),
(2, 2, 2, 'Pizzanın kenarları biraz yanmıştı, bu sefer beğenmedim.'),
(3, 3, 5, 'Ciğer dürüm çok yumuşak ve lezzetliydi.'),
(4, 1, 4, 'Double cheese burger doyuruculuğu 10 numara.'),
(5, 7, 5, 'Detox suları çok ferahlatıcı, sağlıklı beslenmek isteyenlere öneririm.'),
(6, 4, 5, 'Fıstıklı baklava taptazeydi, şerbeti tam kararında.');

UPDATE Restaurants
SET ImageURL = '/Users/pelinozdemir/Downloads/burger.jpeg'
WHERE RestaurantID = 1;