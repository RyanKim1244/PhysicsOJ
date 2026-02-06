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

function navigate(hash) {
    window.location.hash = hash;
}

function getRoute() {
    const hash = window.location.hash.slice(1) || 'problems';
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

// ===== Pages =====

async function renderProblems() {
    const main = document.getElementById('app');
    main.innerHTML = '<div class="loading">로딩 중...</div>';

    const [problems, topics, competitions] = await Promise.all([
        fetchJSON('/api/problems'),
        fetchJSON('/api/problems/topics'),
        fetchJSON('/api/competitions'),
    ]);

    let html = `
        <h2 style="margin-bottom:1rem;">문제 목록</h2>
        <div class="filters">
            <select id="filter-comp">
                <option value="">모든 대회</option>
                ${competitions.map(c => `<option value="${c.abbreviation}">${c.abbreviation} - ${c.name}</option>`).join('')}
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

    // Filters
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

async function renderProblem(id) {
    const main = document.getElementById('app');
    main.innerHTML = '<div class="loading">로딩 중...</div>';

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
                <span class="solution-toggle" onclick="showHints()">힌트 보기</span>
                <div id="hints-container">
                    ${problem.hints.map((h, i) => `<div class="hint-item" id="hint-${i}">${i + 1}. ${h}</div>`).join('')}
                </div>
            </div>
        `;
    }

    main.innerHTML = `
        <div class="problem-detail">
            <a href="#problems" class="btn btn-secondary" style="margin-bottom:1rem;">&larr; 목록으로</a>
            <div class="card">
                <h2>${problem.title}</h2>
                <div class="problem-meta">
                    <span>${problem.competition_abbr} ${problem.year} #${problem.problem_number}</span>
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
                    <div style="margin-top:0.5rem;font-size:0.8rem;color:var(--text-muted);">
                        답안 유형: ${problem.answer_type}
                        ${problem.answer_type === 'numeric' ? '| 숫자를 입력하세요 (예: 3.14, 2.5e3)' : ''}
                        ${problem.answer_type === 'expression' ? '| 수식을 입력하세요 (예: 2*pi*sqrt(L/g))' : ''}
                        ${problem.answer_type === 'multi_part' ? '| JSON 형식으로 입력하세요' : ''}
                    </div>
                </div>

                <div class="result-box" id="result-box">
                    <div class="result-header" id="result-header"></div>
                    <div class="result-score" id="result-score"></div>
                    <div class="result-feedback" id="result-feedback"></div>
                </div>

                <div class="solution-section">
                    <span class="solution-toggle" onclick="toggleSolution(${problem.id})">풀이 보기</span>
                    <div class="solution-content" id="solution-content"></div>
                </div>
            </div>
        </div>
    `;

    // Render LaTeX if MathJax loaded
    if (window.MathJax) {
        MathJax.typesetPromise([document.getElementById('problem-body')]);
    }
}

async function renderCompetitions() {
    const main = document.getElementById('app');
    main.innerHTML = '<div class="loading">로딩 중...</div>';

    const competitions = await fetchJSON('/api/competitions');

    let html = '<h2 style="margin-bottom:1rem;">대회 목록</h2><div class="competition-grid">';
    for (const c of competitions) {
        html += `
            <div class="comp-card">
                <span class="abbr">${c.abbreviation}</span>
                <h3>${c.name}</h3>
                <div class="desc">${c.description}</div>
                <div class="count">${c.problem_count}개 문제</div>
                <a href="#problems" onclick="setTimeout(()=>{document.getElementById('filter-comp').value='${c.abbreviation}';document.getElementById('filter-comp').dispatchEvent(new Event('change'));},100)" class="btn btn-secondary" style="margin-top:0.75rem;">문제 보기</a>
            </div>
        `;
    }
    html += '</div>';
    main.innerHTML = html;
}

async function renderLeaderboard() {
    const main = document.getElementById('app');
    main.innerHTML = '<div class="loading">로딩 중...</div>';

    const [leaderboard, userStats] = await Promise.all([
        fetchJSON('/api/stats/leaderboard'),
        fetchJSON(`/api/stats/user/${getUsername()}`).catch(() => null),
    ]);

    let html = '';

    if (userStats) {
        html += `
            <h2 style="margin-bottom:1rem;">내 통계</h2>
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

    html += `<h2 style="margin-bottom:1rem;">리더보드</h2>`;

    if (leaderboard.length === 0) {
        html += '<div class="card"><p>아직 제출된 답안이 없습니다.</p></div>';
    } else {
        html += `
            <div class="card" style="padding:0;overflow:hidden;">
                <table class="leaderboard-table">
                    <thead>
                        <tr><th>순위</th><th>사용자</th><th>총점</th><th>풀이 수</th></tr>
                    </thead>
                    <tbody>
                        ${leaderboard.map(e => `
                            <tr>
                                <td class="${e.rank <= 3 ? 'rank-' + e.rank : ''}">#${e.rank}</td>
                                <td>${e.display_name}</td>
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

async function renderHistory() {
    const main = document.getElementById('app');
    main.innerHTML = '<div class="loading">로딩 중...</div>';

    try {
        const history = await fetchJSON(`/api/submissions/history/${getUsername()}`);

        let html = `<h2 style="margin-bottom:1rem;">제출 이력 (${getUsername()})</h2>`;

        if (history.length === 0) {
            html += '<div class="card"><p>아직 제출한 답안이 없습니다.</p></div>';
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
                    </a>
                `;
            }
            html += '</div>';
        }

        main.innerHTML = html;
    } catch {
        main.innerHTML = '<div class="card"><p>사용자를 찾을 수 없습니다.</p></div>';
    }
}

// ===== Actions =====

async function submitAnswer(problemId) {
    const input = document.getElementById('answer-input');
    const answer = input.value.trim();
    if (!answer) {
        alert('답안을 입력해주세요.');
        return;
    }

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
    if (content.style.display === 'block') {
        content.style.display = 'none';
        return;
    }

    const data = await fetchJSON(`/api/problems/${problemId}/solution`);
    content.innerHTML = data.solution || '풀이가 아직 등록되지 않았습니다.';
    content.style.display = 'block';

    if (window.MathJax) {
        MathJax.typesetPromise([content]);
    }
}

let hintsRevealed = 0;
function showHints() {
    const hint = document.getElementById(`hint-${hintsRevealed}`);
    if (hint) {
        hint.style.display = 'block';
        hintsRevealed++;
    }
}

// ===== Username prompt =====

function promptUsername() {
    const current = getUsername();
    const name = prompt('사용자명을 입력하세요:', current);
    if (name && name.trim()) {
        setUsername(name.trim());
        route();
    }
}

// ===== Router =====

async function route() {
    const { page, params } = getRoute();

    // Update nav
    document.querySelectorAll('nav a').forEach(a => {
        a.classList.toggle('active', a.getAttribute('href') === '#' + page);
    });

    document.getElementById('username-display').textContent = getUsername();

    try {
        switch (page) {
            case 'problems':
                await renderProblems();
                break;
            case 'problem':
                await renderProblem(params[0]);
                break;
            case 'competitions':
                await renderCompetitions();
                break;
            case 'leaderboard':
                await renderLeaderboard();
                break;
            case 'history':
                await renderHistory();
                break;
            default:
                await renderProblems();
        }
    } catch (err) {
        document.getElementById('app').innerHTML =
            `<div class="card"><p>오류가 발생했습니다: ${err.message}</p></div>`;
    }
}

// Init
window.addEventListener('hashchange', route);
window.addEventListener('load', route);
