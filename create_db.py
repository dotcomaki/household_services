# create_db.py

from app import app
from extensions import db
import models  # Ensure models are imported so SQLAlchemy knows about them

def create_database():
    with app.app_context():
        db.create_all()
        print("Database tables created.")

if __name__ == '__main__':
    create_database()