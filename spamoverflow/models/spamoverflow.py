import datetime
from . import db
import shortuuid
from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ENUM

class Email(db.Model):
    __tablename__ = 'emails'

    id = db.Column(String, primary_key=True, default=shortuuid.uuid)

    priority = db.Column(db.Boolean, nullable=False, default=False)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow) 
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow) 

    to_id = db.Column(db.String, nullable=False)
    from_id = db.Column(db.String, nullable=False)
    subject = db.Column(db.String, nullable=True)
    body = db.Column(db.String)
    status = db.Column(ENUM("pending", "scanned", "failed", name="email_status"), default="pending") #Status for the email
    malicious = db.Column(db.Boolean, nullable=False, default=False)

    spamhammer_metadata = db.Column(db.String)

    #One to many relation with Domain
    domains = relationship("Domain", back_populates="email", cascade="all, delete-orphan")

    #Many to one relationship with Customer
    customer_id = db.Column(String, ForeignKey("customers.id", ondelete="CASCADE"))
    customer = relationship("Customer", back_populates="emails")


class Domain(db.Model):
    __tablename__ = "domains"
    id = db.Column(String, primary_key=True, default=shortuuid.uuid)
    link = db.Column(db.String) #Might be a foreing key to the count table later on

    # Establishing many-to-one relationship with Email
    email_id = db.Column(String, ForeignKey('emails.id', ondelete='CASCADE'))  
    email = relationship("Email", back_populates="domains")



#Table for Customers, which I believe is email clients
class Customer(db.Model):
    __tablename__ = "customers"
    id = db.Column(String, primary_key=True, default=shortuuid.uuid)

    #One to many relationship to Email
    emails = relationship("Email", back_populates="customer", cascade="all, delete-orphan")