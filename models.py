from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime

# User Model
class User(UserMixin, db.Model):
    id = db.column(db.Integer, primary_key=True)
    username = db.column(db.String(100), unique=True, nullable=False)
    password = db.column(db.String(100), nullable=False)
    role = db.column(db.String(20), nullable=False)
    is_active = db.column(db.Boolean, default=True)
    date_created = db.column(db.DateTime, default=datetime.utcnow)

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
    id = db.column(db.Integer, primary_key=True)
    name = db.column(db.String(100), nullable=False)
    base_price = db.column(db.Float, nullable=False)
    description = db.column(db.Text)
    time_required = db.column(db.Integer)
        
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

# Load User
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))