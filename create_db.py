# RUN ONLY ONCE IN THE BEGINNING TO CREATE DATABASE TABLES
from app import app
from extensions import db
import models

def create_database():
    with app.app_context():
        db.create_all()
        print("Database tables created.")

if __name__ == '__main__':
    create_database()