from app import db

class InvoiceDetail(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    orderitem_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable = False)
