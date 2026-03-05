import { showStatus } from './utils.js';

export async function applyFinetuning(): Promise<void> {
    const lrEl = document.getElementById('lr') as HTMLInputElement | null;
    if (!lrEl) return;
    const lr = lrEl.value;

    showStatus('Applying fine-tuning...', 'info');

    const paramChangeBorder = document.getElementById('paramChangeBorder');
    if (paramChangeBorder) {
        paramChangeBorder.classList.add('opacity-100');
        setTimeout(() => paramChangeBorder.classList.remove('opacity-100'), 2000);
    }

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
        console.error(error);
        showStatus('An error occurred during fine-tuning.', 'error');
    }
}
