document.addEventListener('DOMContentLoaded', () => {
    // Upload & Process Logic
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const urlBtn = document.getElementById('url-btn');
    const urlInput = document.getElementById('url-input');
    const progressSection = document.getElementById('progress-section');
    const progressBar = document.getElementById('progress-bar');
    const progressStatus = document.getElementById('progress-status');
    const progressDetail = document.getElementById('progress-detail');

    if (dropZone) {
        dropZone.addEventListener('click', () => fileInput.click());
        dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('border-primary'); });
        dropZone.addEventListener('dragleave', () => dropZone.classList.remove('border-primary'));
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('border-primary');
            if (e.dataTransfer.files.length) uploadFile(e.dataTransfer.files[0]);
        });

        fileInput.addEventListener('change', () => {
            if (fileInput.files.length) uploadFile(fileInput.files[0]);
        });

        urlBtn.addEventListener('click', () => {
            const url = urlInput.value.trim();
            if (url) processUrl(url);
        });
    }

    // Result Page Logic
    const resultContainer = document.getElementById('result-container');
    if (resultContainer) {
        const jobId = resultContainer.dataset.jobId;
        pollStatus(jobId);
    }

    function uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        startProcess('/upload', formData);
    }

    function processUrl(url) {
        startProcess('/process-url', JSON.stringify({ url: url }), true);
    }

    function startProcess(endpoint, body, isJson = false) {
        showProgress();
        const headers = isJson ? { 'Content-Type': 'application/json' } : {};
        
        fetch(endpoint, { method: 'POST', headers: headers, body: body })
            .then(r => r.json())
            .then(data => {
                if (data.error) throw new Error(data.error);
                pollStatus(data.job_id); // In Index page, polling redirects;
                // Wait, if we are on index, we should redirect to result page immediately?
                // Or poll here until "processing" starts then redirect?
                // Let's redirect to Result page immediately and poll there.
                window.location.href = `/result/${data.job_id}`;
            })
            .catch(err => showError(err.message));
    }

    function pollStatus(jobId) {
        const interval = setInterval(() => {
            fetch(`/status/${jobId}`)
                .then(r => r.json())
                .then(data => {
                    if (data.status === 'processing' || data.status === 'queued') {
                        // Update UI if on Result page?
                        // Actually, if we are on Result page, we show progress until complete.
                         updateProgressUI(data);
                    } else if (data.status === 'completed') {
                        clearInterval(interval);
                        // Fetch Result Data and Render
                        fetchResultData(data.result.transcript_id);
                    } else if (data.status === 'failed') {
                        clearInterval(interval);
                        showError(data.message);
                    }
                });
        }, 2000);
    }
    
    function updateProgressUI(data) {
        // If we are on result page, we might show a progress bar in the Loading State
        const loadingState = document.getElementById('loading-state');
        if(loadingState) {
            loadingState.innerHTML = `
                <div class="spinner-border text-primary" role="status"></div>
                <h5 class="mt-3">${data.message}</h5>
                <div class="progress w-50 mx-auto mt-2" style="height: 5px;">
                    <div class="progress-bar" style="width: ${data.progress}%"></div>
                </div>
            `;
        }
    }

    function fetchResultData(transcriptId) {
        // We need an endpoint to get the transcript result by ID or Job ID
        // Currently missing in app.py. I'll fetch via a new endpoint /api/result-data/<job_id>
        // For now, assuming we added it.
        const jobId = resultContainer.dataset.jobId;
        fetch(`/api/result/${jobId}`)
            .then(r => r.json())
            .then(data => renderDashboard(data));
    }

    function renderDashboard(data) {
        document.getElementById('loading-state').classList.add('d-none');
        document.getElementById('content-row').classList.remove('d-none');
        
        // Render Summary
        document.getElementById('summary-content').innerHTML = marked.parse(data.summary);
        
        // Render Sentiment
        const sent = data.sentiment; // {neg: 0.1, neu: 0.8, pos: 0.1, compound: ...}
        document.getElementById('sentiment-pos').innerText = `${Math.round(sent.pos * 100)}%`;
        document.getElementById('sentiment-neg').innerText = `${Math.round(sent.neg * 100)}%`;
        document.getElementById('sentiment-neu').innerText = `${Math.round(sent.neu * 100)}%`;

        // Render Transcript
        const container = document.getElementById('transcript-content');
        container.innerHTML = '';
        data.transcript.forEach(seg => {
            const div = document.createElement('div');
            div.className = 'transcript-item mb-3 p-2 rounded hover-bg-dark';
            div.innerHTML = `
                <div class="d-flex justify-content-between small text-muted mb-1">
                    <span class="fw-bold text-info">${seg.speaker || 'Unknown'}</span>
                    <span>${formatTime(seg.start)}</span>
                </div>
                <p class="mb-0 text-light">${seg.text}</p>
            `;
            container.appendChild(div);
        });
    }

        // Initialize Search
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
             searchInput.addEventListener('input', (e) => {
                 const term = e.target.value.toLowerCase();
                 document.querySelectorAll('.transcript-item').forEach(item => {
                     const text = item.querySelector('p').innerText.toLowerCase();
                     if (text.includes(term)) {
                         item.classList.remove('d-none');
                     } else {
                         item.classList.add('d-none');
                     }
                 });
             });
        }
        
        // Connect Export Buttons (Check existence first as they are dynamically rendered? No, they are static in HTML)
        const pdfBtn = document.getElementById('btn-download-pdf');
        if (pdfBtn) {
            pdfBtn.addEventListener('click', () => {
                window.open(`/download/pdf/${resultContainer.dataset.jobId}`, '_blank');
            });
        }
        const srtBtn = document.getElementById('btn-download-srt');
        if (srtBtn) {
            srtBtn.addEventListener('click', () => {
                window.open(`/download/srt/${resultContainer.dataset.jobId}`, '_blank');
            });
        }
    // End of Export logic - no brace needed here as this is global scope inside DOMContentLoaded

    function showProgress() {
        if(progressSection) progressSection.classList.remove('d-none');
    }

    function showError(msg) {
        alert(msg); // Simple for now
    }
    
    function formatTime(seconds) {
        return new Date(seconds * 1000).toISOString().substr(11, 8);
    }
});
