import os
from dotenv import load_dotenv

# Carrega .env da raiz do projeto automaticamente
load_dotenv()


class Config:
    # Diretórios
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    TRANSCRIPTS_FOLDER = os.path.join(os.getcwd(), 'transcripts')
    ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'm4a', 'flac', 'mp4', 'mpeg', 'opus'}

    # AssemblyAI — obrigatório, quebra cedo se ausente
    ASSEMBLYAI_API_KEY = os.environ.get('ASSEMBLYAI_API_KEY')
    if not ASSEMBLYAI_API_KEY:
        raise RuntimeError(
            'ASSEMBLYAI_API_KEY não definida. '
            'Copie .env.example para .env e preencha a chave.'
        )

    LANGUAGE_CODE = os.environ.get('LANGUAGE_CODE', 'pt')

    # Proxy
    HTTP_PROXY = os.environ.get('HTTP_PROXY')

    # Flask
    DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    HOST = os.environ.get('FLASK_HOST', '127.0.0.1')
