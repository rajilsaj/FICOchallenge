import { showStatus } from './utils.js';

export async function handleFileUpload(event: Event): Promise<void> {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) {
        showStatus('No file selected.', 'error');
        return;
    }

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
        console.error(error);
        showStatus('An error occurred during upload.', 'error');
    }
}
