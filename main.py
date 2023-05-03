from flask import Flask, jsonify, request
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')
db = client['ecommerce_db']

###########################################################################################################

# Retrieve all products
@app.route('/products', methods=['GET'])
def get_products():
    products = []
    for product in db.products.find():
        products.append({'name': product['name'], 'description': product['description'], 'price': product['price'],'stock_quantity': product['stock_quantity']})
    return jsonify({'result': products})



#############################################################################################################

# Create a new product
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

##############################################################################################################################################

# Retrieve a specific product
'''
@app.route('/products/<product_id>', methods=['GET'])
def get_product(product_id):
    product = db.products.find_one_or_404({'_id': product_id})
    output = {'name': product['name'], 'description': product['description'], 'price': product['price']}
    return jsonify({'result': output})

'''
##########################################################################################################################

# DELETE a specific product
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


#####################################################################################################################


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

############################################-----ORDERS-----################################################


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
#########################################################################3
@app.route('/orders/<name>', methods=['GET'])
def get_order_history(name):
    customer_orders = list(db.orders.find({'name': name}))
    return jsonify({'customer_orders': customer_orders})

if __name__ == '__main__':
    app.run(debug=True)
