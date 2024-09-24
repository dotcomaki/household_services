from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    # For Professionals
    service_type = db.Column(db.String(100))
    experience = db.Column(db.Integer)

    # Relations
    service_requests = db.relationship('ServiceRequest', backref='customer', lazy=True)
    assigned_requests = db.relationship('ServiceRequest', backref='professional', lazy=True, foreign_keys='ServiceRequest.professional_id')
    
    def __repr__(self):
        return f'<User: {self.username}>'
    
# Service Model
class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    base_price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    time_required = db.Column(db.Integer)
        
    def __repr__(self):
        return f'<Service: {self.name}>'
    
# Service Request Model
class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    date_of_request = db.Column(db.DateTime, default=datetime.utcnow)
    date_of_completion = db.Column(db.DateTime)
    service_status = db.Column(db.String(20), default='requested')
    remarks = db.Column(db.Text)

    service = db.relationship('Service')

    def __repr__(self):
        return f'<ServiceRequest: {self.id}>'
    