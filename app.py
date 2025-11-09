import re
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, false
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from datetime import datetime
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
from model import *
#==================VALIDATE FUNCTION ==================
def stringChecker(param):
    if type(param) is not str:
        return {"message": "Bad request"}, 400

def falsyChecker(param):
    if not param:
        return abort(400)

def intChecker(param):
    if type(param) is not int:
        return {"message": "Bad request"}, 400

def getallinvoicedetail():
    invoice_details = InvoiceDetail.query.all()
    result = []
    for i in invoice_details:
        orderitem = OrderItem.query.get(i.orderitem_id)
        # assert False, orderitem
        data = {
            "id": i.id,
            "orderitem": {
                "id": orderitem.id,
                "order_id": orderitem.order_id,
                "product_id": orderitem.product_id,
                "price": orderitem.price,
                "quantity": orderitem.qty,
                "total": orderitem.total
            } if orderitem else None
        }
        result.append(data)
    return result
def getinvoicedetail(param):
    i = InvoiceDetail.query.get(param)
    orderitem = OrderItem.query.get(param)
    data = {
            "id": i.id,
            "orderitem": {
                "id": orderitem.id,
                "order_id": orderitem.order_id,
                "product_id": orderitem.product_id,
                "price": orderitem.price,
                "quantity": orderitem.qty,
                "total": orderitem.total
            } if orderitem else None
        }
    return data
def getorder(param):
    order = Order.query.get(param)
    if order is None:
        return None

    data = {
        "Order_id": order.id,
        "user_id": order.user_id,
        "customer_id": order.customer_id,
        "date_time": order.date_time,
        "status": order.status

    }
    return data
# ========================= BEGIN USER API ==========================
@app.route('/user/list')
def show_user():
    Users = User.query.all()
    # result = [{"id": c.id, "name": c.name} for c in categories]
    if not Users:
        return {"message": "no user"}, 404
    result = [{"id": c.id, "username": c.username, "email": c.email, "remark": c.remark} for c in Users]
    return {"User": result}, 200

@app.errorhandler(400)
def error_400(error):
    return 'Bad request', 400

# @app.errorhandler(500)
# def error_500(error):
#     return f'missing key: {error}', 500

@app.post('/user/create')
def create_user():
    req = request.json
    name = req.get("username")
    email = req["email"]
    password = req["password"]
    remark = req.get("remark")
    stringChecker(name)
    falsyChecker(name)
    result = re.search("@gmail.com", email)
    intChecker(password)
    falsyChecker(password)
    stringChecker(remark)
    if result is not None and email != "":
        sqlquery = text("INSERT INTO USER (username, email, password, remark) VALUES (:username, :email, :password, :remark)")
        db.session.execute(sqlquery, {"username": name, "email": email, "password": password, "remark": remark})
        db.session.commit()
        return 'resource created', 200
    else:
        return 'No email', 400

@app.put('/user/<int:id>/update')
def update_user(id):
    req = request.json
    name = req.get("username")
    email = req.get("email")
    user = User.query.get(id)
    if user and email is None:
        email = user.email
    remark = req.get("remark")
    stringChecker(name)
    falsyChecker(name)
    result = re.search("@gmail.com", email)
    if not result:
        return {"message": "missing email"}, 400
    sqlquery = text("UPDATE user SET username = :username, email = :email, remark = :remark WHERE id = :id")
    db.session.execute(sqlquery, {"username": name, "id": id, "email": email, "remark": remark})
    db.session.commit()
    return {"message": "resource is updated"}, 200

@app.delete('/user/<int:id>/delete')
def delete_user(id):
    sqlquery = text("DELETE FROM user WHERE id = :id")
    db.session.execute(sqlquery, {"id": id})
    db.session.commit()
    return {"message": "resource is delete"}, 200

# ========================= END USER API ======================

# ========================= BEGIN CATEGORY API ==========================
@app.route('/')
def hello_world():
    return 'Hello, Vyrak!'
@app.route('/category/list')
def show_category():
    categories = Category.query.all()
    if not categories:
        return {"message": "no category"}, 404
    # result = [{"id": c.id, "name": c.name} for c in categories]
    result = [{"id": c.id, "name": c.name} for c in categories]
    return {"Category": result}, 200

@app.post('/category/create')
def create_category():
    req = request.json
    name = req["name"]
    stringChecker(name)
    falsyChecker(name)
    sqlquery = text("INSERT INTO CATEGORY (name) VALUES (:name)")
    db.session.execute(sqlquery, {"name": name})
    db.session.commit()
    return {"message": "resource is created"}, 200

@app.put('/category/<int:id>/update')
def update_category(id):
    req = request.json
    name = req["name"]
    stringChecker(name)
    falsyChecker(name)
    sqlquery = text("UPDATE category SET name = :name WHERE id = :id")
    db.session.execute(sqlquery, {"name": name, "id": id})
    db.session.commit()
    return {"message": "resource is updated"}, 200

@app.delete('/category/<int:id>/delete')
def delete_category(id):
    sqlquery = text("DELETE FROM category WHERE id = :id")
    db.session.execute(sqlquery, {"id": id})
    db.session.commit()
    return {"message": "resource is delete"}, 200

# ========================= END CATEGORY API ======================
# ========================= BEGIN PRODUCT API ======================
@app.get('/product/list')
def get_product():
    product = Product.query.all()
    if not product:
        return {"message": "no product"}, 404
    list_product = [{"name": p.name, "image": p.image, "cost": p.cost, "price": p.price, "category_id": p.category_id, "stock": p.stock, "description": p.description} for p in product]
    return {"product": list_product}, 200
@app.post('/product/create')
def create_product():
    req = request.form
    file = request.files
    image = file.get('image')
    name = req['name']
    category_id = req['category_id']
    cost = req['cost']
    price = req['price']
    stock = req['stock']
    description = req.get('description')
    if image and image.filename != '':
        file_name = secure_filename(image.filename)
        image.save(f'./image/product/{file_name}')
    else:
        file_name = None
    # no null image, description
    sqlquery = text("INSERT INTO product (name, image, category_id, cost, price, stock, description) VALUES (:name, :image,:category_id, :cost, :price, :stock, :description)")
    db.session.execute(sqlquery, {"name": name, "image": file_name, "category_id": category_id, "cost": cost, "price": price, "stock": stock, "description": description})
    db.session.commit()
    return {"message": "resource is created"}, 200

@app.put('/product/<int:id>/update')
def update_product(id):
    product = Product.query.get(id)
    req = request.form
    file = request.files
    image = file.get('image')
    name = req.get('name') or product.name
    category_id = req.get('category_id') or product.category_id
    cost = req.get('cost') or int(product.cost)
    price = req.get('price') or int(product.price)
    stock = req.get('stock') or int(product.stock)
    description = req.get('description') or product.description
    if image and image.filename != '':
        file_name = secure_filename(image.filename)
        image.save(f'./image/product/{file_name}')
    else:
        file_name = None
    # no null image, description
    sqlquery = text("UPDATE product SET name = :name, image = :image, cost = :cost, price = :price, stock = :stock, description = :description, category_id = :category_id WHERE id = :id")
    db.session.execute(sqlquery, {"name": name, "image": file_name, "category_id": category_id, "cost": cost, "price": price, "stock": stock, "description": description, "id": id})
    db.session.commit()
    return {"message": "resource is created"}, 200

@app.delete('/product/<int:id>/delete')
def delete_product(id):
    sqlquery = text("DELETE FROM product WHERE id = :id")
    db.session.execute(sqlquery, {"id": id})
    db.session.commit()
    return {"message": "resource is delete"}, 200
# ========================= END PRODUCT API ======================

# ========================= BEGIN INVOICE API ======================
@app.route('/invoice/list')
def get_invoice():
    invoice = Invoice.query.all()
    if not invoice:
        return {"message": "no invoice"}, 404
    result = [{"id": i.id, "invoice_detail_id": getinvoicedetail(i.invoice_detail_id), "order": getorder(i.order_id)} for i in invoice]
    return {"invoice": result}, 200
@app.post('/invoice/create')
def create_invoice():
    req = request.json
    order_id = req['order_id']
    invoice_detail_id = req['invoice_detail_id']
    sqlquery = text("INSERT INTO invoice (order_id, invoice_detail_id) VALUES (:order_id, :invoice_detail_id)")
    db.session.execute(sqlquery, {"order_id": order_id, "invoice_detail_id": invoice_detail_id})
    db.session.commit()
    return {"message": "resource is created"}, 200

@app.put('/invoice/<int:id>/update')
def update_invoice(id):
    req = request.json
    order_id = req.get("order_id")
    invoice_detail_id = req.get("invoice_detail_id")
    sqlquery = text("UPDATE invoice SET order_id = :order_id, invoice_detail_id = :invoice_detail_id WHERE id = :id")
    db.session.execute(sqlquery, {"order_id": order_id, "invoice_detail_id": invoice_detail_id, "id": id})
    db.session.commit()
    return {"message": "resource is updated"}, 200

@app.delete('/invoice/<int:id>/delete')
def delete_invoice(id):
    sqlquery = text("DELETE FROM invoice WHERE id = :id")
    db.session.execute(sqlquery, {"id": id})
    db.session.commit()
    return {"message": "resource is delete"}, 200
# ========================= END INVOICE API ======================
# ========================= END INVOICEDETAIL API ======================
@app.route('/invoicedetail/list')
def get_invoicedetail():
    return {"invoice_detail": getallinvoicedetail()}, 200
@app.post('/invoicedetail/create')
def create_invoicedetail():
    req = request.json
    orderitem_id = req['orderitem_id']
    # invoice_detail_id = req['invoice_detail_id']
    sqlquery = text("INSERT INTO invoice_detail (orderitem_id) VALUES (:orderitem_id)")
    db.session.execute(sqlquery, {"orderitem_id": orderitem_id})
    db.session.commit()
    return {"message": "resource is created"}, 200

@app.put('/invoicedetail/<int:id>/update')
def update_invoicedetail(id):
    invoice_detail = InvoiceDetail.query.get(id)
    req = request.json
    orderitem_id = req.get("orderitem_id")
    # invoice_detail_id = req.get("invoice_detail_id")
    sqlquery = text("UPDATE invoice_detail SET orderitem_id = :orderitem_id WHERE id = :id")
    db.session.execute(sqlquery, {"orderitem_id": orderitem_id, "id": id})
    db.session.commit()
    return {"message": "resource is updated"}, 200

@app.delete('/invoicedetail/<int:id>/delete')
def delete_invoicedetail(id):
    sqlquery = text("DELETE FROM invoice_detail WHERE id = :id")
    db.session.execute(sqlquery, {"id": id})
    db.session.commit()
    return {"message": "resource is delete"}, 200
# ========================= END INVOICEDETAIL API ======================
# ========================= BEGIN SALE REPORT API ======================
# ====== Daily =========
@app.route('/reports/sales/daily', methods=['GET'])
def daily_sales_report():
    day = request.args.get('day', type=int)
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    result = Order.query.all()
    filtered_result = []
    for r in result:
        if r.date_time:

                parts = r.date_time.split('-')
                order_day = int(parts[0])
                order_month = int(parts[1])
                order_year = int(parts[2])

                # Check if matches the requested date
                match = True
                if day and order_day != day:
                    match = False
                if month and order_month != month:
                    match = False
                if year and order_year != year:
                    match = False

                if match:
                    filtered_result.append({
                        "id": r.id,
                        "user_id": r.user_id,
                        "customer_id": r.customer_id,
                        "date_time": r.date_time,
                        "status": r.status
                    })
    return jsonify({"daily_sales": filtered_result}), 200
# ====== Weekly ========
@app.route('/reports/sales/weekly', methods=['GET'])
def weekly_sales_report():
    week = request.args.get('week', type=int)
    year = request.args.get('year', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    result = Order.query.all()
    filtered_result = []

    for r in result:
        if r.date_time:
                parts = r.date_time.split('-')
                order_day = int(parts[0])
                order_month = int(parts[1])
                order_year = int(parts[2])
                order_date = datetime(order_year, order_month, order_day)

                match = False

                if week and year:
                    order_week = order_date.isocalendar()[1]
                    if order_week == week and order_year == year:
                        match = True

                elif start_date and end_date:
                    start_parts = start_date.split('-')
                    end_parts = end_date.split('-')

                    start_dt = datetime(int(start_parts[2]), int(start_parts[1]), int(start_parts[0]))
                    end_dt = datetime(int(end_parts[2]), int(end_parts[1]), int(end_parts[0]))

                    if start_dt <= order_date <= end_dt:
                        match = True

                elif not week and not year and not start_date and not end_date:
                    match = True

                if match:
                    filtered_result.append({
                        "id": r.id,
                        "user_id": r.user_id,
                        "customer_id": r.customer_id,
                        "date_time": r.date_time,
                        "status": r.status
                    })


    return jsonify({"weekly_sales": filtered_result}), 200
# ====== Monthly =======
@app.route('/reports/sales/monthly', methods=['GET'])
def monthly_sales_report():
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)

    result = Order.query.all()

    filtered_result = []
    for r in result:
        if r.date_time:
                parts = r.date_time.split('-')
                day = int(parts[0])
                order_month = int(parts[1])
                order_year = int(parts[2])
                match = True
                if month and order_month != month:
                    match = False
                if year and order_year != year:
                    match = False
                if match:
                    filtered_result.append({
                        "id": r.id,
                        "user_id": r.user_id,
                        "customer_id": r.customer_id,
                        "date_time": r.date_time,
                        "status": r.status
                    })
    return jsonify({"monthly_sales": filtered_result}), 200


# ============ SALES REPORT BY PRODUCT ============
@app.route('/reports/sales/by-product', methods=['GET'])
def sales_by_product():
    product_id = request.args.get('product_id', type=int)
    start_date = request.args.get('start_date')  # Format: 23-05-2004
    end_date = request.args.get('end_date')

    if not product_id:
        return jsonify({"error": "product_id is required"}), 400

    orders = Order.query.all()
    filtered_sales = []
    orderitem = OrderItem.query.all()
    for order in orders:
        if start_date and end_date and order.date_time:
                parts = order.date_time.split('-')
                order_date = datetime(int(parts[2]), int(parts[1]), int(parts[0]))

                start_parts = start_date.split('-')
                end_parts = end_date.split('-')
                start_dt = datetime(int(start_parts[2]), int(start_parts[1]), int(start_parts[0]))
                end_dt = datetime(int(end_parts[2]), int(end_parts[1]), int(end_parts[0]))

                if not (start_dt <= order_date <= end_dt):
                    continue

        for item in orderitem:
            if item.product_id == product_id:
                filtered_sales.append({
                    "order_id": order.id,
                    "user_id": order.user_id,
                    "customer_id": order.customer_id,
                    "date_time": order.date_time,
                    "status": order.status,
                    "product_id": item.product_id,
                    "quantity": item.qty,
                    "price": item.price
                })
                break

    return jsonify({
        "product_id": product_id,
        "total_orders": len(filtered_sales),
        "sales": filtered_sales
    }), 200


# ============ SALES REPORT BY CATEGORY ============
@app.route('/reports/sales/by-category', methods=['GET'])
def sales_by_category():
    category_id = request.args.get('category_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if not category_id:
        return jsonify({"error": "category_id is required"}), 400


    products = Product.query.filter_by(category_id=category_id).all()
    product_ids = [p.id for p in products]

    if not product_ids:
        return jsonify({
            "category_id": category_id,
            "total_orders": 0,
            "sales": []
        }), 200

    orders = Order.query.all()
    orderitems =OrderItem.query.all()
    filtered_sales = []

    for order in orders:

        if start_date and end_date and order.date_time:

                parts = order.date_time.split('-')
                order_date = datetime(int(parts[2]), int(parts[1]), int(parts[0]))

                start_parts = start_date.split('-')
                end_parts = end_date.split('-')
                start_dt = datetime(int(start_parts[2]), int(start_parts[1]), int(start_parts[0]))
                end_dt = datetime(int(end_parts[2]), int(end_parts[1]), int(end_parts[0]))

                if not (start_dt <= order_date <= end_dt):
                    continue

        order_items = []
        for item in orderitems:
            if item.product_id in product_ids:
                order_items.append({
                    "product_id": item.product_id,
                    "quantity": item.qty,
                    "price": item.price
                })

        if order_items:
            filtered_sales.append({
                "order_id": order.id,
                "user_id": order.user_id,
                "customer_id": order.customer_id,
                "date_time": order.date_time,
                "status": order.status,
                "items": order_items
            })

    return jsonify({
        "category_id": category_id,
        "total_orders": len(filtered_sales),
        "sales": filtered_sales
    }), 200


# ============ SALES REPORT BY USER ============
@app.route('/reports/sales/by-user', methods=['GET'])
def sales_by_user():
    user_id = request.args.get('user_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    query = Order.query.filter_by(user_id=user_id)
    orders = query.all()

    filtered_sales = []

    for order in orders:
        if start_date and end_date and order.date_time:
                parts = order.date_time.split('-')
                order_date = datetime(int(parts[2]), int(parts[1]), int(parts[0]))

                start_parts = start_date.split('-')
                end_parts = end_date.split('-')
                start_dt = datetime(int(start_parts[2]), int(start_parts[1]), int(start_parts[0]))
                end_dt = datetime(int(end_parts[2]), int(end_parts[1]), int(end_parts[0]))

                if not (start_dt <= order_date <= end_dt):
                    continue

        filtered_sales.append({
            "order_id": order.id,
            "customer_id": order.customer_id,
            "date_time": order.date_time,
            "status": order.status
        })

    return jsonify({
        "user_id": user_id,
        "total_orders": len(filtered_sales),
        "sales": filtered_sales
    }), 200


# ========================= END SALE REPORT API ======================
if __name__ == '__main__':
    app.run()
