from flask import Flask
from flask_wtf.csrf import CSRFProtect
import logging
import os
from .config import Config

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(Config)

    # Inicializa CSRF
    CSRFProtect(app)

    # Cria diretório de upload se não existir
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Registra rotas
    from .routes import init_routes
    init_routes(app)

    return app