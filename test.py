from flask import Flask, render_template, request, redirect, url_for, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# Set up MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['ecommerce_db2']

@app.route('/products2', methods=['GET'])
def get_products2():
    products = []
    for product in db.products2.find():
        products.append({'name': product['name'], 'description': product['description'], 'price': product['price'],'stock_quantity': product['stock_quantity']})
    return jsonify({'result': products})

@app.route('/products', methods=['POST'])
def create_product():
    name = request.json.get('name')
    description = request.json.get('description')
    price = request.json.get('price')
    stock_quantity = request.json.get('stock_quantity')

    if not name or not description or not price or not stock_quantity:
        return jsonify({'error': 'Missing required fields'}), 400

    product = {
        'name': name,
        'description': description,
        'price': price,
        'stock_quantity': stock_quantity
    }

    result = db.product2.insert_one(product)
    if not result.acknowledged:
        return jsonify({'error': 'Failed to create product'}), 500

    return jsonify({'message': 'Product created successfully'}), 201

# Products routes
'''
@app.route('/products')
def index():
    products = list(db.products.find())
    return render_template('index2.html', products=products)


@app.route('/filter', methods=['GET'])
def get_products():
    name = request.args.get('name')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')

    if name:
        #query = db.products.find({"name": name})
        p= db.products.find({"name": name})

    if min_price and max_price:
        #query = db.products.find({"price": {"$gt": min_price, "$lt": max_price}})
        p= db.products.find({"price": {"$gt": min_price, "$lt": max_price}})
    elif min_price:
       # query = db.products.findfind({"price": {"$gte": min_price}})
       p = db.products.find({"price": {"$gte": min_price}})
    elif max_price:
        #query = db.products.find({"price": {"$lte": max_price}})
        p = db.products.find({"price": {"$lte": max_price}})
   #products = db.products.find(query)
   # print(query)
    output = []
    product=[]
    for product in p:
        output.append({

            'name': product['name'],

            'price': product['price'],

        })
    return jsonify({'result': output})
'''

@app.route('/orders2', methods=['POST'])
def place_order():
    order = {
        'customer_name': request.json['customer_name'],
        'email_address': request.json['email_address'],
        'shipping_address': request.json['shipping_address'],
        'products': request.json['products'],
        'quantity': request.json['quantity']
    }
    order_id = db.orders2.insert_one(order).inserted_id
    return jsonify({'order_id': str(order_id)})


@app.route('/orders2/history', methods=['GET'])
def get_order_history():
    customer_name = request.json.get('customer_name')
    if not customer_name:
        return jsonify({'error': 'Customer name is required'}), 400
    orders = db.orders2.find({'customer_name': customer_name})
    output = []
    for order in orders:
        output.append({
            'id': str(order['_id']),
            'customer_name': order['customer_name'],
            'email_address': order['email_address'],
            'shipping_address': order['shipping_address'],
            'products': order['products'],
            'quantity': order['quantity'],
            'status': order.get('status', 'pending')
        })
    return jsonify({'result': output})

##################################################################################################################

# Retrieve all products or filter by name
@app.route('/filter_name', methods=['GET'])
def get_products():
    name_filter = request.json.get('customer_name')
    print(name_filter)
    query = {}
    if name_filter:
        query['customer_name'] = {'$regex': f'.*{name_filter}.*', '$options': 'i'}

    products = []
    print(query)
    for product in db.orders2.find(query):
        products.append({'name': product['customer_name'], 'products': product['products']})
    return jsonify({'result': products})

#####################################################################################################################
# Filter products by price range
@app.route('/filter_price', methods=['GET'])
def filter_products_by_price():
    min_price = float(request.json.get('min_price', 0))
    max_price = float(request.json.get('max_price', float('inf')))
    min_price = float(min_price)
    max_price = float(max_price)
    print(min_price,max_price)
    #print("hiiiiiiiiiiiiiiiiiiiiii")
    filtered_products = []
    for product in db.product2.find({'price': {'$gte': min_price, '$lte': max_price}}):
        filtered_products.append({
            'name': product['name'],

            'price': product['price'],

        })

    return jsonify({'result': filtered_products})
if __name__ == '__main__':
    app.run()
