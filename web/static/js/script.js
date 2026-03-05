// Helper to show status message using Tailwind classes
function showStatus(message, type = 'success') {
    const container = document.getElementById('statusContainer');
    if (!container) return;

    container.classList.remove('hidden');
    // Remove previous color classes
    container.className = 'mb-6 p-4 rounded-xl border flex items-center gap-3 animate-fade-in shadow-lg';

    // Icon SVGs
    const successIcon = `<svg class="w-6 h-6 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`;
    const infoIcon = `<svg class="w-6 h-6 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`;
    const errorIcon = `<svg class="w-6 h-6 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>`;

    let icon = successIcon;

    if (type === 'success') {
        container.classList.add('bg-emerald-500/10', 'border-emerald-500/30', 'text-emerald-400');
        icon = successIcon;
    } else if (type === 'info') {
        container.classList.add('bg-brand-500/10', 'border-brand-500/30', 'text-brand-400');
        icon = infoIcon;
    } else {
        container.classList.add('bg-red-500/10', 'border-red-500/30', 'text-red-400');
        icon = errorIcon;
    }

    container.innerHTML = `${icon} <span class="font-medium">${message}</span>`;

    // Auto hide after 5 seconds if success or error
    if (type !== 'info') {
        setTimeout(() => {
            container.classList.add('hidden');
        }, 5000);
    }
}

// Upload Dataset
async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    showStatus('Uploading dataset...', 'info');

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();

        if (response.ok) {
            showStatus('Dataset uploaded successfully!', 'success');
            setTimeout(() => window.location.reload(), 1500);
        } else {
            showStatus(`Upload failed: ${result.message}`, 'error');
        }
    } catch (error) {
        showStatus('An error occurred during upload.', 'error');
    }
}

// Generate Dataset
async function generateDataset() {
    const model = document.getElementById('modelSelect').value;
    const temperature = document.getElementById('temperature').value;
    const numScenarios = document.getElementById('numScenarios').value;
    const numVariants = document.getElementById('numVariants').value;

    const sentiments = Array.from(document.getElementById('sentiments').selectedOptions).map(opt => opt.value);
    const speechTypes = Array.from(document.getElementById('speechTypes').selectedOptions).map(opt => opt.value);

    showStatus('Generating synthetic dataset... please wait.', 'info');

    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                model,
                temperature,
                num_scenarios: numScenarios,
                num_variants: numVariants,
                sentiments,
                speechTypes
            })
        });

        if (response.ok) {
            showStatus('Generation complete!', 'success');
            setTimeout(() => window.location.reload(), 1500);
        } else {
            showStatus('Generation failed', 'error');
        }
    } catch (error) {
        showStatus('An error occurred during generation.', 'error');
    }
}

// Test Set Evaluation
async function runEvaluation() {
    const fileInput = document.getElementById('testFile');
    if (!fileInput.files.length) {
        alert("Please upload a test set CSV first.");
        return;
    }

    showStatus('Running evaluation...', 'info');
    document.getElementById('evalResults').style.display = 'none';

    try {
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        // Upload first before evaluating
        const uploadRes = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        if (!uploadRes.ok) {
            showStatus('Test set upload failed.', 'error');
            return;
        }

        const response = await fetch('/api/evaluate', {
            method: 'POST'
        });
        const data = await response.json();

        if (response.ok) {
            showStatus('Evaluation complete!', 'success');
            document.getElementById('evalResults').style.display = 'block';
            document.getElementById('accValue').textContent = data.accuracy;
            document.getElementById('f1Value').textContent = data.f1_score;
        } else {
            showStatus('Evaluation failed', 'error');
        }
    } catch (error) {
        showStatus('An error occurred during evaluation.', 'error');
    }
}

// Model Training
async function startTraining() {
    const epochs = parseInt(document.getElementById('epochs').value);

    showStatus('Starting training...', 'info');
    const progressSection = document.getElementById('progressSection');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');

    progressSection.style.display = 'block';
    progressBar.style.width = '0%';
    progressText.innerHTML = '<svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-emerald-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Initializing environment...';

    try {
        const response = await fetch('/api/train', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ epochs })
        });

        if (response.ok) {
            let currentEpoch = 0;
            const interval = setInterval(() => {
                currentEpoch++;
                const percentage = Math.round((currentEpoch / epochs) * 100);

                progressBar.style.width = `${percentage}%`;
                progressText.innerHTML = `<svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-emerald-500 inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Epoch ${currentEpoch}/${epochs} complete`;

                if (currentEpoch >= epochs) {
                    clearInterval(interval);
                    showStatus('Training successful!', 'success');
                    progressText.innerHTML = 'Training Finished ✅';
                }
            }, 700);

        } else {
            showStatus('Training failed to start', 'error');
            progressSection.style.display = 'none';
        }
    } catch (error) {
        showStatus('An error occurred during training.', 'error');
        progressSection.style.display = 'none';
    }
}

// Fine Tuning
async function applyFinetuning() {
    const lr = document.getElementById('lr').value;

    showStatus('Applying fine-tuning...', 'info');

    try {
        const response = await fetch('/api/finetune', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ lr })
        });

        if (response.ok) {
            showStatus('Fine-tuning applied successfully.', 'success');
        } else {
            showStatus('Fine-tuning failed', 'error');
        }
    } catch (error) {
        showStatus('An error occurred during fine-tuning.', 'error');
    }
}
