from flask import Flask
from flask_migrate import Migrate
from config import Config
from extensions import db, login_manager
from models import User, Service, ServiceRequest
import os
import routes

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.config['WTF_CSRF_ENABLED'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

if __name__ == '__main__':
    app.run(debug=False)