import os
import logging
from flask import Blueprint, jsonify, send_file, current_app
from werkzeug.utils import secure_filename
from app.services import storage

logger = logging.getLogger(__name__)

transcripts_bp = Blueprint('transcripts', __name__)


@transcripts_bp.route('/api/transcripts', methods=['GET'])
def list_all():
    logger.debug('Listando todas as transcrições')
    return jsonify({'transcripts': storage.list_transcripts()})


@transcripts_bp.route('/api/transcripts/<filename>', methods=['GET'])
def get_one(filename):
    safe = secure_filename(filename)
    logger.debug('Buscando transcrição: %s', safe)
    content = storage.get_transcript_content(safe)
    if content is None:
        return jsonify({'error': 'Not found'}), 404
    return jsonify({'filename': safe, 'content': content})


@transcripts_bp.route('/download/<filename>')
def download(filename):
    folder = current_app.config['TRANSCRIPTS_FOLDER']
    logger.debug('Download solicitado: %s', filename)
    try:
        return send_file(
            os.path.join(folder, filename),
            as_attachment=True,
            download_name=filename,
        )
    except Exception as e:
        logger.exception('Erro ao baixar %s', filename)
        return jsonify({'error': 'File not found'}), 404
