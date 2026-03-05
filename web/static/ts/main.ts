import { handleFileUpload } from './upload.js';
import { generateDataset } from './generate.js';
import { runEvaluation } from './evaluate.js';
import { startTraining } from './train.js';
import { applyFinetuning } from './finetune.js';

// Setup page interactions
const uploadZone = document.getElementById('uploadZone');
const csvFile = document.getElementById('csvFile') as HTMLInputElement | null;
if (uploadZone && csvFile) {
    uploadZone.addEventListener('click', (e) => {
        if (e.target !== csvFile) {
            csvFile.click();
        }
    });
    csvFile.addEventListener('change', handleFileUpload);
}

const generateBtn = document.getElementById('generateBtn');
if (generateBtn) {
    generateBtn.addEventListener('click', generateDataset);
}

// Evaluation page
const runEvalBtn = document.getElementById('runEvalBtn');
if (runEvalBtn) {
    runEvalBtn.addEventListener('click', runEvaluation);
}

// Training page
const startTrainingBtn = document.getElementById('startTrainingBtn');
if (startTrainingBtn) {
    startTrainingBtn.addEventListener('click', startTraining);
}

// Finetuning page
const applyFinetuneBtn = document.getElementById('applyFinetuneBtn');
if (applyFinetuneBtn) {
    applyFinetuneBtn.addEventListener('click', applyFinetuning);
}
