import { showStatus } from './utils.js';
export async function runEvaluation() {
    const fileInput = document.getElementById('testFile');
    const evalResults = document.getElementById('evalResults');
    const accValue = document.getElementById('accValue');
    const f1Value = document.getElementById('f1Value');
    if (!fileInput || !fileInput.files?.length) {
        alert("Please upload a test set CSV first.");
        return;
    }
    if (!evalResults || !accValue || !f1Value)
        return;
    showStatus('Running evaluation...', 'info');
    evalResults.style.display = 'none';
    const evalPlaceholder = document.getElementById('evalPlaceholder');
    if (evalPlaceholder)
        evalPlaceholder.style.display = 'none';
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
            evalResults.style.display = 'block';
            accValue.textContent = data.accuracy;
            f1Value.textContent = data.f1_score;
        }
        else {
            showStatus('Evaluation failed', 'error');
        }
    }
    catch (error) {
        console.error(error);
        showStatus('An error occurred during evaluation.', 'error');
    }
}
