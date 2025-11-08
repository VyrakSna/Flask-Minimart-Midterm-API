from app import db


class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable = False)
    invoice_detail_id = db.Column(db.Integer, db.ForeignKey('invoice_detail.id'), nullable = False)