# seed.py

from app import app
from extensions import db
from models import User, Service, ServiceRequest
from werkzeug.security import generate_password_hash

def seed_data():
    with app.app_context():
        # Create an admin user
        admin_user = User(
            username='admin',
            password=generate_password_hash('admin'),
            role='admin'
        )
        db.session.add(admin_user)

        # Create sample customers and professionals
        customer1 = User(
            username='customer1',
            password=generate_password_hash('password123'),
            role='customer'
        )
        professional1 = User(
            username='professional1',
            password=generate_password_hash('password123'),
            role='professional',
            service_type='Plumbing',
            experience=5
        )
        db.session.add_all([customer1, professional1])

        # Add sample services
        service1 = Service(
            name='Plumbing',
            base_price=100.0,
            time_required=60,
            description='Fixing leaks and plumbing issues.'
        )
        service2 = Service(
            name='Electrical Repair',
            base_price=150.0,
            time_required=90,
            description='Repairing electrical systems.'
        )
        db.session.add_all([service1, service2])

        # Commit the changes
        db.session.commit()
        print("Database seeded with initial data.")

if __name__ == '__main__':
    seed_data()