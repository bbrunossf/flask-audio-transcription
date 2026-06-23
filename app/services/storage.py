import os
import logging
from datetime import datetime
from flask import current_app

logger = logging.getLogger(__name__)


def save_transcription(text, original_filename):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    base = os.path.splitext(original_filename)[0]
    transcript_filename = f'{base}_transcript_{timestamp}.txt'

    folder = current_app.config['TRANSCRIPTS_FOLDER']
    os.makedirs(folder, exist_ok=True)

    filepath = os.path.join(folder, transcript_filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(text)

    logger.info(
        'Transcrição salva: %s (%d bytes)',
        transcript_filename, len(text.encode('utf-8')),
    )
    return transcript_filename


def list_transcripts():
    folder = current_app.config['TRANSCRIPTS_FOLDER']
    if not os.path.exists(folder):
        logger.debug('Pasta de transcrições não existe: %s', folder)
        return []

    files = []
    for f in sorted(os.listdir(folder), reverse=True):
        if f.endswith('.txt'):
            filepath = os.path.join(folder, f)
            stat = os.stat(filepath)
            with open(filepath, 'r', encoding='utf-8') as fh:
                preview = fh.read(200)
            files.append({
                'filename': f,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'preview': preview,
            })

    logger.debug('%d transcrições listadas', len(files))
    return files


def get_transcript_content(filename):
    filepath = os.path.join(current_app.config['TRANSCRIPTS_FOLDER'], filename)
    if not os.path.exists(filepath):
        logger.warning('Transcrição não encontrada: %s', filename)
        return None
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    logger.debug('Transcrição carregada: %s (%d bytes)', filename, len(content.encode('utf-8')))
    return content
