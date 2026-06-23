document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const fileInput = document.getElementById('audioFile');
    const submitButton = document.getElementById('submitButton');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const errorMessage = document.getElementById('errorMessage');
    const resultContainer = document.getElementById('resultContainer');
    const transcriptionResult = document.getElementById('transcriptionResult');
    const downloadContainer = document.getElementById('downloadContainer');

    // Clear previous results and errors
    errorMessage.textContent = '';
    transcriptionResult.textContent = '';
    downloadContainer.innerHTML = '';
    resultContainer.style.display = 'none';

    if (!fileInput.files.length) {
        errorMessage.textContent = 'Please select a file.';
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    try {
        // Show loading state
        submitButton.disabled = true;
        loadingIndicator.style.display = 'block';

        const response = await fetch('/', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        // Display results
        resultContainer.style.display = 'block';
        transcriptionResult.textContent = data.transcript;

        // Add download button if filename is provided
        if (data.filename) {
            const downloadLink = document.createElement('a');
            downloadLink.href = `/download/${data.filename}`;
            downloadLink.textContent = 'Download Transcription';
            downloadLink.className = 'download-button';
            downloadContainer.appendChild(downloadLink);
        }
    } catch (error) {
        errorMessage.textContent = error.message || 'An error occurred during transcription.';
    } finally {
        // Reset loading state
        submitButton.disabled = false;
        loadingIndicator.style.display = 'none';
    }
});

// Update submit button state based on file selection
document.getElementById('audioFile').addEventListener('change', (e) => {
    const submitButton = document.getElementById('submitButton');
    submitButton.disabled = !e.target.files.length;
});

// --- Saved Transcripts Section ---

const transcriptList = document.getElementById('transcriptList');
const loadingTranscripts = document.getElementById('loadingTranscripts');
const noTranscripts = document.getElementById('noTranscripts');
const viewerContainer = document.getElementById('viewerContainer');
const viewerFilename = document.getElementById('viewerFilename');
const viewerContent = document.getElementById('viewerContent');
const viewerDownload = document.getElementById('viewerDownload');
const viewerClose = document.getElementById('viewerClose');

let allTranscripts = [];
let activeTranscriptItem = null;

async function loadTranscripts() {
    try {
        const res = await fetch('/api/transcripts');
        const data = await res.json();
        allTranscripts = data.transcripts;

        transcriptList.querySelectorAll('.loading-transcripts').forEach(el => el.remove());

        if (allTranscripts.length === 0) {
            noTranscripts.style.display = 'block';
            return;
        }

        noTranscripts.style.display = 'none';
        renderTranscriptList(allTranscripts);
    } catch (err) {
        loadingTranscripts.textContent = 'Failed to load transcriptions.';
    }
}

function renderTranscriptList(transcripts) {
    transcriptList.querySelectorAll('.transcript-item').forEach(el => el.remove());

    transcripts.forEach(t => {
        const item = document.createElement('div');
        item.className = 'transcript-item';
        item.dataset.filename = t.filename;

        const date = new Date(t.modified).toLocaleString();

        item.innerHTML = `
            <div class="transcript-filename">${escapeHtml(t.filename)}</div>
            <div class="transcript-meta">${date} — ${formatSize(t.size)}</div>
            <div class="transcript-preview">${escapeHtml(t.preview)}</div>
        `;

        item.addEventListener('click', () => loadTranscriptContent(t.filename, item));
        transcriptList.appendChild(item);
    });
}

async function loadTranscriptContent(filename, itemElement) {
    if (activeTranscriptItem) {
        activeTranscriptItem.classList.remove('active');
    }
    itemElement.classList.add('active');
    activeTranscriptItem = itemElement;

    try {
        const res = await fetch(`/api/transcripts/${encodeURIComponent(filename)}`);
        const data = await res.json();
        if (data.error) throw new Error(data.error);

        viewerFilename.textContent = data.filename;
        viewerContent.textContent = data.content;
        viewerDownload.href = `/download/${encodeURIComponent(data.filename)}`;
        viewerContainer.style.display = 'block';
        viewerContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    } catch (err) {
        viewerContent.textContent = 'Failed to load transcript content.';
        viewerContainer.style.display = 'block';
    }
}

viewerClose.addEventListener('click', () => {
    viewerContainer.style.display = 'none';
    if (activeTranscriptItem) {
        activeTranscriptItem.classList.remove('active');
        activeTranscriptItem = null;
    }
});

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function formatSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

loadTranscripts();
