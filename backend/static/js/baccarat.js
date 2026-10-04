/**
 * Baccarat Web Client
 */
document.addEventListener('DOMContentLoaded', () => {
    let currentChip = 10;
    let selectedChoice = 'PLAYER';

    const chipBtns = document.querySelectorAll('.chip-btn');
    const betInput = document.getElementById('betAmountInput');
    const choiceInput = document.getElementById('betChoiceInput');
    const zoneBtns = document.querySelectorAll('.bet-zone-btn');

    chipBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            chipBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentChip = parseInt(btn.dataset.value);
            if (betInput) {
                betInput.value = currentChip;
            }
            if (window.soundEngine) window.soundEngine.chip();
        });
    });

    zoneBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            zoneBtns.forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');
            selectedChoice = btn.dataset.choice;
            if (choiceInput) {
                choiceInput.value = selectedChoice;
            }
            if (window.soundEngine) window.soundEngine.chip();
        });
    });

    // Handle HTMX response events
    document.body.addEventListener('htmx:beforeRequest', (evt) => {
        if (evt.detail.target.id === 'baccaratArena') {
            const dealBtn = document.getElementById('dealBtn');
            if (dealBtn) {
                dealBtn.disabled = true;
                dealBtn.innerHTML = '<span class="spinner"></span> Dealing...';
            }
            if (window.soundEngine) window.soundEngine.card();
        }
    });

    document.body.addEventListener('htmx:afterSwap', (evt) => {
        if (evt.detail.target.id === 'baccaratArena') {
            if (window.soundEngine) window.soundEngine.card();
            // Re-bind listeners for newly rendered table
            const newZoneBtns = document.querySelectorAll('.bet-zone-btn');
            newZoneBtns.forEach(btn => {
                btn.addEventListener('click', () => {
                    newZoneBtns.forEach(b => b.classList.remove('selected'));
                    btn.classList.add('selected');
                    const choice = btn.dataset.choice;
                    const cInput = document.getElementById('betChoiceInput');
                    if (cInput) cInput.value = choice;
                    if (window.soundEngine) window.soundEngine.chip();
                });
            });
        }
    });
});
