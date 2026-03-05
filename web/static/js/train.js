import { showStatus } from './utils.js';
export async function startTraining() {
    const epochsEl = document.getElementById('epochs');
    const progressSection = document.getElementById('progressSection');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const progressPercentage = document.getElementById('progressPercentage');
    if (!epochsEl || !progressSection || !progressBar || !progressText)
        return;
    const epochs = parseInt(epochsEl.value, 10);
    showStatus('Starting training...', 'info');
    const trainPlaceholder = document.getElementById('trainPlaceholder');
    if (trainPlaceholder)
        trainPlaceholder.style.display = 'none';
    progressSection.style.display = 'block';
    progressBar.style.width = '0%';
    if (progressPercentage)
        progressPercentage.innerText = '0%';
    progressText.innerHTML = '<svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-emerald-500 inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Initializing environment...';
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
                if (progressPercentage)
                    progressPercentage.innerText = `${percentage}%`;
                progressText.innerHTML = `<svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-emerald-500 inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Epoch ${currentEpoch}/${epochs} complete`;
                if (currentEpoch >= epochs) {
                    clearInterval(interval);
                    showStatus('Training successful!', 'success');
                    progressText.innerHTML = 'Training Finished ✅';
                }
            }, 700);
        }
        else {
            showStatus('Training failed to start', 'error');
            progressSection.style.display = 'none';
        }
    }
    catch (error) {
        console.error(error);
        showStatus('An error occurred during training.', 'error');
        progressSection.style.display = 'none';
    }
}
