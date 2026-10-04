/**
 * Cross Chicken (Crash) - 60fps Canvas Animation & Game Engine
 */
class CrossChickenGame {
    constructor() {
        this.canvas = document.getElementById('crashCanvas');
        if (!this.canvas) return;
        this.ctx = this.canvas.getContext('2d');
        this.multiplierEl = document.getElementById('multiplierText');
        this.statusEl = document.getElementById('gameStatusText');
        this.betBtn = document.getElementById('startCrashBtn');
        this.cashoutBtn = document.getElementById('cashoutCrashBtn');
        this.betAmountInput = document.getElementById('crashBetAmount');
        this.autoCashoutInput = document.getElementById('autoCashoutInput');
        
        this.roundId = null;
        this.betId = null;
        this.gameState = 'IDLE'; // IDLE, RUNNING, BUSTED, CASHED_OUT
        this.startTime = 0;
        this.currentMultiplier = 1.00;
        this.crashPoint = 0;
        this.durationSeconds = 0;
        this.hasBet = false;
        this.hasCashedOut = false;
        this.particles = [];
        this.laneOffset = 0;

        this.resize();
        window.addEventListener('resize', () => this.resize());
        this.bindEvents();
        this.initLoop();
    }

    resize() {
        if (!this.canvas) return;
        const rect = this.canvas.parentElement.getBoundingClientRect();
        this.canvas.width = rect.width;
        this.canvas.height = rect.height;
    }

    bindEvents() {
        if (this.betBtn) {
            this.betBtn.addEventListener('click', () => this.startRound());
        }
        if (this.cashoutBtn) {
            this.cashoutBtn.addEventListener('click', () => this.manualCashout());
        }
    }

    async startRound() {
        if (this.gameState === 'RUNNING') return;

        const amount = parseFloat(this.betAmountInput.value);
        if (isNaN(amount) || amount <= 0) {
            alert('Please enter a valid bet amount.');
            return;
        }

        this.betBtn.disabled = true;
        this.statusEl.innerText = "PREPARING ROAD...";

        try {
            // 1. Request new round from server
            const roundRes = await fetch('/games/crash/new-round/');
            const roundData = await roundRes.json();
            this.roundId = roundData.round_id;
            this.durationSeconds = roundData.duration_seconds;

            // 2. Place bet
            const formData = new FormData();
            formData.append('round_id', this.roundId);
            formData.append('bet_amount', amount);
            const autoVal = this.autoCashoutInput.value;
            if (autoVal) formData.append('auto_cashout', autoVal);

            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            const betRes = await fetch('/games/crash/bet/', {
                method: 'POST',
                headers: { 'X-CSRFToken': csrfToken },
                body: formData
            });
            const betData = await betRes.json();

            if (!betData.success) {
                alert(betData.error || 'Failed to place bet');
                this.betBtn.disabled = false;
                return;
            }

            this.betId = betData.bet_id;
            this.hasBet = true;
            this.hasCashedOut = false;
            
            // Update balance badge
            if (betData.balance !== undefined) {
                this.updateBalanceBadge(betData.balance);
            }

            // Start Animation
            this.gameState = 'RUNNING';
            this.startTime = performance.now();
            this.multiplierEl.classList.remove('crashed');
            this.statusEl.innerText = "CHICKEN DASHING ACROSS HIGHWAY!";
            this.cashoutBtn.style.display = 'inline-flex';
            this.betBtn.style.display = 'none';

        } catch (err) {
            console.error(err);
            alert('Network error starting round');
            this.betBtn.disabled = false;
        }
    }

    async manualCashout() {
        if (this.gameState !== 'RUNNING' || this.hasCashedOut || !this.hasBet) return;
        this.hasCashedOut = true;
        this.cashoutBtn.disabled = true;

        try {
            const formData = new FormData();
            formData.append('bet_id', this.betId);
            formData.append('multiplier', this.currentMultiplier.toFixed(2));
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            const res = await fetch('/games/crash/cashout/', {
                method: 'POST',
                headers: { 'X-CSRFToken': csrfToken },
                body: formData
            });
            const data = await res.json();

            if (data.success) {
                this.spawnCoins();
                if (window.soundEngine) window.soundEngine.cashout();
                this.statusEl.innerHTML = `<span style="color:#10B981">CASHED OUT @ ${data.multiplier}x (Won $${data.payout.toFixed(2)})!</span>`;
                this.updateBalanceBadge(data.balance);
            }
        } catch (e) {
            console.error(e);
        }
    }

    async bust(finalMultiplier) {
        this.gameState = 'BUSTED';
        this.multiplierEl.classList.add('crashed');
        this.statusEl.innerHTML = `<span style="color:#EF4444">CRASHED @ ${finalMultiplier.toFixed(2)}x!</span>`;
        this.spawnExplosion();
        if (window.soundEngine) window.soundEngine.crash();

        // Notify server round finish
        try {
            const formData = new FormData();
            formData.append('round_id', this.roundId);
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            await fetch('/games/crash/finish/', {
                method: 'POST',
                headers: { 'X-CSRFToken': csrfToken },
                body: formData
            });
        } catch (e) {}

        this.cashoutBtn.style.display = 'none';
        this.cashoutBtn.disabled = false;
        this.betBtn.style.display = 'inline-flex';
        this.betBtn.disabled = false;

        // Prepend to history bar
        this.addHistoryPill(finalMultiplier);
    }

    addHistoryPill(mult) {
        const bar = document.querySelector('.crash-history-bar');
        if (!bar) return;
        const pill = document.createElement('div');
        const m = mult.toFixed(2);
        pill.className = `history-pill ${mult >= 3 ? 'high' : mult >= 1.5 ? 'mid' : 'low'}`;
        pill.innerText = `${m}x`;
        bar.prepend(pill);
    }

    updateBalanceBadge(bal) {
        const el = document.querySelector('.wallet-balance');
        if (el) el.innerText = `$${bal.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
    }

    spawnCoins() {
        const cx = this.canvas.width / 2;
        const cy = this.canvas.height / 2;
        for (let i = 0; i < 40; i++) {
            this.particles.push({
                x: cx,
                y: cy,
                vx: (Math.random() - 0.5) * 12,
                vy: (Math.random() - 0.7) * 12,
                color: '#F59E0B',
                size: Math.random() * 6 + 4,
                life: 60
            });
        }
    }

    spawnExplosion() {
        const cx = this.canvas.width / 2;
        const cy = this.canvas.height / 2;
        for (let i = 0; i < 50; i++) {
            this.particles.push({
                x: cx,
                y: cy,
                vx: (Math.random() - 0.5) * 15,
                vy: (Math.random() - 0.5) * 15,
                color: ['#EF4444', '#F97316', '#FCD34D'][Math.floor(Math.random() * 3)],
                size: Math.random() * 8 + 3,
                life: 45
            });
        }
    }

    initLoop() {
        const loop = (now) => {
            this.update(now);
            this.render();
            requestAnimationFrame(loop);
        };
        requestAnimationFrame(loop);
    }

    update(now) {
        if (this.gameState === 'RUNNING') {
            const elapsed = (now - this.startTime) / 1000;
            // Formula matches CrashEngine: 1.00 + 0.055 * (t ** 1.72)
            this.currentMultiplier = 1.00 + 0.055 * Math.pow(elapsed, 1.72);
            this.multiplierEl.innerText = `${this.currentMultiplier.toFixed(2)}x`;
            this.laneOffset = (this.laneOffset + (4 + elapsed * 3)) % 60;

            // Check auto-cashout
            const autoLimit = parseFloat(this.autoCashoutInput.value);
            if (!this.hasCashedOut && autoLimit && this.currentMultiplier >= autoLimit) {
                this.manualCashout();
            }

            // Check server crash
            if (elapsed >= this.durationSeconds) {
                this.bust(this.currentMultiplier);
            }
        }

        // Particle physics
        for (let i = this.particles.length - 1; i >= 0; i--) {
            const p = this.particles[i];
            p.x += p.vx;
            p.y += p.vy;
            p.vy += 0.25; // gravity
            p.life--;
            if (p.life <= 0) {
                this.particles.splice(i, 1);
            }
        }
    }

    render() {
        const w = this.canvas.width;
        const h = this.canvas.height;
        const ctx = this.ctx;

        ctx.clearRect(0, 0, w, h);

        // 1. Draw Asphalt Highway
        ctx.fillStyle = '#080C14';
        ctx.fillRect(0, 0, w, h);

        // 2. Draw Moving Lane Dividers
        ctx.strokeStyle = 'rgba(6, 182, 212, 0.25)';
        ctx.lineWidth = 4;
        ctx.setLineDash([25, 25]);
        ctx.lineDashOffset = -this.laneOffset;

        const lanes = 4;
        for (let i = 1; i < lanes; i++) {
            const y = (h / lanes) * i;
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(w, y);
            ctx.stroke();
        }
        ctx.setLineDash([]); // Reset line dash

        // 3. Draw Road Borders
        ctx.strokeStyle = 'rgba(245, 158, 11, 0.5)';
        ctx.lineWidth = 3;
        ctx.strokeRect(0, 0, w, h);

        // 4. Draw Chicken / Avatar in Center
        const cx = w * 0.45;
        const cy = h * 0.5;
        const bounce = this.gameState === 'RUNNING' ? Math.sin(performance.now() * 0.015) * 6 : 0;

        ctx.save();
        ctx.translate(cx, cy + bounce);

        // Chicken Body
        ctx.fillStyle = '#FBBF24';
        ctx.beginPath();
        ctx.arc(0, 0, 22, 0, Math.PI * 2);
        ctx.fill();

        // Comb (Jengger)
        ctx.fillStyle = '#EF4444';
        ctx.beginPath();
        ctx.arc(-4, -24, 7, 0, Math.PI * 2);
        ctx.arc(4, -25, 8, 0, Math.PI * 2);
        ctx.arc(12, -22, 6, 0, Math.PI * 2);
        ctx.fill();

        // Eye
        ctx.fillStyle = '#000';
        ctx.beginPath();
        ctx.arc(10, -6, 3, 0, Math.PI * 2);
        ctx.fill();

        // Beak
        ctx.fillStyle = '#F97316';
        ctx.beginPath();
        ctx.moveTo(18, -4);
        ctx.lineTo(30, 0);
        ctx.lineTo(18, 6);
        ctx.closePath();
        ctx.fill();

        // Wing
        ctx.fillStyle = '#F59E0B';
        ctx.beginPath();
        ctx.ellipse(-6, 2, 12, 7, Math.PI / 6, 0, Math.PI * 2);
        ctx.fill();

        ctx.restore();

        // 5. Draw Particles (coins/explosions)
        this.particles.forEach(p => {
            ctx.fillStyle = p.color;
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            ctx.fill();
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.crossChickenGame = new CrossChickenGame();
});
