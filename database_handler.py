from datetime import datetime
import time
from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY
import random

# Create a Flask application
app = Flask(__name__)

# Configure the application to use a SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Product_catalog.db"
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_FILE_DIR'] = '/tmp/flask_session'
app.config['SESSION_FILE_THRESHOLD'] = 500
app.config['SESSION_FILE_MODE'] = 384
# Initialize the database object
db = SQLAlchemy(app)
Session(app)

# Define a Product model class
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(255), nullable=False)
    company_name = db.Column(db.String(255), nullable=False)
    environmental_impact = db.Column(db.Float, nullable=False)
    delivery_fee = db.Column(db.Float, nullable=False)
    collection = db.Column(db.String(255), nullable=False)
    

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_ordered = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(50), nullable=False, default="Pending")
    total_price = db.Column(db.Float, nullable=False)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

# Create a function to reinitialize the database
def reinitialize_database():
    # Drop all existing tables
    with app.app_context():
        db.drop_all()

        # Create the tables
        db.create_all()

        # Add some example data to the database
        names = ["Organic Cotton T-Shirt", "Bamboo Socks", "Recycled Plastic Water Bottle", "Hemp Backpack", "Reusable Beeswax Wraps", "Fair Trade Chocolate Bar", "Upcycled Denim Jeans", "Eco-Friendly Yoga Mat", "Sustainable Wood Cutting Board", "Recycled Glass Vase"]
        prices = [10.99, 14.99, 7.99, 39.99, 16.99, 3.99, 79.99, 24.99, 29.99, 12.99]
        companies = ["EarthWear", "EcoLife", "GreenGoods", "SustainCo", "PlanetFriendly", "EcoEssentials", "ConsciousChoice", "EcoCoast", "GreenGenie", "EcoProducts"]
        impacts = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        collection_method = ["Click and Collect", "Delivery", "Free Delivery"]
        characters_to_remove = [",", ".", " ", "-"]
        for _ in range(10):
            curr_item = random.randint(0, len(names)-1)
            image = "".join([char for char in names[curr_item] if char not in characters_to_remove]) + ".png"
            name = names.pop(curr_item)
            price = random.choice(prices)
            company_name = random.choice(companies)
            environmental_impact = random.choice(impacts)
            random_collection = random.randint(0, 2)
            if random_collection == 1:
                delivery_fee = round(random.randint(1, 10) + round(random.random(), 2), 2)
                collection = collection_method[random_collection]
            else:
                delivery_fee = 0
                collection = collection_method[random_collection]
            item = Product(name = name, price = price, image = image, company_name = company_name, environmental_impact = environmental_impact, delivery_fee = delivery_fee, collection = collection)
            db.session.add(item)
        db.session.commit()

    print("Database reinitialized")

def read_table(tablename):
    with app.app_context():
        table_class = db.Model._decl_class_registry.get(tablename)
        if table_class:
            results = table_class.query.all()
            return results
        else:
            print(f"Table {tablename} not found")
            return None

def read_all():
    # Query all records from the Product table
    with app.app_context():
        products = Product.query.all()
        orders = Order.query.all()
        orderitems = OrderItem.query.all()
    results = []
    for product in products:
        result_dict = {}
        for key, value in product.__dict__.items():
            if not key.startswith('_') and key != 'metadata':
                result_dict[key] = value
        results.append(result_dict)
    for order in orders:
        result_dict = {}
        for key, value in order.__dict__.items():
            if not key.startswith("_") and key != 'metadata':
                result_dict[key] = value
        results.append(result_dict)
    for orderitem in orderitems:
        result_dict = {}
        for key, value in orderitem.__dict__.items():
            if not key.startswith("_") and key != 'metadata':
                result_dict[key] = value
        results.append(result_dict)
    return results

# Run the reinitialize_database function when the program is executed
if __name__ == '__main__':
    done = False
    while not done:
        print()
        print("Enter 2 to read all;")
        print("Enter 3 to reinitialise the database;")
        print("Enter 4 to close the program. ")
        print("Please enter the function you wish to perform: ", end="")


        while True:
            try:
                ui = int(input())
                break
            except:
                print("Please enter the function you wish to perform: ", end="")

        if ui == 2:
            return_val = read_all()
            for pos in return_val:
                print(pos)
            time.sleep(1)
        elif ui == 3:
            reinitialize_database()
            time.sleep(1)

        elif ui == 4:
            done = True