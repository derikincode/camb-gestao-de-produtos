import sys
import os
import logging
from datetime import datetime

from colorlog import ColoredFormatter  # Importa o formatter colorido

# Adiciona o diretório raiz do projeto ao sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.database import init_db

# Configura logging colorido
formatter = ColoredFormatter(
    "%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
    datefmt='%H:%M:%S',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
)

handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)
logger.propagate = False  # Impede log duplicado no console

app = create_app()

if __name__ == '__main__':
    init_db()
    
    logger.info("=======================================")
    logger.info("Iniciando o Sistema de Gestão de Produtos")
    logger.info(f"Data e Hora de Início: {datetime.now().strftime('%H:%M:%S - %d/%m/%Y')}")
    logger.info("=======================================")

    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    port = int(os.environ.get('PORT', 5000))

    logger.info("Modo de Depuração: %s", "Ativado" if debug_mode else "Desativado")
    logger.info("Servidor rodando em http://0.0.0.0:%d", port)
    logger.info("Acessível em todas as interfaces (0.0.0.0)")

    logger.warning("ATENÇÃO: Este é um servidor de desenvolvimento. Não use em produção!")
    logger.warning("Para produção, utilize um servidor WSGI como Gunicorn ou uWSGI.")

    app.run(host='0.0.0.0', port=port, debug=debug_mode)
