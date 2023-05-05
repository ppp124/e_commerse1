from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson.objectid import ObjectId


app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')
db = client['ecommerce_db']

###########################################################################################################
# Retrieve all products

'''
@app.route('/products', methods=['GET'])
def get_products():
    products = []
    for product in db.products.find():
        products.append({'name': product['name'], 'description': product['description'], 'price': product['price'],
                         'stock_quantity': product['stock_quantity']})
    return jsonify({'result': products})
    
###############################################

@app.route('/products', methods=['GET'])
def get_products():
    result = db.products.find({}, {'_id': 0}) # exclude the '_id' field from the result
    return jsonify({'result': [product for product in result]})
'''


# new code with changes

@app.route('/products', methods=['GET'])
def get_products():
    result = db.products.find({})
    products = [{'product_id': str(product['_id']), 'name': product['name'], 'description': product['description'],
                 'price': product['price'], 'stock_quantity': product['stock_quantity']} for product in result]
    return jsonify({'result': products})


############################################################################################################################################

# Retrieve particular product with ID

@app.route('/products_withID/<id>', methods=['GET'])
def get_product(id):
    product = db.products.find_one({'_id': ObjectId(id)})
    if product:
        product['_id'] = str(product['_id'])
        return jsonify({'product': product})
    else:
        return jsonify({'error': 'Product not found'})


##########################################################################################################################################

# Create a new product

'''
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

    result = db.products.insert_one(product)
    if not result.acknowledged:
        return jsonify({'error': 'Failed to create product'}), 500

    return jsonify({'message': 'Product created successfully'}), 201
'''


# with stock initially as 0

@app.route('/products', methods=['POST'])
def create_product():
    name = request.json.get('name')
    description = request.json.get('description')
    price = request.json.get('price')
    stock_quantity = request.json.get('stock_quantity', 0)

    if not name or not description or not price:
        return jsonify({'error': 'Missing required fields'}), 400

    product = {
        'name': name,
        'description': description,
        'price': price,
        'stock_quantity': stock_quantity
    }

    result = db.products.insert_one(product)
    if not result.acknowledged:
        return jsonify({'error': 'Failed to create product'}), 500

    return jsonify({'message': 'Product created successfully'}), 201


##############################################################################################################################################

# DELETE a specific product

'''
@app.route('/products/<product_name>', methods=['DELETE'])
def delete(product_name):
    # Find the product in the database by its name
    product = db.products.find_one({'name': product_name})
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    # Delete the product from the database
    db.products.delete_one({'name': product_name})

    # Return a success message
    return jsonify({'success': f'{product_name} deleted successfully'}), 200
'''


# with changes delete with id

@app.route('/products/<id>', methods=['DELETE'])
def delete_product(id):
    result = db.products.delete_one({'_id': ObjectId(id)})
    if result.deleted_count == 1:
        return jsonify({'message': 'Product deleted successfully'})
    else:
        return jsonify({'error': 'Product not found'})


##############################################################################################################################

# update the product
'''
@app.route('/products/<product_name>', methods=['PUT'])
def update_product(product_name):
    product = db.products.find_one({'name': product_name})
    if product is None:
        return jsonify({'error': 'Product not found.'}), 404
    name = request.json.get('name', product['name'])
    description = request.json.get('description', product['description'])
    price = request.json.get('price', product['price'])
    stock_quantity = request.json.get('stock_quantity', product['stock_quantity'])
    db.products.update_one({'name': product_name}, {'$set': {'name': name, 'description': description, 'price': price, 'stock_quantity': stock_quantity}})
    updated_product = db.products.find_one({'name': name})
    output = {'name': updated_product['name'], 'description': updated_product['description'], 'price': updated_product['price'], 'stock_quantity': updated_product['stock_quantity']}
    return jsonify({'result': output})
'''


# updated with changes

@app.route('/products/<id>', methods=['PUT'])
def update_product(id):
    product = db.products.find_one({'_id': ObjectId(id)})
    if product:
        # Prompt user for the field to update
        field = input('Enter the field to update (name, description, price, stock_quantity): ')
        if field in ['name', 'description', 'price', 'stock_quantity']:
            # Prompt user for the new value
            value = input(f'Enter the new value for {field}: ')
            if field == 'price':
                value = float(value)
            elif field == 'stock_quantity':
                value = int(value)
            db.products.update_one({'_id': ObjectId(id)}, {'$set': {field: value}})
            updated_product = db.products.find_one({'_id': ObjectId(id)})
            updated_product['_id'] = str(updated_product['_id'])
            return jsonify({'product': updated_product})
        else:
            return jsonify({'error': 'Invalid field name'})
    else:
        return jsonify({'error': 'Product not found'})


############################################                ################################################
############################################-----ORDERS-----################################################
############################################                ################################################

'''
@app.route('/orders', methods=['POST'])
def place_order():
    order = {
        'customer_name': request.json['customer_name'],
        'email_address': request.json['email_address'],
        'shipping_address': request.json['shipping_address'],
        'products': request.json['products']
    }
    order_id = db.orders.insert_one(order).inserted_id
    return jsonify({'order_id': str(order_id)})
'''


# with changes

@app.route('/place_order', methods=['POST'])
def place_order():
    customer_name = request.json.get('customer_name')
    email_address = request.json.get('email_address')
    shipping_address = request.json.get('shipping_address')
    products = request.json.get('products')

    if not customer_name or not email_address or not shipping_address or not products:
        return jsonify({'error': 'Missing required fields'}), 400

    order_products = []

    product_id = input(f"Enter the ID of the product  that you want to order: ")
    stock_quantity = int(input(f"Enter the desired quantity for the product  "))

    db_product = db.products.find_one({'_id': ObjectId(product_id)})
    if not db_product:
        return jsonify({'error': f"Product with ID  not found"}), 404

    if db_product['stock_quantity'] < stock_quantity:
        return jsonify({'error': f"Not enough stock available for product "}), 400

    order_products.append({
        # 'product_name': product['name'],
        'product_id': ObjectId(product_id),
        'quantity': stock_quantity,
        'price': db_product['price']
    })

    db.products.update_one({'_id': ObjectId(product_id)}, {'$inc': {'stock_quantity': -stock_quantity}})

    order = {
        'customer_name': customer_name,
        'email_address': email_address,
        'shipping_address': shipping_address,
        'products': order_products,
        'status': 'Pending'
    }

    result = db.orders.insert_one(order)
    if not result.acknowledged:
        return jsonify({'error': 'Failed to create order'}), 500

    return jsonify({'message': 'Order created successfully'}), 201


#########################################################################3
'''
@app.route('/orders/<name>', methods=['GET'])
def get_order_history(name):
    customer_orders = list(db.orders.find_one({'customer_name': name}))
    return jsonify({'customer_orders': customer_orders})
'''

# get the order history
'''
@app.route('/orders/history', methods=['GET'])
def get_order_history2():
    customer_name = request.json.get('customer_name')
    if not customer_name:
        return jsonify({'error': 'Customer name is required'}), 400
    orders = db.orders.find({'customer_name': customer_name})
    output = []
    for order in orders:
        output.append({
            'id': str(order['_id']),
            'customer_name': order['customer_name'],
            'email_address': order['email_address'],
            'shipping_address': order['shipping_address'],
            'products': order['products'],
            'status': order.get('status', 'pending')
        })
    return jsonify({'result': output})



@app.route('/orders_history', methods=['GET'])
def get_order_history():
    customer_email = request.json.get('email_address')
    orders = []
    # for order in db.orders.find({'customer_email': customer_email}):
    orders = db.orders.find({'email_address': customer_email})
    output = []
    for order in orders:
        output.append({
            'id': str(order['_id']),
            'customer_name': order['customer_name'],
            'email_address': order['email_address'],
            'shipping_address': order['shipping_address'],
            'products': order['products'],
            'status': order.get('status', 'pending')
        })
    return jsonify({'result': output})

@app.route('/orders', methods=['GET'])
def get_orders():
    orders = list(db.orders.find())
    for order in orders:
        order['_id'] = str(order['_id'])
    return jsonify({'orders': orders})
'''
#_______________________running code______________________________

def convert_object_id(data):
    if isinstance(data, list):
        return [convert_object_id(item) for item in data]
    elif isinstance(data, dict):
        return {k: convert_object_id(v) for k, v in data.items() if k != '_id'}
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data
@app.route('/orderss', methods=['GET'])
def get_orders3():
    orders = db.orders.find()
    result = [convert_object_id(order) for order in orders]
    return jsonify({'orders': result})
#_________________________________________________________________

#with email Id
@app.route('/orders_history', methods=['GET'])
def get_order_history():
    customer_email = request.json.get('email_address')
    orders = []
    # for order in db.orders.find({'customer_email': customer_email}):
    orders = db.orders.find({'email_address': customer_email})
    result = [convert_object_id(order) for order in orders]
    return jsonify({'orders': result})


####################################################################################
@app.route('/filter_price', methods=['GET'])
def filter_products_by_price():
    min_price = float(request.json.get('min_price', 0))
    max_price = float(request.json.get('max_price', float('inf')))
    print(min_price, max_price)
    print("hiiiiiiiiiiiiiiiiiiiiii")
    filtered_products = []
    for product in db.products.find({'price': {'$gte': min_price, '$lte': max_price}}):
        filtered_products.append({
            'name': product['name'],

            'price': product['price'],

        })

    return jsonify({'result': filtered_products})


###############################################################################################

# Return the order

@app.route('/return', methods=['POST'])
def return_product():
    order_id = input(f"Enter the ID of the order  that you want to return: ")
    quantity = eval(input(f"Enter the Quantity of the product  that you want to return: "))
    product_id = input(f"Enter the ID of the product  that you want to return: ")
    if not order_id or not quantity:
        return jsonify({'error': 'Missing required fields'}), 400

    # Check if the order exists
    order = db.orders.find_one({'_id': ObjectId(order_id)})
    if not order:
        return jsonify({'error': f"Order with ID '{order_id}' not found"}), 404

    # Calculate the new stock quantity for the product
    product = db.products.find_one({'_id': ObjectId(product_id)})
    new_quantity = product['stock_quantity'] + quantity

    # Update the product stock quantity
    result = db.products.update_one({'_id': ObjectId(product_id)}, {'$set': {'stock_quantity': new_quantity}})
    if not result.acknowledged:
        return jsonify({'error': 'Failed to update product stock quantity'}), 500

    return jsonify({'message': f"Returned {quantity} units of product with ID '{product_id}'"}), 200


#####################################################################################################
if __name__ == '__main__':
    app.run(debug=True)
