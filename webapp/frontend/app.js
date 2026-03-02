const API_BASE = '/api';

// --- State Management ---
let currentStep = 1;

// --- DOM Elements ---
const steps = [1, 2, 3, 4].map(s => document.getElementById(`section-${s}`));
const stepIndicators = [1, 2, 3, 4].map(s => document.querySelector(`.step-item[data-step="${s}"]`));

// --- Navigation Functions ---
function showStep(stepNum) {
    if (stepNum < 1 || stepNum > 4) return;
    
    // Update sections
    steps.forEach((sec, idx) => {
        if (!sec) return;
        if (idx + 1 === stepNum) {
            sec.classList.remove('hidden');
            sec.classList.add('block', 'animate-fade-in');
        } else {
            sec.classList.add('hidden');
            sec.classList.remove('block', 'animate-fade-in');
        }
    });

    // Update Indicators
    stepIndicators.forEach((ind, idx) => {
        if (!ind) return;
        const icon = ind.querySelector('.step-icon');
        
        ind.className = `flex items-start gap-4 step-item`;
        icon.className = `step-icon w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm transition-all`;

        if (idx + 1 < stepNum) {
            // Completed
            ind.classList.add('step-completed');
            icon.classList.add('bg-emerald-500', 'border-emerald-500', 'text-white', 'shadow-lg', 'shadow-emerald-500/30');
            icon.innerHTML = '<i class="fa-solid fa-check"></i>';
        } else if (idx + 1 === stepNum) {
            // Active
            ind.classList.add('step-active');
            icon.classList.add('bg-blue-600', 'border-transparent', 'text-white', 'shadow-lg', 'shadow-blue-500/30');
            icon.innerHTML = stepNum;
        } else {
            // Inactive
            ind.classList.add('step-inactive');
            icon.classList.add('bg-slate-800', 'border-slate-700', 'text-slate-400');
            icon.innerHTML = idx + 1;
        }
    });

    currentStep = stepNum;
}

function setBtnLoading(btn, isLoading, originalText, iconClass = '') {
    if (isLoading) {
        btn.disabled = true;
        btn.innerHTML = `<span class="loader"></span><span class="ml-2">Processing...</span>`;
    } else {
        btn.disabled = false;
        btn.innerHTML = `${iconClass ? `<i class="${iconClass}"></i>` : ''}<span class="${iconClass ? 'ml-2' : ''}">${originalText}</span>`;
    }
}

// --- Step 1: Generation ---
document.getElementById('gen-temp')?.addEventListener('input', (e) => {
    document.getElementById('temp-val').textContent = e.target.value;
});

document.getElementById('btn-generate')?.addEventListener('click', async (e) => {
    const btn = e.target.closest('button');
    const intent = document.getElementById('gen-intent').value;
    const temp = parseFloat(document.getElementById('gen-temp').value);
    const num = parseInt(document.getElementById('gen-count').value);

    setBtnLoading(btn, true, 'Generate Scenarios', 'fa-solid fa-wand-magic-sparkles');
    document.getElementById('gen-status').textContent = 'Generating...';
    document.getElementById('gen-status').className = 'text-xs bg-blue-900/50 text-blue-300 px-2 py-1 rounded border border-blue-700 animate-pulse';

    try {
        const res = await fetch(`${API_BASE}/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ intent, temperature: temp, num_scenarios: num })
        });
        const data = await res.json();
        
        // Render Results
        document.getElementById('gen-empty')?.classList.add('hidden');
        const resultsDiv = document.getElementById('gen-results');
        resultsDiv.classList.remove('hidden');
        resultsDiv.innerHTML = '';

        data.scenarios.forEach((s) => {
            const el = document.createElement('div');
            el.className = 'bg-slate-800/80 p-3 rounded-lg border border-slate-700 text-sm flex gap-3 animate-fade-in group hover:border-blue-500/50 transition-colors';
            el.innerHTML = `
                <div class="text-blue-400 font-mono mt-0.5 opacity-50 text-xs">[${s.id}]</div>
                <div class="flex-1 text-slate-200">
                    <p>${s.scenario}</p>
                    <div class="text-[10px] text-slate-500 mt-2 flex gap-2 uppercase font-medium">
                        <span class="bg-slate-900 px-1.5 py-0.5 rounded border border-slate-700">Conf: ${s.confidence_score}</span>
                        <span class="bg-slate-900 px-1.5 py-0.5 rounded border border-slate-700">${s.intent}</span>
                    </div>
                </div>
            `;
            resultsDiv.appendChild(el);
        });

        document.getElementById('gen-status').textContent = 'Completed';
        document.getElementById('gen-status').className = 'text-xs bg-emerald-900/50 text-emerald-300 px-2 py-1 rounded border border-emerald-700';
    } catch (err) {
        console.error(err);
        document.getElementById('gen-status').textContent = 'Error';
        document.getElementById('gen-status').className = 'text-xs bg-red-900/50 text-red-300 px-2 py-1 rounded border border-red-700';
    } finally {
        setBtnLoading(btn, false, 'Generate Scenarios', 'fa-solid fa-wand-magic-sparkles');
    }
});

// --- Step 2: Preparation ---
document.getElementById('prep-split')?.addEventListener('input', (e) => {
    document.getElementById('split-val').textContent = `${e.target.value}% / ${100 - e.target.value}%`;
});

document.getElementById('btn-prepare')?.addEventListener('click', async (e) => {
    const btn = e.target.closest('button');
    const split = parseInt(document.getElementById('prep-split').value);

    setBtnLoading(btn, true, 'Prepare Dataset', 'fa-solid fa-layer-group');

    try {
        const res = await fetch(`${API_BASE}/prepare`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ split_ratio: split })
        });
        const data = await res.json();
        
        document.getElementById('prep-empty')?.classList.add('hidden');
        document.getElementById('prep-stats')?.classList.remove('hidden');
        
        // Counter animation helper
        const animateValue = (id, end) => {
            const obj = document.getElementById(id);
            let current = 0;
            const inc = Math.ceil(end / 20);
            const timer = setInterval(() => {
                current += inc;
                if (current >= end) {
                    obj.innerHTML = end.toLocaleString();
                    clearInterval(timer);
                } else {
                    obj.innerHTML = current.toLocaleString();
                }
            }, 30);
        };

        animateValue('stat-train', data.train_samples);
        animateValue('stat-test', data.test_samples);

        // Build bars
        const barsDiv = document.getElementById('prep-bars');
        barsDiv.innerHTML = '';
        Object.entries(data.distributions).forEach(([intent, val], idx) => {
            const max = data.total_samples;
            const pct = Math.round((val / max) * 100);
            const colors = ['bg-blue-500', 'bg-purple-500', 'bg-emerald-500', 'bg-amber-500'];
            const color = colors[idx % colors.length];

            barsDiv.innerHTML += `
                <div>
                    <div class="flex justify-between text-xs text-slate-400 mb-1">
                        <span class="capitalize">${intent.replace('_', ' ')}</span>
                        <span>${val.toLocaleString()} (${pct}%)</span>
                    </div>
                    <div class="w-full bg-slate-800 rounded-full h-1.5 border border-white/5 overflow-hidden">
                        <div class="${color} h-1.5 rounded-full" style="width: ${pct}%"></div>
                    </div>
                </div>
            `;
        });

        // Enable Next
        document.getElementById('btn-next-3').disabled = false;
        document.getElementById('btn-next-3').classList.remove('opacity-50', 'cursor-not-allowed');

    } catch (err) {
        console.error(err);
    } finally {
        setBtnLoading(btn, false, 'Prepare Dataset', 'fa-solid fa-layer-group');
    }
});


// --- Step 3: Training ---
document.getElementById('train-epochs')?.addEventListener('input', (e) => {
    document.getElementById('train-epochs-val').textContent = e.target.value;
});

document.getElementById('btn-train')?.addEventListener('click', async (e) => {
    const btn = e.target.closest('button');
    const modelType = document.querySelector('input[name="model_type"]:checked').value;
    const epochs = parseInt(document.getElementById('train-epochs').value);

    setBtnLoading(btn, true, 'Training...', 'fa-solid fa-rocket');
    
    // Terminal simulation
    const termStat = document.getElementById('term-status');
    const termContent = document.getElementById('term-content');
    const overlay = document.getElementById('train-overlay');
    
    termStat.textContent = 'Running';
    termStat.className = 'text-blue-400 animate-pulse';
    termContent.innerHTML = '';
    overlay.classList.add('hidden');
    overlay.classList.remove('flex', 'opacity-100');
    overlay.style.opacity = '0';

    const addLine = (txt, color = 'text-slate-300') => {
        const div = document.createElement('div');
        const now = new Date();
        const timeStr = `[${now.toTimeString().split(' ')[0]}]`;
        div.innerHTML = `<span class="text-slate-600 mr-2">${timeStr}</span> <span class="${color}">${txt}</span>`;
        termContent.appendChild(div);
        termContent.scrollTop = termContent.scrollHeight;
    };

    addLine(`Initializing ${modelType.toUpperCase()} trainer interface...`);
    addLine(`Loading prepared dataset into VRAM...`);

    try {
        // We simulate intermediate logs via Timeout before awaiting fetch (since fetch is mocked bulk)
        let stepCount = 0;
        const logTimer = setInterval(() => {
            stepCount++;
            addLine(`Epoch ${Math.min(epochs, Math.ceil(stepCount/3))}: Batch loss ${Math.random().toFixed(4)}...`);
        }, 800);

        const res = await fetch(`${API_BASE}/train`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ model_type: modelType, epochs: epochs })
        });
        const data = await res.json();
        
        clearInterval(logTimer);
        
        addLine(`Training sequence finished successfully.`, 'text-green-400 font-bold');
        addLine(`Final cross-entropy loss: ${data.final_loss}`);
        addLine(`Validation accuracy: ${data.accuracy}`, 'text-blue-400');
        addLine(`Saving model checkpoints... completed.`, 'text-purple-400');

        termStat.textContent = 'Completed';
        termStat.className = 'text-green-500';

        // Show overlay stats
        setTimeout(() => {
            overlay.classList.remove('hidden');
            overlay.classList.add('flex');
            setTimeout(() => {
                overlay.style.opacity = '1';
                document.getElementById('final-acc').textContent = `${(data.accuracy * 100).toFixed(1)}%`;
            }, 50);
        }, 1000);

        // Enable next
        document.getElementById('btn-next-4').disabled = false;
        document.getElementById('btn-next-4').classList.remove('opacity-50', 'cursor-not-allowed');

    } catch (err) {
        console.error(err);
        addLine(`CRITICAL ERROR: Training failed.`, 'text-red-500');
        termStat.textContent = 'Error';
        termStat.className = 'text-red-500';
    } finally {
        setBtnLoading(btn, false, 'Start Training Run', 'fa-solid fa-rocket');
    }
});


// --- Step 4: Inference ---
document.getElementById('chat-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const inputEl = document.getElementById('chat-input');
    const text = inputEl.value.trim();
    if (!text) return;

    const hist = document.getElementById('chat-history');
    
    // Append User MSG
    hist.innerHTML += `
        <div class="flex gap-4 max-w-3xl ml-auto justify-end mb-6 animate-fade-in">
            <div>
                <div class="bg-blue-600 rounded-2xl rounded-tr-none px-5 py-3 text-white shadow-md inline-block">
                    ${text}
                </div>
            </div>
            <div class="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center shrink-0 shadow-lg border border-slate-600 text-xs">
                U
            </div>
        </div>
    `;
    inputEl.value = '';
    hist.scrollTop = hist.scrollHeight;
    
    // Add loading typing indicator
    const typingId = 'typing-' + Date.now();
    hist.innerHTML += `
        <div id="${typingId}" class="flex gap-4 max-w-3xl mb-6">
            <div class="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shrink-0 shadow-lg">
                <i class="fa-solid fa-robot text-white text-xs"></i>
            </div>
            <div>
                <div class="bg-slate-800 rounded-2xl rounded-tl-none px-5 py-3 text-slate-400 border border-slate-700 shadow-md inline-flex gap-1 items-center h-[48px]">
                    <div class="w-2 h-2 rounded-full bg-slate-500 animate-bounce" style="animation-delay: 0ms"></div>
                    <div class="w-2 h-2 rounded-full bg-slate-500 animate-bounce" style="animation-delay: 150ms"></div>
                    <div class="w-2 h-2 rounded-full bg-slate-500 animate-bounce" style="animation-delay: 300ms"></div>
                </div>
            </div>
        </div>
    `;
    hist.scrollTop = hist.scrollHeight;

    try {
        const res = await fetch(`${API_BASE}/predict`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });
        const data = await res.json();
        
        document.getElementById(typingId)?.remove();

        hist.innerHTML += `
            <div class="flex gap-4 max-w-3xl mb-6 animate-fade-in">
                <div class="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shrink-0 shadow-lg">
                    <i class="fa-solid fa-robot text-white text-xs"></i>
                </div>
                <div>
                    <div class="bg-slate-800 rounded-2xl rounded-tl-none px-5 py-3 text-slate-200 border border-slate-700 shadow-md inline-block">
                        <span class="block text-xs uppercase tracking-wider text-slate-400 mb-1">CLASSIFIED INTENT</span>
                        <div class="font-bold text-lg text-purple-400 mb-2">${data.predicted_intent}</div>
                        <div class="text-xs bg-black/30 rounded inline-block px-2 py-1 border border-white/5">
                            Confidence: <span class="text-emerald-400">${Math.round(data.confidence * 100)}%</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        hist.scrollTop = hist.scrollHeight;
    } catch (err) {
        console.error(err);
        document.getElementById(typingId)?.remove();
    }
});


// Navigation bindings
document.getElementById('btn-next-2')?.addEventListener('click', () => showStep(2));
document.getElementById('btn-prev-1')?.addEventListener('click', () => showStep(1));
document.getElementById('btn-next-3')?.addEventListener('click', () => showStep(3));
document.getElementById('btn-prev-2')?.addEventListener('click', () => showStep(2));
document.getElementById('btn-next-4')?.addEventListener('click', () => showStep(4));
document.getElementById('btn-prev-3')?.addEventListener('click', () => showStep(3));

// Init
showStep(1);
