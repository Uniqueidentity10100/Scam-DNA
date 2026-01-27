/**
 * Analyzer page functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('analyzerForm');
    const messageInput = document.getElementById('messageInput');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const resultsSection = document.getElementById('resultsSection');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const text = messageInput.value.trim();
        
        if (text.length < 10) {
            showNotification('Message is too short for meaningful analysis', 'error');
            return;
        }

        // Show loading state
        analyzeBtn.disabled = true;
        analyzeBtn.querySelector('.btn-text').style.display = 'none';
        analyzeBtn.querySelector('.btn-loading').style.display = 'inline';

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: text })
            });

            const data = await response.json();

            if (data.success) {
                displayResults(data.result);
                showNotification('Analysis complete!', 'success');
            } else {
                showNotification(data.error || 'Analysis failed', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            showNotification('Network error occurred', 'error');
        } finally {
            // Reset button state
            analyzeBtn.disabled = false;
            analyzeBtn.querySelector('.btn-text').style.display = 'inline';
            analyzeBtn.querySelector('.btn-loading').style.display = 'none';
        }
    });

    function displayResults(result) {
        // Show results section
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth' });

        // Display DNA code
        document.getElementById('dnaCode').textContent = result.dna_code;

        // Display category
        const categoryEl = document.getElementById('category');
        categoryEl.textContent = result.category.replace(/_/g, ' ').toUpperCase();
        categoryEl.className = `category-badge category-${result.category}`;

        // Display mutation info
        document.getElementById('mutationType').textContent = 
            result.mutation_type.replace(/_/g, ' ').toUpperCase();
        document.getElementById('mutationScore').textContent = 
            `Mutation Score: ${result.mutation_score}`;

        // Display signals
        displaySignals('emotionalSignals', result.signals.emotional);
        displaySignals('structuralMarkers', result.signals.structural);
        displaySignals('linguisticPatterns', result.signals.linguistic);

        // Display family info
        const familyInfo = document.getElementById('familyInfo');
        familyInfo.innerHTML = `
            This message has been assigned to <strong>Family #${result.family_id}</strong>.
            <br>
            Classification: <strong>${result.mutation_type.replace(/_/g, ' ')}</strong>
            ${result.mutation_type !== 'original' ? 
                `(${(result.mutation_score * 100).toFixed(1)}% different from parent)` : 
                '(New family lineage)'}
        `;
    }

    function displaySignals(elementId, signals) {
        const list = document.getElementById(elementId);
        list.innerHTML = '';
        
        if (signals && signals.length > 0) {
            signals.forEach(signal => {
                const li = document.createElement('li');
                li.textContent = signal.replace(/_/g, ' ');
                list.appendChild(li);
            });
        } else {
            const li = document.createElement('li');
            li.textContent = 'None detected';
            li.style.color = 'var(--text-muted)';
            list.appendChild(li);
        }
    }
});
