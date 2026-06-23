import time
import logging
import requests
from flask import current_app

logger = logging.getLogger(__name__)

BASE_URL = 'https://api.assemblyai.com/v2'


def _api_key():
    return current_app.config['ASSEMBLYAI_API_KEY']


def upload_file(filepath):
    headers = {'authorization': _api_key()}
    logger.debug('Enviando arquivo para AssemblyAI: %s', filepath)

    try:
        with open(filepath, 'rb') as f:
            resp = requests.post(
                f'{BASE_URL}/upload',
                headers=headers,
                data=f,
                timeout=60,
            )

        if resp.status_code == 200:
            upload_url = resp.json()['upload_url']
            logger.info('Upload concluído: %s', upload_url)
            return upload_url

        logger.error('Falha no upload — HTTP %d: %s', resp.status_code, resp.text)
        return None

    except requests.RequestException as e:
        logger.exception('Erro de rede no upload: %s', e)
        return None


def start_transcription(audio_url):
    headers = {
        'authorization': _api_key(),
        'content-type': 'application/json',
    }
    payload = {
        'audio_url': audio_url,
        'language_code': current_app.config['LANGUAGE_CODE'],
        'punctuate': 'true',
        'format_text': 'true',
    }

    logger.debug('Iniciando transcrição: %s', audio_url)

    try:
        resp = requests.post(
            f'{BASE_URL}/transcript',
            json=payload,
            headers=headers,
            timeout=30,
        )

        if resp.status_code == 200:
            transcript_id = resp.json()['id']
            logger.info('Transcrição iniciada — ID: %s', transcript_id)
            return transcript_id

        logger.error('Falha ao iniciar transcrição — HTTP %d: %s', resp.status_code, resp.text)
        return None

    except requests.RequestException as e:
        logger.exception('Erro de rede ao iniciar transcrição: %s', e)
        return None


def poll_transcription(transcript_id):
    headers = {'authorization': _api_key()}
    endpoint = f'{BASE_URL}/transcript/{transcript_id}'

    logger.info('Polling iniciado para transcrição: %s', transcript_id)
    attempts = 0

    while True:
        attempts += 1
        try:
            resp = requests.get(endpoint, headers=headers, timeout=30)

            if resp.status_code != 200:
                logger.error('Erro no polling — HTTP %d (tentativa %d)', resp.status_code, attempts)
                time.sleep(3)
                continue

            result = resp.json()
            status = result.get('status')

            if status == 'completed':
                text = result['text']
                logger.info(
                    'Transcrição concluída — ID: %s (%d tentativas, %d caracteres)',
                    transcript_id, attempts, len(text),
                )
                return text

            if status == 'error':
                logger.error(
                    'Transcrição falhou — ID: %s, erro: %s',
                    transcript_id, result.get('error', 'desconhecido'),
                )
                return None

            # status == 'processing' ou 'queued'
            logger.debug('Transcrição %s — status: %s (tentativa %d)', transcript_id, status, attempts)

        except requests.RequestException as e:
            logger.exception('Erro de rede no polling (tentativa %d): %s', attempts, e)

        time.sleep(3)
