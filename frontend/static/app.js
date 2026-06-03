/**
 * Evolutionary Studio Frontend — System 3 SPA
 */

const API_BASE = '';

// ============================================
// State
// ============================================

const state = {
    currentTab: 'produce',
    productions: [],
    currentProductionId: null,
    vaultNotes: [],
    activeVaultNote: null,
    pollingInterval: null
};

// ============================================
// DOM Utils
// ============================================

function $(sel) { return document.querySelector(sel); }
function $$(sel) { return document.querySelectorAll(sel); }

function renderDirectorDecision(decision) {
    const verdictColors = {
        'accept': '#22c55e',
        'reject': '#ef4444',
        'iterate': '#f59e0b',
        'escalate': '#a78bfa'
    };
    const color = verdictColors[decision.verdict] || '#6b7280';
    
    return `
        <div style="margin-top:16px;padding:12px 16px;border-radius:8px;background:rgba(0,0,0,0.3);border-left:4px solid ${color};">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                <div style="display:flex;align-items:center;gap:8px;">
                    <span style="font-size:18px;">${decision.verdict === 'accept' ? '✅' : decision.verdict === 'reject' ? '❌' : decision.verdict === 'iterate' ? '🔁' : '⚠️'}</span>
                    <strong style="color:${color};text-transform:uppercase;font-size:13px;letter-spacing:0.5px;">Director: ${decision.verdict}</strong>
                </div>
                <span style="font-size:12px;color:var(--text-muted);">Confidence: ${Math.round(decision.confidence * 100)}%</span>
            </div>
            <p style="font-size:13px;color:var(--text-secondary);margin:0 0 8px 0;">${decision.reason}</p>
            ${decision.specific_notes?.length ? `
                <div style="font-size:12px;color:var(--text-muted);">
                    <strong>Notes:</strong>
                    <ul style="margin:4px 0 0 16px;padding:0;">
                        ${decision.specific_notes.slice(0, 3).map(n => `<li>${n}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
        </div>
    `;
}

function renderEmotionalBadge(emotional) {
    const score = emotional.score || 0;
    const color = score >= 7 ? '#22c55e' : score >= 4 ? '#f59e0b' : '#ef4444';
    return `
        <div style="margin-top:12px;padding:10px 14px;border-radius:8px;background:rgba(0,0,0,0.2);border-left:3px solid ${color};display:inline-block;margin-right:12px;">
            <span style="font-size:12px;color:var(--text-muted);">Emotional Arc:</span>
            <strong style="color:${color};margin-left:6px;">${emotional.arc || 'Unknown'}</strong>
            <span style="font-size:12px;color:var(--text-muted);margin-left:8px;">${score}/10</span>
        </div>
    `;
}

function renderConcernsBadge(concerns) {
    const count = concerns.concerns_count || 0;
    const critical = concerns.critical_count || 0;
    const color = critical > 0 ? '#ef4444' : '#f59e0b';
    const icon = critical > 0 ? '🔴' : '🟠';
    return `
        <div style="margin-top:12px;padding:10px 14px;border-radius:8px;background:rgba(0,0,0,0.2);border-left:3px solid ${color};display:inline-block;">
            <span style="font-size:12px;color:var(--text-muted);">Concerns:</span>
            <strong style="color:${color};margin-left:6px;">${icon} ${count}</strong>
        </div>
    `;
}

function renderScoreBars(scores, combinedScore) {
    if (!scores) {
        // Fallback: show combined score only
        return `<div class="score-bars">
            <div class="score-bar-item">
                <div class="score-bar-label">Combined</div>
                <div class="score-bar-track"><div class="score-bar-fill structure" style="width:${(combinedScore / 10) * 100}%"></div></div>
                <div class="score-value">${combinedScore.toFixed(1)}</div>
            </div>
        </div>`;
    }
    
    const categories = [
        { key: 'structure', label: 'Structure', color: 'structure' },
        { key: 'character', label: 'Character', color: 'character' },
        { key: 'emotion', label: 'Emotion', color: 'emotion' },
        { key: 'pacing', label: 'Pacing', color: 'pacing' },
        { key: 'theme', label: 'Theme', color: 'theme' },
        { key: 'dialogue', label: 'Dialogue', color: 'dialogue' },
    ];
    
    let html = '<div class="score-bars">';
    let hasAnyScore = false;
    
    for (const cat of categories) {
        const scoreData = scores[cat.key];
        if (scoreData && typeof scoreData.score === 'number') {
            hasAnyScore = true;
            const score = scoreData.score;
            const width = (score / 10) * 100;
            const issues = scoreData.issues || [];
            const strengths = scoreData.strengths || [];
            const topIssue = issues.length > 0 ? issues[0] : null;
            const topStrength = strengths.length > 0 ? strengths[0] : null;
            
            html += `
                <div class="score-bar-item">
                    <div class="score-bar-label">${cat.label}</div>
                    <div class="score-bar-track"><div class="score-bar-fill ${cat.color}" style="width:${width}%"></div></div>
                    <div class="score-value">${score.toFixed(1)}</div>
                    ${topIssue ? `<div class="score-hint score-hint-issue" title="${issues.join('\\n')}">⚠ ${topIssue.substring(0, 40)}${topIssue.length > 40 ? '...' : ''}</div>` : ''}
                    ${!topIssue && topStrength ? `<div class="score-hint score-hint-good" title="${strengths.join('\\n')}">✓ ${topStrength.substring(0, 40)}${topStrength.length > 40 ? '...' : ''}</div>` : ''}
                </div>
            `;
        }
    }
    
    // If no individual scores found, show combined
    if (!hasAnyScore) {
        html += `
            <div class="score-bar-item">
                <div class="score-bar-label">Combined</div>
                <div class="score-bar-track"><div class="score-bar-fill structure" style="width:${(combinedScore / 10) * 100}%"></div></div>
                <div class="score-value">${combinedScore.toFixed(1)}</div>
            </div>
        `;
    }
    
    html += '</div>';
    return html;
}

function showTab(tabId) {
    state.currentTab = tabId;
    
    // Update nav tabs
    $$('.nav-tab').forEach(t => {
        t.classList.remove('active');
        if (t.dataset.tab === tabId) t.classList.add('active');
    });
    
    // Update content panels
    $$('.tab-panel').forEach(p => {
        p.classList.remove('active');
        if (p.id === `tab-${tabId}`) p.classList.add('active');
    });
    
    if (tabId === 'vault') loadVault();
    if (tabId === 'dashboard') refreshDashboard();
    if (tabId === 'evolution') loadEvolution();
    if (tabId === 'package') loadPackage();
    if (tabId === 'memory') loadMemoryStats();
}

function showToast(message, type = 'info') {
    const container = $('#toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type} fade-in`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}

// ============================================
// API
// ============================================

async function apiGet(path) {
    const res = await fetch(`${API_BASE}${path}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
}

async function apiPost(path, body) {
    const res = await fetch(`${API_BASE}${path}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
}

// ============================================
// Health Check
// ============================================

async function checkHealth() {
    try {
        const data = await apiGet('/api/health');
        $('#server-status').classList.add('connected');
        $('#server-status-text').textContent = 'Connected';
    } catch (e) {
        $('#server-status').classList.remove('connected');
        $('#server-status-text').textContent = 'Disconnected';
    }
}

// ============================================
// Produce Form
// ============================================

function initProduceForm() {
    const form = $('#produce-form');
    const btn = $('#produce-btn');
    
    // Update preview when inputs change
    const inputs = ['n-concepts', 'n-rounds', 'budget'];
    inputs.forEach(id => {
        $(`#${id}`)?.addEventListener('input', updatePreview);
    });
    updatePreview();
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        btn.disabled = true;
        btn.innerHTML = '<span class="btn-icon">◌</span> Evolving...';
        
        const req = {
            dna_source: $('#dna-source').value,
            setting: $('#setting').value,
            group_a: $('#group-a').value,
            group_b: $('#group-b').value,
            theme: $('#theme').value,
            metaphor: $('#metaphor').value || undefined,
            genre: $('#genre').value,
            n_concepts: parseInt($('#n-concepts').value),
            n_rounds: parseInt($('#n-rounds').value),
            budget: parseFloat($('#budget').value),
        };
        
        try {
            const res = await apiPost('/api/produce', req);
            state.currentProductionId = res.production_id;
            state.productions.push(res.production_id);
            updateProductionSelectors();
            showToast(`Production ${res.production_id} started!`, 'success');
            showTab('dashboard');
            startPolling();
        } catch (err) {
            showToast(`Failed: ${err.message}`, 'error');
        } finally {
            btn.disabled = false;
            btn.innerHTML = '<span class="btn-icon">▶</span> Start Evolution';
        }
    });
}

function updatePreview() {
    const nConcepts = $('#n-concepts')?.value || 4;
    const descs = $$('.flow-desc');
    if (descs[0]) descs[0].textContent = `${nConcepts} competing concepts from DNA`;
}

// ============================================
// Dashboard
// ============================================

function updateProductionSelectors() {
    const opts = state.productions.map(id => `<option value="${id}">${id}</option>`).join('');
    ['#production-select', '#evolution-production-select', '#package-production-select'].forEach(sel => {
        const el = $(sel);
        if (el) el.innerHTML = '<option value="">Select a production...</option>' + opts;
    });
}

function startPolling() {
    if (state.pollingInterval) clearInterval(state.pollingInterval);
    state.pollingInterval = setInterval(() => {
        // Refresh production list periodically
        refreshProductionList();
        if (state.currentProductionId) {
            refreshDashboard();
            if (state.currentTab === 'evolution') loadEvolution();
            if (state.currentTab === 'package') loadPackage();
        }
    }, 2000);
}

async function refreshProductionList() {
    try {
        // Fetch all post-mortems to discover production IDs
        const pkgs = await apiGet('/api/vault?folder=memory/post_mortems');
        const prodIds = new Set(state.productions);
        
        pkgs.forEach(p => {
            // Match package_{id}.md or post_mortem_{id}.md
            const match = p.path.match(/(?:package|post_mortem)_(.+?)\.md/);
            if (match) prodIds.add(match[1]);
        });
        
        const allIds = Array.from(prodIds);
        const newIds = allIds.filter(id => !state.productions.includes(id));
        if (newIds.length > 0 || state.productions.length !== allIds.length) {
            state.productions = allIds;
            updateProductionSelectors();
            // Auto-select first production if none selected
            if (!state.currentProductionId && state.productions.length > 0) {
                state.currentProductionId = state.productions[0];
                const ps = $('#production-select');
                const eps = $('#evolution-production-select');
                const pps = $('#package-production-select');
                if (ps) ps.value = state.currentProductionId;
                if (eps) eps.value = state.currentProductionId;
                if (pps) pps.value = state.currentProductionId;
                refreshDashboard();
            }
        }
    } catch (e) {
        // Silently fail
        console.log('refreshProductionList error:', e);
    }
}

async function refreshDashboard() {
    if (!state.currentProductionId) return;
    
    try {
        const status = await apiGet(`/api/status/${state.currentProductionId}`);
        renderDashboard(status);
    } catch (e) {
        console.error('Dashboard refresh failed:', e);
    }
}

function renderDashboard(status) {
    const container = $('#dashboard-content');
    const phase = status.phase || 'unknown';
    const evo = status.evolution_stats || {};
    const swarm = status.swarm_stats || {};
    
    let phaseDisplay = phase;
    let progress = 0;
    if (phase === 'queued') progress = 5;
    else if (phase === 'evolution') progress = 25;
    else if (phase === 'production') progress = 60;
    else if (phase === 'compile') progress = 85;
    else if (phase === 'done') progress = 100;
    
    const badgeClass = phase === 'done' ? 'badge-complete' : phase === 'failed' ? 'badge-failed' : 'badge-running';
    
    container.innerHTML = `
        <div class="stats-grid fade-in">
            <div class="stat-card">
                <div class="stat-value">${evo.total_concepts_generated || 0}</div>
                <div class="stat-label">Concepts Generated</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${evo.total_evaluations || 0}</div>
                <div class="stat-label">Critic Evaluations</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${swarm.total || 0}</div>
                <div class="stat-label">Production Tasks</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${swarm.completed || 0}</div>
                <div class="stat-label">Tasks Completed</div>
            </div>
        </div>
        
        <div class="card fade-in">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
                <h3>Production: ${status.production_id}</h3>
                <span class="badge ${badgeClass}">${phaseDisplay}</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width:${progress}%"></div>
            </div>
            <div style="display:flex;justify-content:space-between;margin-top:8px;font-size:12px;color:var(--text-muted);">
                <span>Budget: $${status.budget_remaining?.toFixed(2) || '50.00'} remaining</span>
                <span>${progress}% complete</span>
            </div>
        </div>
        
        ${swarm.total ? `
        <div class="card fade-in">
            <h3>Swarm Progress</h3>
            <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:12px;text-align:center;margin-top:12px;">
                <div><div style="font-size:24px;font-weight:700;font-family:var(--font-mono);color:var(--text-primary)">${swarm.total}</div><div style="font-size:11px;color:var(--text-muted)">Total</div></div>
                <div><div style="font-size:24px;font-weight:700;font-family:var(--font-mono);color:var(--warning)">${swarm.pending}</div><div style="font-size:11px;color:var(--text-muted)">Pending</div></div>
                <div><div style="font-size:24px;font-weight:700;font-family:var(--font-mono);color:var(--info)">${swarm.in_progress}</div><div style="font-size:11px;color:var(--text-muted)">In Progress</div></div>
                <div><div style="font-size:24px;font-weight:700;font-family:var(--font-mono);color:var(--success)">${swarm.completed}</div><div style="font-size:11px;color:var(--text-muted)">Completed</div></div>
                <div><div style="font-size:24px;font-weight:700;font-family:var(--font-mono);color:var(--danger)">${swarm.failed}</div><div style="font-size:11px;color:var(--text-muted)">Failed</div></div>
            </div>
        </div>
        ` : ''}
        
        ${phase === 'done' ? `
        <div class="card fade-in" style="text-align:center;padding:40px;">
            <div style="font-size:48px;margin-bottom:16px;">🎬</div>
            <h3>Production Complete!</h3>
            <p style="color:var(--text-secondary);margin:12px 0 20px;">View the full package in the Package tab, or browse the vault.</p>
            <button class="btn-primary" onclick="showTab('package')">View Package</button>
            <button class="btn-secondary" style="margin-left:8px;" onclick="showTab('evolution')">View Evolution</button>
        </div>
        ` : ''}
    `;
}

$('#refresh-dashboard')?.addEventListener('click', refreshDashboard);
$('#production-select')?.addEventListener('change', (e) => {
    state.currentProductionId = e.target.value;
    refreshDashboard();
});

// ============================================
// Evolution
// ============================================

async function loadEvolution() {
    try {
        const concepts = await apiGet('/api/concepts');
        renderEvolution(concepts);
    } catch (e) {
        console.error('Load evolution failed:', e);
    }
}

function renderEvolution(concepts) {
    const container = $('#evolution-content');
    if (!concepts.length) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🧬</div>
                <p>No concepts yet. Start a production first.</p>
            </div>`;
        return;
    }
    
    container.innerHTML = `
        <div class="concept-list fade-in">
            ${concepts.map(c => `
                <div class="concept-card ${c.status === 'winner' ? 'winner' : ''}" data-id="${c.id}">
                    <div class="concept-header">
                        <div>
                            <div class="concept-title">${c.title}</div>
                            <div class="concept-meta">
                                <span>${c.genre}</span>
                                <span>•</span>
                                <span>${c.setting}</span>
                                ${c.status === 'winner' ? '<span class="badge badge-winner">Winner</span>' : ''}
                            </div>
                        </div>
                    </div>
                    <div class="concept-logline">${c.logline}</div>
                    ${c.combined_score ? renderScoreBars(c.scores, c.combined_score) : ''}
                </div>
            `).join('')}
        </div>
    `;
    
    $$('.concept-card').forEach(card => {
        card.addEventListener('click', () => loadConceptDetail(card.dataset.id));
    });
}

async function loadConceptDetail(conceptId) {
    try {
        const concept = await apiGet(`/api/concepts/${conceptId}`);
        showModal(concept.title, concept.content);
    } catch (e) {
        showToast('Failed to load concept', 'error');
    }
}

$('#evolution-production-select')?.addEventListener('change', (e) => {
    state.currentProductionId = e.target.value;
    loadEvolution();
});

// ============================================
// Package
// ============================================

async function loadPackage() {
    if (!state.currentProductionId) return;
    
    try {
        const pkg = await apiGet(`/api/package/${state.currentProductionId}`);
        if (pkg.status && !pkg.concept) {
            $('#package-content').innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📦</div>
                    <p>${pkg.message || 'Package not ready yet.'}</p>
                </div>`;
            return;
        }
        
        // Load emotional analysis and concerns in parallel
        let emotional = null;
        let concerns = null;
        try {
            emotional = await apiGet(`/api/emotional/${state.currentProductionId}`);
        } catch (e) { /* ignore */ }
        try {
            concerns = await apiGet(`/api/concerns/${state.currentProductionId}`);
        } catch (e) { /* ignore */ }
        
        renderPackage(pkg, emotional, concerns);
    } catch (e) {
        console.error('Load package failed:', e);
    }
}

function renderPackage(pkg, emotional, concerns) {
    const container = $('#package-content');
    const concept = pkg.concept || {};
    const scenes = pkg.scenes || [];
    const characters = pkg.characters || [];
    const environments = pkg.environments || [];
    const shotLists = pkg.shot_lists || [];
    
    const hasEmotional = emotional && emotional.score !== undefined;
    const hasConcerns = concerns && concerns.concerns_count > 0;
    
    container.innerHTML = `
        <div class="card fade-in" style="margin-bottom:20px;">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:16px;">
                <div>
                    <h2 style="margin-bottom:4px;">${concept.title || 'Untitled'}</h2>
                    <p style="color:var(--text-secondary);font-size:14px;">${concept.logline || ''}</p>
                </div>
                <span class="badge badge-complete">Complete</span>
            </div>
            <div style="display:flex;gap:24px;font-size:13px;color:var(--text-muted);flex-wrap:wrap;">
                <span><strong>Genre:</strong> ${concept.genre || '—'}</span>
                <span><strong>Setting:</strong> ${concept.setting || '—'}</span>
                <span><strong>Theme:</strong> ${concept.theme || '—'}</span>
                <span><strong>Scenes:</strong> ${scenes.length}</span>
                <span><strong>Characters:</strong> ${characters.length}</span>
            </div>
            ${pkg.director_decision ? renderDirectorDecision(pkg.director_decision) : ''}
            ${hasEmotional ? renderEmotionalBadge(emotional) : ''}
            ${hasConcerns ? renderConcernsBadge(concerns) : ''}
        </div>
        
        <div class="package-nav">
            <button class="package-nav-item active" data-section="scenes">Scenes</button>
            <button class="package-nav-item" data-section="characters">Characters</button>
            <button class="package-nav-item" data-section="environments">Environments</button>
            <button class="package-nav-item" data-section="shots">Shot Lists</button>
            <button class="package-nav-item" data-section="reviews">Reviews</button>
            ${hasEmotional ? '<button class="package-nav-item" data-section="emotional">Emotional</button>' : ''}
            ${hasConcerns ? `<button class="package-nav-item" data-section="concerns">Concerns ${concerns.critical_count > 0 ? '🔴' : concerns.concerns_count > 0 ? '🟠' : ''}</button>` : ''}
        </div>
        
        <div class="package-section active" id="section-scenes">
            ${scenes.map(s => `
                <div class="scene-card">
                    <div class="scene-slugline">${s.slugline}</div>
                    <div style="font-size:12px;color:var(--text-muted);margin-bottom:8px;">
                        Characters: ${s.characters?.join(', ') || '—'} | Duration: ${s.duration_estimate || '—'}
                    </div>
                    <div class="scene-content">${s.content_preview || ''}</div>
                </div>
            `).join('') || '<p style="color:var(--text-muted)">No scenes yet.</p>'}
        </div>
        
        <div class="package-section" id="section-characters">
            <div class="card-grid">
                ${characters.map(c => `
                    <div class="character-card">
                        <div class="character-name">${c.name}</div>
                        <div class="character-archetype">${c.archetype}</div>
                        <div style="font-size:12px;color:var(--text-muted);">Role: ${c.role}</div>
                    </div>
                `).join('') || '<p style="color:var(--text-muted)">No characters yet.</p>'}
            </div>
        </div>
        
        <div class="package-section" id="section-environments">
            <div class="card-grid">
                ${environments.map(e => `
                    <div class="env-card">
                        <h3 style="margin-bottom:4px;">${e.name}</h3>
                        <div style="font-size:12px;color:var(--accent-light);text-transform:uppercase;">${e.type}</div>
                    </div>
                `).join('') || '<p style="color:var(--text-muted)">No environments yet.</p>'}
            </div>
        </div>
        
        <div class="package-section" id="section-shots">
            ${shotLists.map(sl => `
                <div class="shot-card">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <h3 style="margin:0;">${sl.scene_id}</h3>
                        <span style="font-size:12px;color:var(--text-muted);">${sl.shot_count} shots • ${sl.total_duration}s</span>
                    </div>
                </div>
            `).join('') || '<p style="color:var(--text-muted)">No shot lists yet.</p>'}
        </div>
        
        <div class="package-section" id="section-reviews">
            <div class="card">
                <h3>Review Summary</h3>
                <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;text-align:center;margin-top:16px;">
                    <div><div style="font-size:28px;font-weight:700;font-family:var(--font-mono);color:var(--text-primary)">${pkg.reviews?.total_reviews || 0}</div><div style="font-size:11px;color:var(--text-muted)">Total</div></div>
                    <div><div style="font-size:28px;font-weight:700;font-family:var(--font-mono);color:var(--warning)">${pkg.reviews?.pending || 0}</div><div style="font-size:11px;color:var(--text-muted)">Pending</div></div>
                    <div><div style="font-size:28px;font-weight:700;font-family:var(--font-mono);color:var(--success)">${pkg.reviews?.applied || 0}</div><div style="font-size:11px;color:var(--text-muted)">Applied</div></div>
                    <div><div style="font-size:28px;font-weight:700;font-family:var(--font-mono);color:var(--danger)">${pkg.reviews?.rejected || 0}</div><div style="font-size:11px;color:var(--text-muted)">Rejected</div></div>
                </div>
            </div>
        </div>
        
        ${hasEmotional ? `
        <div class="package-section" id="section-emotional">
            <div class="card">
                <h3>Emotional Arc Analysis</h3>
                <div style="display:flex;gap:24px;margin-top:16px;flex-wrap:wrap;">
                    <div style="text-align:center;">
                        <div style="font-size:36px;font-weight:700;color:${emotional.score >= 7 ? '#22c55e' : emotional.score >= 4 ? '#f59e0b' : '#ef4444'};">${emotional.score}/10</div>
                        <div style="font-size:12px;color:var(--text-muted);">Score</div>
                    </div>
                    <div style="text-align:center;">
                        <div style="font-size:36px;font-weight:700;color:var(--text-primary);">${emotional.arc || '—'}</div>
                        <div style="font-size:12px;color:var(--text-muted);">Arc Type</div>
                    </div>
                    <div style="text-align:center;">
                        <div style="font-size:36px;font-weight:700;color:var(--text-primary);">${emotional.valence_range || '—'}</div>
                        <div style="font-size:12px;color:var(--text-muted);">Valence Range</div>
                    </div>
                </div>
            </div>
            <div class="card" style="margin-top:16px;">
                <pre style="white-space:pre-wrap;font-size:12px;color:var(--text-secondary);line-height:1.7;">${escapeHtml(emotional.content || '')}</pre>
            </div>
        </div>
        ` : ''}
        
        ${hasConcerns ? `
        <div class="package-section" id="section-concerns">
            <div class="card">
                <h3>Diffused Attention Concerns</h3>
                <div style="margin-top:16px;">
                    <pre style="white-space:pre-wrap;font-size:12px;color:var(--text-secondary);line-height:1.7;">${escapeHtml(concerns.content || '')}</pre>
                </div>
            </div>
        </div>
        ` : ''}
    `;
    
    // Package nav
    $$('.package-nav-item').forEach(item => {
        item.addEventListener('click', () => {
            $$('.package-nav-item').forEach(i => i.classList.remove('active'));
            $$('.package-section').forEach(s => s.classList.remove('active'));
            item.classList.add('active');
            $(`#section-${item.dataset.section}`)?.classList.add('active');
        });
    });
}

$('#package-production-select')?.addEventListener('change', (e) => {
    state.currentProductionId = e.target.value;
    loadPackage();
});

// ============================================
// Vault
// ============================================

async function loadVault() {
    const folder = $('#vault-folder')?.value || '';
    try {
        const notes = await apiGet(`/api/vault?folder=${encodeURIComponent(folder)}`);
        state.vaultNotes = notes;
        renderVaultList(notes);
    } catch (e) {
        console.error('Load vault failed:', e);
    }
}

function renderVaultList(notes) {
    const list = $('#vault-list');
    const search = $('#vault-search')?.value?.toLowerCase() || '';
    
    const filtered = notes.filter(n => 
        n.title.toLowerCase().includes(search) || 
        n.path.toLowerCase().includes(search)
    );
    
    list.innerHTML = filtered.map(n => `
        <div class="vault-item ${state.activeVaultNote?.path === n.path ? 'active' : ''}" data-path="${n.path}">
            <div class="vault-item-title">${n.title}</div>
            <div class="vault-item-path">${n.path}</div>
        </div>
    `).join('');
    
    $$('.vault-item').forEach(item => {
        item.addEventListener('click', () => loadVaultDetail(item.dataset.path));
    });
}

async function loadVaultDetail(path) {
    try {
        const note = await apiGet(`/api/vault/${encodeURIComponent(path)}`);
        state.activeVaultNote = note;
        renderVaultDetail(note);
        renderVaultList(state.vaultNotes);
    } catch (e) {
        showToast('Failed to load note', 'error');
    }
}

function renderVaultDetail(note) {
    const detail = $('#vault-detail');
    
    let contentHtml = '';
    // Simple markdown-to-HTML conversion
    const lines = note.content.split('\n');
    let inCode = false;
    
    for (const line of lines) {
        if (line.startsWith('```')) {
            if (inCode) {
                contentHtml += '</pre>';
                inCode = false;
            } else {
                contentHtml += '<pre>';
                inCode = true;
            }
            continue;
        }
        if (inCode) {
            contentHtml += escapeHtml(line) + '\n';
            continue;
        }
        
        if (line.startsWith('# ')) {
            contentHtml += `<h1>${escapeHtml(line.slice(2))}</h1>`;
        } else if (line.startsWith('## ')) {
            contentHtml += `<h2>${escapeHtml(line.slice(3))}</h2>`;
        } else if (line.startsWith('### ')) {
            contentHtml += `<h3>${escapeHtml(line.slice(4))}</h3>`;
        } else if (line.startsWith('- ')) {
            contentHtml += `<li>${escapeHtml(line.slice(2))}</li>`;
        } else if (line.startsWith('**') && line.includes('**:')) {
            const [label, ...rest] = line.split(':');
            contentHtml += `<p><strong>${escapeHtml(label.replace(/\*\*/g, ''))}:</strong>${escapeHtml(rest.join(':'))}</p>`;
        } else if (line.trim() === '---') {
            contentHtml += '<hr>';
        } else if (line.trim() === '') {
            contentHtml += '<br>';
        } else {
            contentHtml += `<p>${escapeHtml(line)}</p>`;
        }
    }
    
    const tagsHtml = note.tags?.length 
        ? `<div style="margin-bottom:16px;">${note.tags.map(t => `<span class="tag">#${t}</span>`).join(' ')}</div>` 
        : '';
    
    detail.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:16px;">
            <h2 style="margin:0;">${note.title}</h2>
            <span style="font-size:11px;color:var(--text-muted);font-family:var(--font-mono);">${note.path}</span>
        </div>
        ${tagsHtml}
        ${contentHtml}
    `;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

$('#vault-folder')?.addEventListener('change', loadVault);
$('#vault-search')?.addEventListener('input', () => renderVaultList(state.vaultNotes));
$('#refresh-vault')?.addEventListener('click', loadVault);

// ============================================
// Modal
// ============================================

function showModal(title, content) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal" style="
            position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);
            background:var(--bg-1);border:1px solid var(--border);border-radius:12px;
            padding:24px;max-width:600px;width:90%;max-height:80vh;overflow:auto;z-index:2000;
            box-shadow:var(--shadow);
        ">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
                <h3 style="margin:0;">${escapeHtml(title)}</h3>
                <button onclick="this.closest('.modal-overlay').remove()" style="background:none;border:none;color:var(--text-muted);cursor:pointer;font-size:20px;">×</button>
            </div>
            <div style="color:var(--text-secondary);line-height:1.7;white-space:pre-wrap;">${escapeHtml(content)}</div>
        </div>
        <div style="position:fixed;inset:0;background:rgba(0,0,0,0.5);z-index:1999;" onclick="this.closest('.modal-overlay').remove()"></div>
    `;
    document.body.appendChild(modal);
}

// ============================================
// Memory (Vector Search)
// ============================================

async function loadMemoryStats() {
    try {
        const stats = await apiGet('/api/memory/stats');
        const container = $('#memory-stats');
        const collections = stats.collections || {};
        const total = Object.values(collections).reduce((a, b) => a + b, 0);
        
        const items = Object.entries(collections)
            .filter(([_, count]) => count > 0)
            .map(([name, count]) => `<span class="memory-stat-item">${name}: ${count}</span>`)
            .join('');
        
        container.innerHTML = items ? `${items} <span class="memory-stat-total">(total: ${total})</span>` : '';
    } catch (e) {
        console.error('Load memory stats failed:', e);
    }
}

async function searchMemory() {
    const query = $('#memory-query').value.trim();
    const docType = $('#memory-doc-type').value;
    const container = $('#memory-results');
    
    if (!query) {
        showToast('Enter a search query', 'warning');
        return;
    }
    
    container.innerHTML = `
        <div class="memory-loading">
            <div class="spinner"></div>
            <p>Searching memory...</p>
        </div>
    `;
    
    try {
        let url = `/api/memory/search?q=${encodeURIComponent(query)}&n=10`;
        if (docType) url += `&doc_type=${encodeURIComponent(docType)}`;
        
        const data = await apiGet(url);
        renderMemoryResults(data);
    } catch (e) {
        console.error('Memory search failed:', e);
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">⚠</div>
                <p>Search failed. ${escapeHtml(e.message)}</p>
            </div>
        `;
    }
}

function renderMemoryResults(data) {
    const container = $('#memory-results');
    const results = data.results || [];
    
    if (!results.length) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🔍</div>
                <p>No results found for "${escapeHtml(data.query)}".</p>
            </div>
        `;
        return;
    }
    
    const typeColors = {
        concept: '#3b82f6',
        evaluation: '#22c55e',
        post_mortem: '#a855f7',
        voice_profile: '#f59e0b',
        scene: '#ef4444',
        director_decision: '#ec4899',
    };
    
    container.innerHTML = `
        <div class="memory-results-header">
            <span>${results.length} results for "${escapeHtml(data.query)}"</span>
        </div>
        <div class="memory-result-list">
            ${results.map(r => `
                <div class="memory-result-card fade-in">
                    <div class="memory-result-meta">
                        <span class="memory-result-type" style="background:${typeColors[r.doc_type] || '#666'}20;color:${typeColors[r.doc_type] || '#666'}">
                            ${r.doc_type.replace('_', ' ')}
                        </span>
                        <span class="memory-result-score">${(r.score * 100).toFixed(0)}% match</span>
                    </div>
                    <div class="memory-result-text">${escapeHtml(r.text.substring(0, 280))}${r.text.length > 280 ? '...' : ''}</div>
                    ${r.metadata && Object.keys(r.metadata).length ? `
                        <div class="memory-result-meta-tags">
                            ${Object.entries(r.metadata).slice(0, 3).map(([k, v]) => `
                                <span class="memory-tag">${escapeHtml(k)}: ${escapeHtml(String(v)).substring(0, 30)}</span>
                            `).join('')}
                        </div>
                    ` : ''}
                </div>
            `).join('')}
        </div>
    `;
}

// Enter key on memory query
$('#memory-query')?.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') searchMemory();
});

// ============================================
// Init
// ============================================

function init() {
    // Tab navigation
    $$('.nav-tab').forEach(tab => {
        tab.addEventListener('click', () => showTab(tab.dataset.tab));
    });
    
    // Form
    initProduceForm();
    
    // Health check
    checkHealth();
    setInterval(checkHealth, 5000);
    
    // Initial vault load
    loadVault();
    
    // Start polling for production updates
    startPolling();
}

document.addEventListener('DOMContentLoaded', init);
