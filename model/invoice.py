from app import db

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    invoice_detail = db.Column(db.String(255), nullable= False)