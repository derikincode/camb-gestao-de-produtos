from PIL import Image
import io
import logging
from .config import Config

logger = logging.getLogger(__name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def validate_image_dimensions(file):
    try:
        img = Image.open(file)
        max_width, max_height = 2000, 2000
        if img.width > max_width or img.height > max_height:
            return False
        file.seek(0)
        return True
    except Exception as e:
        logger.error(f"Erro ao validar dimensões da imagem: {e}")
        return False

def compress_image(file):
    try:
        img = Image.open(file)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=75)
        output.seek(0)
        return output
    except Exception as e:
        logger.error(f"Erro ao comprimir imagem: {e}")
        return None