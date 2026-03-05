import { showStatus } from './utils.js';
export async function generateDataset() {
    const modelEl = document.getElementById('modelSelect');
    const tempEl = document.getElementById('temperature');
    const scenariosEl = document.getElementById('numScenarios');
    const variantsEl = document.getElementById('numVariants');
    const sentimentsEl = document.getElementById('sentiments');
    const speechEl = document.getElementById('speechTypes');
    if (!modelEl || !tempEl || !scenariosEl || !variantsEl || !sentimentsEl || !speechEl)
        return;
    const model = modelEl.value;
    const temperature = tempEl.value;
    const numScenarios = scenariosEl.value;
    const numVariants = variantsEl.value;
    const sentiments = Array.from(sentimentsEl.selectedOptions).map(opt => opt.value);
    const speechTypes = Array.from(speechEl.selectedOptions).map(opt => opt.value);
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
        }
        else {
            showStatus('Generation failed', 'error');
        }
    }
    catch (error) {
        console.error(error);
        showStatus('An error occurred during generation.', 'error');
    }
}
