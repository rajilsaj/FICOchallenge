// Helper to show status message
function showStatus(message, type = 'success') {
    const container = document.getElementById('statusContainer');
    if (!container) return;

    container.style.display = 'block';
    container.textContent = message;

    if (type === 'success') {
        container.style.backgroundColor = '#f0fdf4';
        container.style.borderColor = '#bbf7d0';
        container.style.color = '#166534';
    } else if (type === 'info') {
        container.style.backgroundColor = '#eff6ff';
        container.style.borderColor = '#bfdbfe';
        container.style.color = '#1e3a8a';
    } else {
        container.style.backgroundColor = '#fef2f2';
        container.style.borderColor = '#fecaca';
        container.style.color = '#991b1b';
    }

    // Auto hide after 5 seconds if success or error
    if (type !== 'info') {
        setTimeout(() => {
            container.style.display = 'none';
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
            showStatus('Dataset uploaded successfully! ✅');
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
            showStatus('Generation complete ✅');
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
        const response = await fetch('/api/evaluate', {
            method: 'POST'
        });
        const data = await response.json();

        if (response.ok) {
            showStatus('Evaluation complete ✅');
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
    progressBar.textContent = '0%';

    try {
        // We notify server to start, but here we just simulate the progress bar for UX
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
                progressBar.textContent = `${percentage}%`;
                progressText.textContent = `Epoch ${currentEpoch}/${epochs} complete`;

                if (currentEpoch >= epochs) {
                    clearInterval(interval);
                    showStatus('Training successful! ✅');
                    progressText.textContent = 'Training Finished ✅';
                }
            }, 700); // simulate 0.7s per epoch like in streamlit

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
            showStatus('Fine-tuning applied. ✅');
        } else {
            showStatus('Fine-tuning failed', 'error');
        }
    } catch (error) {
        showStatus('An error occurred during fine-tuning.', 'error');
    }
}
