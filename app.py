from os import abort
from tokenize import String
import re

from click import Abort
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, false
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
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

@app.errorhandler(500)
def error_500(error):
    return f'missing key: {error}', 500

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
        return {"message": "no user"}, 404
    # result = [{"id": c.id, "name": c.name} for c in categories]
    result = [{"id": c.id, "name": c.name} for c in categories]
    return {"Category": result}, 200

@app.errorhandler(400)
def error_400(error):
    return 'Bad request', 400

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
    if image and image.filename is not '':
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
    if image and image.filename is not '':
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



if __name__ == '__main__':
    app.run()
