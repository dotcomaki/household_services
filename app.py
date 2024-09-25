from flask import Flask
from flask_migrate import Migrate
from config import Config
from extensions import db, login_manager

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)
login_manager.init_app(app)
login_manager.login_view = 'login'

from models import User, Service, ServiceRequest

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

import routes

if __name__ == '__main__':
    app.run(debug=True)