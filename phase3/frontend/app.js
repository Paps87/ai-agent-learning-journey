// Mini Perplexity - Frontend JavaScript

const API_URL = '';  // Même domaine que le frontend (pas de CORS)

// Elements
const queryInput = document.getElementById('queryInput');
const searchBtn = document.getElementById('searchBtn');
const searchContainer = document.getElementById('searchContainer');
const resultsContainer = document.getElementById('resultsContainer');
const questionDisplay = document.getElementById('questionDisplay');
const loading = document.getElementById('loading');
const answerContainer = document.getElementById('answerContainer');
const answerContent = document.getElementById('answerContent');
const answerMeta = document.getElementById('answerMeta');
const sourcesContainer = document.getElementById('sourcesContainer');
const sourcesGrid = document.getElementById('sourcesGrid');
const newSearchBtn = document.getElementById('newSearchBtn');
const statusText = document.querySelector('.status-text');
const statusDot = document.querySelector('.status-dot');

// Event Listeners
searchBtn.addEventListener('click', handleSearch);
queryInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleSearch();
});
newSearchBtn.addEventListener('click', resetSearch);

// Suggestions
document.querySelectorAll('.suggestion').forEach(btn => {
    btn.addEventListener('click', () => {
        queryInput.value = btn.dataset.query;
        handleSearch();
    });
});

// Check API Health on load
checkHealth();

async function checkHealth() {
    try {
        const response = await fetch(`${API_URL}/api/health`);
        const data = await response.json();

        if (data.lm_studio_connected) {
            updateStatus('Prêt', 'success');
        } else {
            updateStatus('LM Studio déconnecté', 'warning');
        }
    } catch (error) {
        updateStatus('Backend déconnecté', 'error');
    }
}

function updateStatus(text, type) {
    statusText.textContent = text;
    statusDot.style.background =
        type === 'success' ? 'var(--success)' :
            type === 'warning' ? 'var(--warning)' :
                '#ef4444';
}

async function handleSearch() {
    const query = queryInput.value.trim();

    if (!query) {
        queryInput.focus();
        return;
    }

    // Show results container
    resultsContainer.style.display = 'block';
    searchContainer.classList.add('compact');

    // Display question
    questionDisplay.textContent = query;

    // Show loading
    loading.style.display = 'flex';
    answerContainer.style.display = 'none';
    sourcesContainer.style.display = 'none';
    newSearchBtn.style.display = 'none';

    updateStatus('Recherche...', 'warning');

    try {
        const response = await fetch(`${API_URL}/api/ask`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                max_results: 5,
                use_web: true
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        // Hide loading
        loading.style.display = 'none';

        // Display answer
        displayAnswer(data);

        // Display sources
        displaySources(data.sources);

        // Show new search button
        newSearchBtn.style.display = 'flex';

        updateStatus('Prêt', 'success');

    } catch (error) {
        console.error('Error:', error);
        loading.style.display = 'none';

        answerContainer.style.display = 'block';
        answerContent.innerHTML = `
            <p style="color: #ef4444;">
                ❌ Erreur: ${error.message}
            </p>
            <p style="color: var(--text-secondary); font-size: 14px; margin-top: 12px;">
                Vérifiez que le backend est lancé sur le port 8000 et que LM Studio est actif.
            </p>
        `;

        updateStatus('Erreur', 'error');
    }
}

function displayAnswer(data) {
    answerContainer.style.display = 'block';

    // Meta info
    answerMeta.textContent = `${data.processing_time.toFixed(2)}s • ${data.web_sources_count} sources web`;

    // Format answer with citations
    let formattedAnswer = data.answer;

    // Convert markdown-style bold
    formattedAnswer = formattedAnswer.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Highlight citations [1], [2], etc.
    formattedAnswer = formattedAnswer.replace(/\[(\d+)\]/g,
        '<span class="citation" onclick="scrollToSource($1)">[$1]</span>');

    // Convert line breaks to paragraphs
    const paragraphs = formattedAnswer.split('\n\n').filter(p => p.trim());
    formattedAnswer = paragraphs.map(p => `<p>${p}</p>`).join('');

    answerContent.innerHTML = formattedAnswer;
}

function displaySources(sources) {
    if (!sources || sources.length === 0) {
        sourcesContainer.style.display = 'none';
        return;
    }

    sourcesContainer.style.display = 'block';
    sourcesGrid.innerHTML = '';

    sources.forEach((source, index) => {
        const card = document.createElement('a');
        card.className = 'source-card';
        card.href = source.url;
        card.target = '_blank';
        card.id = `source-${index + 1}`;

        card.innerHTML = `
            <div>
                <span class="source-number">${index + 1}</span>
                <span class="source-title">${escapeHtml(source.title)}</span>
            </div>
            <div class="source-url">${escapeHtml(source.url)}</div>
            <span class="source-type">${source.type === 'web' ? '🌐 Web' : '📚 Local'}</span>
        `;

        sourcesGrid.appendChild(card);
    });
}

function scrollToSource(number) {
    const sourceElement = document.getElementById(`source-${number}`);
    if (sourceElement) {
        sourceElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        sourceElement.style.borderColor = 'var(--accent)';
        setTimeout(() => {
            sourceElement.style.borderColor = '';
        }, 2000);
    }
}

function resetSearch() {
    resultsContainer.style.display = 'none';
    searchContainer.classList.remove('compact');
    queryInput.value = '';
    queryInput.focus();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Auto-focus on input
queryInput.focus();
