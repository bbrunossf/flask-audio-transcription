import logging
import sys
from logging.handlers import RotatingFileHandler
from flask import Flask

def setup_logging(app):
    """Configura logging com saída para stdout e arquivo app.log."""
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    # Handler 1: stdout (terminal)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    # Handler 2: arquivo com rotação (app.log, app.log.1, app.log.2, app.log.3)
    log_filepath = os.path.join(os.getcwd(), 'app.log')
    file_handler = RotatingFileHandler(
        log_filepath,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding='utf-8',
    )
    file_handler.setFormatter(formatter)

    # Configura o logger raiz
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(stream_handler)
    root_logger.addHandler(file_handler)

    if app.config.get('DEBUG'):
        root_logger.setLevel(logging.DEBUG)
    else:
        root_logger.setLevel(logging.INFO)

    # Silencia loggers verbosos de bibliotecas
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

    app.logger.info('App iniciado — DEBUG=%s | Log file: %s', app.config.get('DEBUG'), log_filepath)

def create_app(config_object=None):
    app = Flask(__name__, template_folder='templates')

    if config_object:
        app.config.from_object(config_object)
    else:
        from app.config import Config
        app.config.from_object(Config)

    # Logging precisa ser configurado antes de tudo
    setup_logging(app)

    # Blueprints
    from app.routes.main import main_bp
    from app.routes.transcripts import transcripts_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(transcripts_bp)

    return app
