from flask import Flask
from config import Config
from models import db
from routes import api_bp

app = Flask(__name__)
app.config.from_object(Config)

# Инициализация базы данных
db.init_app(app)

# Регистрация Blueprint для API
app.register_blueprint(api_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True)
