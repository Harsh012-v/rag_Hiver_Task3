// Configuration
// Use relative URL for Vercel deployment, fallback to localhost for local dev
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000'
    : window.location.origin;

// DOM Elements
const queryInput = document.getElementById('queryInput');
const searchBtn = document.getElementById('searchBtn');
const loadingState = document.getElementById('loadingState');
const errorState = document.getElementById('errorState');
const errorMessage = document.getElementById('errorMessage');
const resultsSection = document.getElementById('resultsSection');
const confidenceValue = document.getElementById('confidenceValue');
const confidenceFill = document.getElementById('confidenceFill');
const confidenceDescription = document.getElementById('confidenceDescription');
const answerContent = document.getElementById('answerContent');
const articleCount = document.getElementById('articleCount');
const articlesGrid = document.getElementById('articlesGrid');

// Quick query buttons
const quickQueryBtns = document.querySelectorAll('.quick-query-btn');

// Event Listeners
searchBtn.addEventListener('click', handleSearch);
queryInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        handleSearch();
    }
});

quickQueryBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const query = btn.getAttribute('data-query');
        queryInput.value = query;
        handleSearch();
    });
});

// Main search handler
async function handleSearch() {
    const query = queryInput.value.trim();

    if (!query) {
        showError('Please enter a query');
        return;
    }

    // Show loading state
    showLoading();

    try {
        const response = await fetch(`${API_BASE_URL}/api/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                k: 3
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to fetch results');
        }

        const data = await response.json();
        displayResults(data);

    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'Failed to connect to the server. Make sure the backend is running.');
    }
}

// Show loading state
function showLoading() {
    loadingState.classList.remove('hidden');
    errorState.classList.add('hidden');
    resultsSection.classList.add('hidden');
    searchBtn.disabled = true;
}

// Show error state
function showError(message) {
    errorMessage.textContent = message;
    errorState.classList.remove('hidden');
    loadingState.classList.add('hidden');
    resultsSection.classList.add('hidden');
    searchBtn.disabled = false;
}

// Display results
function displayResults(data) {
    // Hide loading and error states
    loadingState.classList.add('hidden');
    errorState.classList.add('hidden');
    searchBtn.disabled = false;

    // Show results section
    resultsSection.classList.remove('hidden');

    // Display confidence score
    displayConfidence(data.confidence_score);

    // Display answer
    displayAnswer(data.answer);

    // Display retrieved articles
    displayArticles(data.retrieved_articles);

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Display confidence score
function displayConfidence(score) {
    const percentage = Math.round(score * 100);
    confidenceValue.textContent = `${percentage}%`;
    confidenceFill.style.width = `${percentage}%`;

    // Update description based on confidence level
    if (score >= 0.8) {
        confidenceDescription.textContent = 'High confidence - The retrieved information is highly relevant to your query.';
        confidenceDescription.style.color = '#4ade80';
    } else if (score >= 0.5) {
        confidenceDescription.textContent = 'Medium confidence - The information may be partially relevant. Review the articles for details.';
        confidenceDescription.style.color = '#fbbf24';
    } else {
        confidenceDescription.textContent = 'Low confidence - Limited relevant information found. Try rephrasing your query.';
        confidenceDescription.style.color = '#f87171';
    }
}

// Display answer
function displayAnswer(answer) {
    // Format the answer with proper line breaks
    const formattedAnswer = answer.replace(/\n/g, '<br>');
    answerContent.innerHTML = formattedAnswer;
}

// Display retrieved articles
function displayArticles(articles) {
    articleCount.textContent = `${articles.length} article${articles.length !== 1 ? 's' : ''}`;

    // Clear existing articles
    articlesGrid.innerHTML = '';

    // Create article cards
    articles.forEach(article => {
        const card = createArticleCard(article);
        articlesGrid.appendChild(card);
    });
}

// Create article card element
function createArticleCard(article) {
    const card = document.createElement('div');
    card.className = 'article-card';

    // Rank badge
    const rank = document.createElement('div');
    rank.className = 'article-rank';
    rank.textContent = article.rank;

    // Title
    const title = document.createElement('h4');
    title.className = 'article-title';
    title.textContent = article.title;

    // Meta information (category and tags)
    const meta = document.createElement('div');
    meta.className = 'article-meta';

    const category = document.createElement('span');
    category.className = 'article-category';
    category.textContent = article.category;
    meta.appendChild(category);

    // Add first 2 tags
    article.tags.slice(0, 2).forEach(tag => {
        const tagEl = document.createElement('span');
        tagEl.className = 'article-tag';
        tagEl.textContent = tag;
        meta.appendChild(tagEl);
    });

    // Content preview
    const preview = document.createElement('p');
    preview.className = 'article-preview';
    preview.textContent = article.content_preview;

    // Similarity score
    const scoreContainer = document.createElement('div');
    scoreContainer.className = 'article-score';

    const scoreLabel = document.createElement('span');
    scoreLabel.className = 'score-label';
    scoreLabel.textContent = 'Relevance Score';

    const scoreValue = document.createElement('span');
    scoreValue.className = 'score-value';
    scoreValue.textContent = (article.similarity_score * 100).toFixed(1) + '%';

    scoreContainer.appendChild(scoreLabel);
    scoreContainer.appendChild(scoreValue);

    // Assemble card
    card.appendChild(rank);
    card.appendChild(title);
    card.appendChild(meta);
    card.appendChild(preview);
    card.appendChild(scoreContainer);

    return card;
}

// Check backend health on page load
async function checkBackendHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/health`);
        const data = await response.json();

        if (!data.rag_engine_initialized) {
            console.warn('RAG engine not initialized');
        }

        if (!data.openai_configured) {
            console.warn('OpenAI API key not configured - answer generation may be limited');
        }

        console.log('Backend health check:', data);
    } catch (error) {
        console.error('Backend health check failed:', error);
        console.warn('Make sure the backend server is running on http://localhost:8000');
    }
}

// Initialize
checkBackendHealth();
