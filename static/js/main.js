/**
 * main.js  –  SolarAI Ban Pong | Global Utilities
 */

// ── Toast notifications ───────────────────────────────────────────────────
const Toast = {
    container: null,
    init() {
        this.container = document.getElementById('toast-container');
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.id = 'toast-container';
            this.container.className = 'toast-wrap';
            document.body.appendChild(this.container);
        }
    },
    show(msg, type = 'info', duration = 3500) {
        this.init();
        const el = document.createElement('div');
        el.className = `toast-msg ${type}`;
        el.textContent = msg;
        this.container.appendChild(el);
        // Trigger entrance animation
        requestAnimationFrame(() => { el.style.opacity = '1'; el.style.transform = 'translateX(0)'; });
        setTimeout(() => {
            el.style.opacity = '0';
            el.style.transform = 'translateX(100%)';
            el.style.transition = 'opacity 0.3s, transform 0.3s';
            setTimeout(() => el.remove(), 300);
        }, duration);
    },
    success: (m) => Toast.show(m, 'success'),
    error:   (m) => Toast.show(m, 'error'),
};

// ── Number formatters ─────────────────────────────────────────────────────
const fmt = {
    num:  (v, d = 1) => Number(v).toLocaleString('th-TH', { minimumFractionDigits: d, maximumFractionDigits: d }),
    int:  (v)        => Number(v).toLocaleString('th-TH', { maximumFractionDigits: 0 }),
    thb:  (v)        => `฿${Number(v).toLocaleString('th-TH', { maximumFractionDigits: 0 })}`,
    pct:  (v)        => `${Number(v).toFixed(1)}%`,
    kwh:  (v, d = 1) => `${fmt.num(v, d)} kWh`,
    year: (v)        => `${Number(v).toFixed(1)} ปี`,
};

// ── Stars renderer ────────────────────────────────────────────────────────
function renderStars(n, max = 5) {
    return '★'.repeat(n) + '<span class="star-empty">' + '★'.repeat(max - n) + '</span>';
}

// ── API helpers ───────────────────────────────────────────────────────────
async function apiFetch(url, opts = {}) {
    const res = await fetch(url, {
        headers: { 'Content-Type': 'application/json' },
        ...opts,
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
}

// ── Dashboard stats loader ────────────────────────────────────────────────
async function loadDashboardStats() {
    try {
        const [stats, model] = await Promise.all([
            apiFetch('/api/stats'),
            apiFetch('/api/model-info'),
        ]);
        populateStats(stats);
        populateModelInfo(model);
        renderFeatureChart(model);
    } catch (e) {
        console.error('Stats load error:', e);
    }
}

function populateStats(s) {
    setText('stat-count',    s.count        || 0);
    setText('stat-daily',    fmt.num(s.avg_daily  || 0));
    setText('stat-annual',   fmt.int(s.avg_annual || 0));
    setText('stat-save',     fmt.int(s.avg_save   || 0));
    setText('stat-roi',      fmt.pct(s.avg_roi    || 0));
    setText('stat-breakeven',s.avg_breakeven ? `${fmt.num(s.avg_breakeven)} ปี` : '–');
}

function populateModelInfo(m) {
    setText('model-type',  m.type || '–');
    setText('model-r2',    fmt.num(m.r2   || 0, 4));
    setText('model-rmse',  `${fmt.num(m.rmse || 0, 2)} kWh`);
    setText('model-mae',   `${fmt.num(m.mae  || 0, 2)} kWh`);
    setText('model-file',  m.model_file || '–');

    // Animate R² progress bar
    const bar = document.getElementById('r2-bar');
    if (bar) {
        const pct = Math.round((m.r2 || 0) * 100);
        setTimeout(() => { bar.style.width = pct + '%'; }, 200);
    }
}

function renderFeatureChart(model) {
    const ctx = document.getElementById('feature-chart');
    if (!ctx || !model.features) return;

    const pairs = model.features.map((f, i) => ({ f, v: model.importances[i] || 0 }))
                                .sort((a, b) => b.v - a.v)
                                .slice(0, 12); // show top 12 features

    const colors = pairs.map((_, i) => {
        if (i === 0) return '#10b981';
        if (i === 1) return '#3b82f6';
        if (i === 2) return '#f59e0b';
        return 'rgba(148,163,184,0.7)';
    });

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: pairs.map(p => p.f),
            datasets: [{
                label: 'Feature Importance',
                data:  pairs.map(p => p.v),
                backgroundColor: colors,
                borderRadius: 6,
                borderSkipped: false,
            }],
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { grid: { color: 'rgba(255,255,255,0.06)' }, ticks: { font: { family: 'Prompt', size: 10 }, color: '#94a3b8' } },
                y: { grid: { display: false }, ticks: { font: { family: 'Prompt', size: 11 }, color: '#cbd5e1' } },
            },
        },
    });
}

// ── History table loader (dashboard) ─────────────────────────────────────
async function loadRecentHistory() {
    try {
        const data = await apiFetch('/api/history');
        const tbody = document.getElementById('recent-tbody');
        const mobileContainer = document.getElementById('recent-mobile-cards');
        if (!tbody && !mobileContainer) return;

        if (!data.length) {
            const emptyMsg = `
                <div style="text-align:center;color:var(--text-muted);padding:24px;">
                    <i class="bi bi-inbox" style="font-size:24px;display:block;margin-bottom:8px;opacity:.4;"></i>
                    ยังไม่มีข้อมูลการวิเคราะห์ – <a href="/map" style="color:var(--secondary);">เริ่มวิเคราะห์พื้นที่</a>
                </div>`;
            if (tbody) tbody.innerHTML = `<tr><td colspan="6">${emptyMsg}</td></tr>`;
            if (mobileContainer) mobileContainer.innerHTML = emptyMsg;
            return;
        }

        const recent = data.slice(0, 5);

        // 1. Desktop Table
        if (tbody) {
            tbody.innerHTML = recent.map(r => `
                <tr>
                    <td><a href="/analysis/${r.id}" style="color:var(--secondary);font-weight:600;">${r.address || '–'}</a></td>
                    <td><span class="stars-display" style="font-size:13px;">${renderStars(r.suitability || 0)}</span></td>
                    <td>${fmt.num(r.current_daily || 0)} kWh</td>
                    <td>${fmt.int(r.annual_kwh || 0)} kWh</td>
                    <td style="color:var(--primary-dark);font-weight:700;">${fmt.thb(r.annual_save || 0)}</td>
                    <td><span class="badge badge-green">${fmt.pct(r.roi || 0)}</span></td>
                </tr>`).join('');
        }

        // 2. Mobile Cards
        if (mobileContainer) {
            mobileContainer.innerHTML = recent.map(r => `
                <div class="audit-mobile-card" style="margin-bottom:8px;">
                    <div class="d-flex justify-content-between align-items-center mb-1">
                        <a href="/analysis/${r.id}" style="font-weight:700;font-size:14px;color:var(--secondary);flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
                            ${r.address || 'บ้านโป่ง, ราชบุรี'}
                        </a>
                        <span class="stars-display" style="font-size:12px;margin-left:8px;">${renderStars(r.suitability || 0)}</span>
                    </div>
                    <div style="display:grid;grid-template-columns:repeat(3, 1fr);gap:6px;background:rgba(0,0,0,0.25);padding:8px;border-radius:8px;text-align:center;">
                        <div>
                            <div style="font-size:9.5px;color:var(--text-muted);">ผลิต / วัน</div>
                            <div style="font-size:13px;font-weight:700;color:#f8fafc;">${fmt.num(r.current_daily || 0)} <small>kWh</small></div>
                        </div>
                        <div>
                            <div style="font-size:9.5px;color:var(--text-muted);">ประหยัด / ปี</div>
                            <div style="font-size:13px;font-weight:800;color:#34d399;">${fmt.thb(r.annual_save || 0)}</div>
                        </div>
                        <div>
                            <div style="font-size:9.5px;color:var(--text-muted);">ROI</div>
                            <div style="font-size:13px;font-weight:700;color:#38bdf8;">${fmt.pct(r.roi || 0)}</div>
                        </div>
                    </div>
                    <div style="text-align:right;margin-top:2px;">
                        <a href="/analysis/${r.id}" class="btn btn-ghost btn-sm" style="font-size:11.5px;padding:3px 10px;color:var(--secondary);border-color:rgba(56,189,248,0.3);">
                            ดูรายละเอียด <i class="bi bi-arrow-right"></i>
                        </a>
                    </div>
                </div>`).join('');
        }
    } catch (e) {
        console.error('Recent history error:', e);
    }
}

// ── Utility ───────────────────────────────────────────────────────────────
function setText(id, val) {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
}

function setHtml(id, val) {
    const el = document.getElementById(id);
    if (el) el.innerHTML = val;
}

// Run on page load
window.addEventListener('DOMContentLoaded', () => {
    const page = document.body.dataset.page;
    if (page === 'dashboard') {
        loadDashboardStats();
        loadRecentHistory();
    }
});
