// Helper to show status message using Tailwind classes
export function showStatus(message: string, type: 'success' | 'info' | 'error' = 'success'): void {
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
