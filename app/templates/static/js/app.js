/* PhysicsOJ - Physics Online Judge - Frontend */

const API = '';

// ===== Utility =====

async function fetchJSON(url) {
    const res = await fetch(API + url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
}

async function postJSON(url, data) {
    const res = await fetch(API + url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
    return res.json();
}

function getUsername() {
    return localStorage.getItem('physicsoj_username') || 'guest';
}

function setUsername(name) {
    localStorage.setItem('physicsoj_username', name);
}

// ===== Router =====

function getRoute() {
    const hash = window.location.hash.slice(1) || 'home';
    const parts = hash.split('/');
    return { page: parts[0], params: parts.slice(1) };
}

// ===== Render helpers =====

function difficultyBadge(d) {
    const labels = { easy: '쉬움', medium: '보통', hard: '어려움', olympiad: '올림피아드' };
    return `<span class="badge badge-${d}">${labels[d] || d}</span>`;
}

function statusBadge(s) {
    const labels = { correct: '정답', wrong: '오답', partial: '부분 점수', pending: '대기' };
    return `<span class="badge badge-${s}">${labels[s] || s}</span>`;
}

function loading() {
    return '<div class="loading-spinner"><div class="spinner"></div></div>';
}

// ===== HOME PAGE =====

async function renderHome() {
    const main = document.getElementById('app');
    main.innerHTML = loading();

    const [problems, competitions] = await Promise.all([
        fetchJSON('/api/problems'),
        fetchJSON('/api/competitions'),
    ]);

    const totalProblems = problems.length;
    const totalComps = competitions.length;
    const topics = [...new Set(problems.map(p => p.topic))].length;

    main.innerHTML = `
        <div class="hero">
            <span class="hero-badge">Physics Online Judge</span>
            <h1>물리학 문제를<br>풀고 실력을 키우세요</h1>
            <p>IPhO, KPhO, APhO 등 세계 물리 대회 기출문제를 풀고<br>즉시 채점 받을 수 있습니다</p>
            <div class="hero-actions">
                <a href="#problems" class="btn btn-primary btn-lg">문제 풀기</a>
                <a href="#competitions" class="btn btn-outline btn-lg">대회 둘러보기</a>
            </div>
            <div class="quick-stats">
                <div class="quick-stat">
                    <div class="qs-value">${totalProblems}</div>
                    <div class="qs-label">문제</div>
                </div>
                <div class="quick-stat">
                    <div class="qs-value">${totalComps}</div>
                    <div class="qs-label">대회</div>
                </div>
                <div class="quick-stat">
                    <div class="qs-value">${topics}</div>
                    <div class="qs-label">주제 분야</div>
                </div>
            </div>
        </div>

        <h3 class="home-section-title">대회별 문제</h3>
        <div class="feature-grid">
            ${competitions.map(c => `
                <a href="#problems" class="feature-card" onclick="setTimeout(()=>{const el=document.getElementById('filter-comp');if(el){el.value='${c.abbreviation}';el.dispatchEvent(new Event('change'));}},150)">
                    <div class="fc-icon fc-icon-blue">${c.abbreviation.charAt(0)}</div>
                    <h3>${c.name}</h3>
                    <p>${c.description}</p>
                    <span class="fc-meta">${c.problem_count}개 문제 &rarr;</span>
                </a>
            `).join('')}
        </div>

        <h3 class="home-section-title">최근 추가된 문제</h3>
        <div class="problem-list">
            ${problems.slice(0, 5).map(p => `
                <a class="problem-item" href="#problem/${p.id}">
                    <span class="problem-id">${p.competition_abbr} ${p.year}-${p.problem_number}</span>
                    <div class="problem-title-block">
                        <h3>${p.title}</h3>
                        <div class="meta">${p.topic}</div>
                    </div>
                    ${difficultyBadge(p.difficulty)}
                    <span class="problem-points">${p.points}점</span>
                    <span class="problem-solved">${p.solved_count}명 풀이</span>
                </a>
            `).join('')}
        </div>
        <div style="text-align:center;margin-top:1.25rem;">
            <a href="#problems" class="btn btn-outline">모든 문제 보기 &rarr;</a>
        </div>
    `;
}

// ===== PROBLEMS PAGE =====

async function renderProblems() {
    const main = document.getElementById('app');
    main.innerHTML = loading();

    const [problems, topics, competitions] = await Promise.all([
        fetchJSON('/api/problems'),
        fetchJSON('/api/problems/topics'),
        fetchJSON('/api/competitions'),
    ]);

    let html = `
        <div class="page-header">
            <h2>Problems</h2>
            <p>${problems.length}개의 물리학 문제</p>
        </div>
        <div class="filters">
            <select id="filter-comp">
                <option value="">모든 대회</option>
                ${competitions.map(c => `<option value="${c.abbreviation}">${c.abbreviation}</option>`).join('')}
            </select>
            <select id="filter-topic">
                <option value="">모든 주제</option>
                ${topics.map(t => `<option value="${t}">${t}</option>`).join('')}
            </select>
            <select id="filter-diff">
                <option value="">모든 난이도</option>
                <option value="easy">쉬움</option>
                <option value="medium">보통</option>
                <option value="hard">어려움</option>
                <option value="olympiad">올림피아드</option>
            </select>
        </div>
        <div class="problem-list" id="problem-list">
    `;

    for (const p of problems) {
        html += `
            <a class="problem-item" href="#problem/${p.id}"
               data-comp="${p.competition_abbr}" data-topic="${p.topic}" data-diff="${p.difficulty}">
                <span class="problem-id">${p.competition_abbr} ${p.year}-${p.problem_number}</span>
                <div class="problem-title-block">
                    <h3>${p.title}</h3>
                    <div class="meta">${p.topic}</div>
                </div>
                ${difficultyBadge(p.difficulty)}
                <span class="problem-points">${p.points}점</span>
                <span class="problem-solved">${p.solved_count}명 풀이</span>
            </a>
        `;
    }
    html += '</div>';
    main.innerHTML = html;

    const filterComp = document.getElementById('filter-comp');
    const filterTopic = document.getElementById('filter-topic');
    const filterDiff = document.getElementById('filter-diff');

    function applyFilters() {
        const comp = filterComp.value;
        const topic = filterTopic.value;
        const diff = filterDiff.value;
        document.querySelectorAll('.problem-item').forEach(el => {
            const show =
                (!comp || el.dataset.comp === comp) &&
                (!topic || el.dataset.topic === topic) &&
                (!diff || el.dataset.diff === diff);
            el.style.display = show ? '' : 'none';
        });
    }

    filterComp.addEventListener('change', applyFilters);
    filterTopic.addEventListener('change', applyFilters);
    filterDiff.addEventListener('change', applyFilters);
}

// ===== PROBLEM DETAIL =====

async function renderProblem(id) {
    const main = document.getElementById('app');
    main.innerHTML = loading();

    const problem = await fetchJSON(`/api/problems/${id}`);

    const answerInput = problem.answer_type === 'multi_part'
        ? `<textarea id="answer-input" placeholder='{"a": "답1", "b": "답2"}'></textarea>`
        : problem.answer_type === 'multiple_choice'
            ? `<input type="text" id="answer-input" placeholder="A, B, C, 또는 D">`
            : `<input type="text" id="answer-input" placeholder="답을 입력하세요 (숫자 또는 수식)">`;

    let hintsHtml = '';
    if (problem.hints && problem.hints.length > 0) {
        hintsHtml = `
            <div class="hints-section">
                <span class="solution-toggle" onclick="showHints()">&#128161; 힌트 보기</span>
                <div id="hints-container">
                    ${problem.hints.map((h, i) => `<div class="hint-item" id="hint-${i}">${i + 1}. ${h}</div>`).join('')}
                </div>
            </div>
        `;
    }

    const typeLabels = {
        numeric: '숫자를 입력하세요 (예: 3.14, 2.5e3)',
        expression: '수식을 입력하세요 (예: 2*pi*sqrt(L/g))',
        multiple_choice: '보기를 입력하세요 (A, B, C, D)',
        multi_part: 'JSON 형식으로 입력하세요',
    };

    main.innerHTML = `
        <div class="problem-detail">
            <a href="#problems" class="btn btn-ghost btn-sm" style="margin-bottom:1rem;">&larr; 목록으로</a>
            <div class="card">
                <h2 style="font-size:1.3rem;font-weight:800;letter-spacing:-0.02em;">${problem.title}</h2>
                <div class="problem-meta">
                    <span style="font-weight:600;color:var(--primary);">${problem.competition_abbr} ${problem.year} #${problem.problem_number}</span>
                    ${difficultyBadge(problem.difficulty)}
                    <span>${problem.topic}</span>
                    <span>${problem.points}점</span>
                    <span>${problem.solved_count}명 풀이</span>
                </div>
                <div class="problem-body" id="problem-body">
                    ${problem.description}
                </div>

                ${hintsHtml}

                <div class="answer-form">
                    <h3>답안 제출</h3>
                    <div class="input-group">
                        ${answerInput}
                        <button class="btn btn-primary" onclick="submitAnswer(${problem.id})">제출</button>
                    </div>
                    <div class="input-hint">${typeLabels[problem.answer_type] || ''}</div>
                </div>

                <div class="result-box" id="result-box">
                    <div class="result-header" id="result-header"></div>
                    <div class="result-score" id="result-score"></div>
                    <div class="result-feedback" id="result-feedback"></div>
                </div>

                <div class="solution-section">
                    <span class="solution-toggle" onclick="toggleSolution(${problem.id})">&#128214; 풀이 보기</span>
                    <div class="solution-content" id="solution-content"></div>
                </div>
            </div>
        </div>
    `;

    if (window.MathJax) {
        MathJax.typesetPromise([document.getElementById('problem-body')]);
    }
}

// ===== COMPETITIONS PAGE =====

async function renderCompetitions() {
    const main = document.getElementById('app');
    main.innerHTML = loading();

    const competitions = await fetchJSON('/api/competitions');

    const icons = { IPhO: '🌍', APhO: '🌏', KPhO: '🇰🇷', 'F=ma': '🇺🇸', BPhO: '🇬🇧' };

    let html = `
        <div class="page-header">
            <h2>Competitions</h2>
            <p>등록된 물리학 대회</p>
        </div>
        <div class="competition-grid">
    `;

    for (const c of competitions) {
        html += `
            <div class="comp-card">
                <span class="abbr">${icons[c.abbreviation] || ''} ${c.abbreviation}</span>
                <h3>${c.name}</h3>
                <div class="desc">${c.description}</div>
                <div class="count">${c.problem_count}개 문제</div>
                <a href="#problems" onclick="setTimeout(()=>{const el=document.getElementById('filter-comp');if(el){el.value='${c.abbreviation}';el.dispatchEvent(new Event('change'));}},150)" class="btn btn-outline btn-sm" style="margin-top:0.75rem;">문제 보기 &rarr;</a>
            </div>
        `;
    }
    html += '</div>';
    main.innerHTML = html;
}

// ===== LEADERBOARD PAGE =====

async function renderLeaderboard() {
    const main = document.getElementById('app');
    main.innerHTML = loading();

    const [leaderboard, userStats] = await Promise.all([
        fetchJSON('/api/stats/leaderboard'),
        fetchJSON(`/api/stats/user/${getUsername()}`).catch(() => null),
    ]);

    let html = `<div class="page-header"><h2>Leaderboard</h2><p>사용자 순위</p></div>`;

    if (userStats) {
        html += `
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">${userStats.problems_solved}</div>
                    <div class="stat-label">풀이 완료</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${userStats.total_submissions}</div>
                    <div class="stat-label">총 제출</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${(userStats.accuracy * 100).toFixed(1)}%</div>
                    <div class="stat-label">정답률</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${userStats.total_score.toFixed(1)}</div>
                    <div class="stat-label">총점</div>
                </div>
            </div>
        `;
    }

    if (leaderboard.length === 0) {
        html += '<div class="card"><p style="color:var(--text-muted);">아직 제출된 답안이 없습니다.</p></div>';
    } else {
        const rankIcons = { 1: '🥇', 2: '🥈', 3: '🥉' };
        html += `
            <div class="card" style="padding:0;overflow:hidden;">
                <table class="leaderboard-table">
                    <thead>
                        <tr><th>순위</th><th>사용자</th><th>총점</th><th>풀이 수</th></tr>
                    </thead>
                    <tbody>
                        ${leaderboard.map(e => `
                            <tr>
                                <td class="${e.rank <= 3 ? 'rank-' + e.rank : ''}">${rankIcons[e.rank] || ''} #${e.rank}</td>
                                <td style="font-weight:600;">${e.display_name}</td>
                                <td>${e.total_score.toFixed(1)}</td>
                                <td>${e.problems_solved}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }

    main.innerHTML = html;
}

// ===== HISTORY PAGE =====

async function renderHistory() {
    const main = document.getElementById('app');
    main.innerHTML = loading();

    try {
        const history = await fetchJSON(`/api/submissions/history/${getUsername()}`);

        let html = `
            <div class="page-header">
                <h2>History</h2>
                <p>${getUsername()}님의 제출 이력</p>
            </div>
        `;

        if (history.length === 0) {
            html += `
                <div class="card" style="text-align:center;padding:3rem;">
                    <p style="color:var(--text-muted);margin-bottom:1rem;">아직 제출한 답안이 없습니다</p>
                    <a href="#problems" class="btn btn-primary">문제 풀러 가기</a>
                </div>
            `;
        } else {
            html += '<div class="problem-list">';
            for (const s of history) {
                html += `
                    <a class="problem-item" href="#problem/${s.problem_id}">
                        <span class="problem-id">#${s.problem_id}</span>
                        <div class="problem-title-block">
                            <h3>${s.problem_title}</h3>
                            <div class="meta">${new Date(s.submitted_at).toLocaleString('ko-KR')}</div>
                        </div>
                        ${statusBadge(s.status)}
                        <span class="problem-points">${s.score}점</span>
                        <span></span>
                    </a>
                `;
            }
            html += '</div>';
        }

        main.innerHTML = html;
    } catch {
        main.innerHTML = `
            <div class="card" style="text-align:center;padding:3rem;">
                <p style="color:var(--text-muted);margin-bottom:1rem;">제출 이력이 없습니다</p>
                <a href="#problems" class="btn btn-primary">문제 풀러 가기</a>
            </div>
        `;
    }
}

// ===== Actions =====

async function submitAnswer(problemId) {
    const input = document.getElementById('answer-input');
    const answer = input.value.trim();
    if (!answer) { alert('답안을 입력해주세요.'); return; }

    const resultBox = document.getElementById('result-box');
    resultBox.style.display = 'none';

    const data = await postJSON('/api/submissions', {
        problem_id: problemId,
        username: getUsername(),
        answer: answer,
    });

    resultBox.style.display = 'block';
    resultBox.className = 'result-box ' + data.status;

    const headers = { correct: '정답!', wrong: '오답', partial: '부분 점수' };
    document.getElementById('result-header').textContent = headers[data.status] || data.status;
    document.getElementById('result-score').textContent = `점수: ${data.score} / ${data.max_score}`;
    document.getElementById('result-feedback').textContent = data.feedback;
}

async function toggleSolution(problemId) {
    const content = document.getElementById('solution-content');
    if (content.style.display === 'block') { content.style.display = 'none'; return; }

    const data = await fetchJSON(`/api/problems/${problemId}/solution`);
    content.innerHTML = data.solution || '풀이가 아직 등록되지 않았습니다.';
    content.style.display = 'block';

    if (window.MathJax) { MathJax.typesetPromise([content]); }
}

let hintsRevealed = 0;
function showHints() {
    const hint = document.getElementById(`hint-${hintsRevealed}`);
    if (hint) { hint.style.display = 'block'; hintsRevealed++; }
}

function promptUsername() {
    const current = getUsername();
    const name = prompt('사용자명을 입력하세요:', current);
    if (name && name.trim()) { setUsername(name.trim()); route(); }
}

// ===== Router =====

async function route() {
    const { page, params } = getRoute();

    // Update nav
    document.querySelectorAll('#main-nav a').forEach(a => {
        a.classList.toggle('active', a.dataset.page === page);
    });

    document.getElementById('username-display').textContent = getUsername();

    // Reset hints counter
    hintsRevealed = 0;

    try {
        switch (page) {
            case 'home': await renderHome(); break;
            case 'problems': await renderProblems(); break;
            case 'problem': await renderProblem(params[0]); break;
            case 'competitions': await renderCompetitions(); break;
            case 'leaderboard': await renderLeaderboard(); break;
            case 'history': await renderHistory(); break;
            default: await renderHome();
        }
    } catch (err) {
        document.getElementById('app').innerHTML =
            `<div class="card" style="text-align:center;padding:2rem;">
                <p style="color:var(--danger);">오류가 발생했습니다: ${err.message}</p>
            </div>`;
    }
}

window.addEventListener('hashchange', route);
window.addEventListener('load', route);
