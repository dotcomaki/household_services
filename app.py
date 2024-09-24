# app.py

from flask import Flask
from config import Config
from extensions import db, login_manager

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions with the app
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

# Import models after initializing extensions
from models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Import routes after models
import routes

if __name__ == '__main__':
    app.run(debug=True)