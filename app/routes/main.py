import os
import logging
from flask import Blueprint, render_template, request, jsonify
from werkzeug.utils import secure_filename
from app.services import assemblyai, storage

logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)


def _allowed(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'wav', 'mp3', 'ogg', 'm4a', 'flac', 'mp4', 'mpeg', 'opus'}


@main_bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or file.filename == '':
            logger.warning('POST sem arquivo')
            return jsonify({'error': 'No file provided'}), 400

        if not _allowed(file.filename):
            logger.warning('Tipo de arquivo não permitido: %s', file.filename)
            return jsonify({'error': 'File type not allowed'}), 400

        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        file.save(filepath)
        logger.info('Arquivo recebido: %s (%d bytes)', filename, file.content_length or 0)

        upload_url = assemblyai.upload_file(filepath)
        if not upload_url:
            return jsonify({'error': 'Upload to AssemblyAI failed'}), 502

        transcript_id = assemblyai.start_transcription(upload_url)
        if not transcript_id:
            return jsonify({'error': 'Failed to start transcription'}), 502

        text = assemblyai.poll_transcription(transcript_id)
        if text is None:
            return jsonify({'error': 'Transcription failed or timed out'}), 502

        transcript_filename = storage.save_transcription(text, filename)
        return jsonify({
            'transcript': text,
            'filename': transcript_filename,
        })

    return render_template('index.html')


# resolve current_app no escopo do blueprint quando necessário
from flask import current_app
