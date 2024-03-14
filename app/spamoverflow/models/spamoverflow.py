import datetime
from . import db
import shortuuid
from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID



class Email(db.Model):
    __tablename__ = 'emails'

    id = db.Column(String(22), primary_key=True, default=shortuuid.uuid)

    customer_id = db.Column(db.String)  #Might be a foreign key later on

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow) 
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow) 

    to_id = db.Column(db.String, nullable=False)
    from_id = db.Column(db.String, nullable=False)
    subject = db.Column(db.String, nullable=True)
    body = db.Column(db.String)
    state = db.Column(Enum("pending", "scanned", "failed")) #Status for the email

    domains = relationship("Domain", back_populates="email", cascade="all, delete")


    malicious = db.Column(db.Boolean, nullable=False, default=False)

class Domain(db.Model):
    __tablename__ = "domains"
    id = db.Column(String(22), primary_key=True, default=shortuuid.uuid)
    link = db.Column(db.String)

    # Establishing many-to-one relationship with Email
    email_id = db.Column(String(22), ForeignKey('emails.id', ondelete='CASCADE'))  
    email = relationship("Email", back_populates="domains")
