from . import db 
import datetime
from sqlalchemy import Enum

class Email(db.Model):
    __tablename__ = 'emails'

    email_id = db.Column(db.String, primary_key=True)
    customer_id = db.Column(db.String)  #Might be a foreign key

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow) 
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow) 

    to_id = db.Column(db.String, nullable=False)
    from_id = db.Column(db.String, nullable=False)
    subject = db.Column(db.String, nullable=True)
    body = db.Column(db.String)

    state = db.Column(Enum("pending", "scanned", "failed")) #Status for the email
    domains = db.Column(db.String)    #Links found in the email

    #spamhammer_metadata = db.Column(db.String, nullable=True)   #The content which is passed to the spamhammer binary
    malicious = db.Column(db.Boolean, nullable=False, default=False)

""" class Customer(db.Model):
    __tablename__ = "customers" #I believe this is actually clients like google etc? because they are "customers" of my service
    customer_id = db.Column(db.String, primary_key=True)
    #Some foreign keys to emails directly? """
