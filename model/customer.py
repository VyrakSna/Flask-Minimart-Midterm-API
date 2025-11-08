from app import db

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150))
    email = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    remark = db.Column(db.String(255))

