import os

class Config:
    UPLOAD_FOLDER = './app/static/uploads'
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB por imagem
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'sua_chave_secreta_aqui')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    DATABASE = 'database.db'