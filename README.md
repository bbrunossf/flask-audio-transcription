# Audio Transcription App

Aplicação web Flask para transcrição de arquivos de áudio usando a API
[AssemblyAI](https://www.assemblyai.com/). Suporta upload de arquivos,
listagem de transcrições anteriores e visualização rich text.

## Funcionalidades

- Upload de áudio nos formatos WAV, MP3, OGG, M4A, FLAC, MP4, MPEG, Opus
- Transcrição automática via AssemblyAI com suporte a português
- Salvamento automático das transcrições em arquivos `.txt`
- Painel "Saved Transcriptions" com lista scrollável e preview
- Visualizador rich text com tipografia serifada e texto justificado
- Download de qualquer transcrição salva
- Logging estruturado (stdout + `app.log` com rotação)

## Estrutura do projeto
```
.
├── app/
│   ├── __init__.py            # Factory: create_app() + setup_logging()
│   ├── config.py              # Configurações via .env (python-dotenv)
│   ├── routes/
│   │   ├── main.py            # Blueprint: GET/POST /
│   │   └── transcripts.py     # Blueprint: /api/transcripts, /download
│   ├── services/
│   │   ├── assemblyai.py      # Upload, start e polling da API AssemblyAI
│   │   └── storage.py         # Salvar, listar e ler transcrições em disco
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css      # Estilos da interface
│   │   └── js/
│   │       └── script.js      # Lógica do frontend (upload + listagem)
│   └── templates/
│       └── index.html         # Template Jinja2
├── transcripts/               # Transcrições salvas (.txt)
├── uploads/                   # Arquivos de áudio enviados
├── .env.example               # Template de variáveis de ambiente
├── .gitignore
├── requirements.txt
├── run.py                     # Entrypoint
└── README.md
```

## Pré-requisitos

- Python 3.8+
- Conta e chave de API [AssemblyAI](https://www.assemblyai.com/app/)
- (Opcional) Proxy HTTP corporativo configurado

## Instalação

```bash
# 1. Clone o repositório
git clone <repo-url>
cd "flask audio transcription"

# 2. Crie um ambiente virtual (recomendado)
python -m venv venv

# 3. Ative o ambiente

# 4. Instale as dependências
pip install -r requirements.txt

# 5. Configure as variáveis de ambiente
cp .env.example .env
# Edite .env e insira sua chave ASSEMBLYAI_API_KEY

# Obrigatório
ASSEMBLYAI_API_KEY=sua_chave_aqui

# Opcionais
LANGUAGE_CODE=pt
FLASK_DEBUG=true
FLASK_HOST=0.0.0.0

# Proxy corporativo (se necessário)
# HTTP_PROXY=http://usuario:senha@host:porta

`python run.py`
```

# API interna

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/` | Interface principal |
| `POST` | `/` | Envia áudio para transcrição (`multipart/form-data`, campo `file`) |
| `GET` | `/api/transcripts` | Lista todas as transcrições salvas (JSON com nome, data, tamanho, preview) |
| `GET` | `/api/transcripts/<filename>` | Retorna o conteúdo completo de uma transcrição |
| `GET` | `/download/<filename>` | Download de uma transcrição como arquivo `.txt` |

 
# Tecnologias

| Camada | Tecnologia |
|---|---|
| Backend | Flask (Python) |
| Templates | Jinja2 |
| Frontend | HTML5, CSS3, JavaScript (vanilla) |
| Transcrição | AssemblyAI API v2 |
| Configuração | python-dotenv (.env) |
| Logging | RotatingFileHandler + StreamHandler |
