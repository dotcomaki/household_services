from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# User Model
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_completed = db.Column(db.DateTime)

    # For Professionals Only
    is_approved = db.Column(db.Boolean, default=False)
    service_type = db.Column(db.String(100))
    experience = db.Column(db.Integer)
    resume_filename = db.Column(db.String(200))
    approval_status = db.Column(db.String(50), default='pending')

    # DB Relationships
    customer_service_requests = db.relationship('ServiceRequest', backref='customer', foreign_keys='ServiceRequest.customer_id', lazy='dynamic')
    professional_service_requests = db.relationship('ServiceRequest', backref='professional', foreign_keys='ServiceRequest.professional_id', lazy='dynamic')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def __repr__(self):
        return f'<User: {self.username}>'
    
# Service Model
class Service(db.Model):
    __tablename__ = 'services'

    id = db.Column(db.Integer, nullable =False, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    base_price = db.Column(db.Float, nullable=False)
    time_required = db.Column(db.Integer, nullable=False)  # in minutes
    description = db.Column(db.Text)
        
    def __repr__(self):
        return f'<Service: {self.name}>'
    
# Service Request Model
class ServiceRequest(db.Model):
    __tablename__ = 'service_requests'

    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    service_status = db.Column(db.String(20), nullable=False, default='requested')

    # DB Relationships
    service = db.relationship('Service', backref='service_requests')
    date_of_request = db.Column(db.DateTime, default=datetime.utcnow)
    date_of_completion = db.Column(db.DateTime)
    remarks = db.Column(db.Text)

    def __repr__(self):
        return f'<ServiceRequest: {self.id}>'
