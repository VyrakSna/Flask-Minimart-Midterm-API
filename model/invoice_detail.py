from app import db

class InvoiceDetail(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable = False)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable = False)