# app.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object('config.Config')

# Initialize extensions
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Import models after initializing extensions
from models import User

# Define user loader in app.py
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Import routes after everything else
import routes

if __name__ == '__main__':
    app.run(debug=True)