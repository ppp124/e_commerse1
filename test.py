from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient

app = Flask(__name__)

# Set up MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['ecommerce_db']
# Products routes

@app.route('/products')
def index():
    products = list(db.products.find())
    return render_template('index2.html', products=products)


if __name__ == '__main__':
    app.run()
