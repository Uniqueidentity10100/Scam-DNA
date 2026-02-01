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
        document.getElementById('dnaCode').textContent = result.dna_code || 'N/A';

        // Display category
        const categoryEl = document.getElementById('category');
        const category = result.category || 'Unknown';
        categoryEl.textContent = category.replace(/_/g, ' ').toUpperCase();
        categoryEl.className = `category-badge category-${category.toLowerCase().replace(/ /g, '-')}`;

        // Display mutation info
        const mutationType = result.mutation_type || 'original';
        const mutationScore = result.mutation_score || 0;
        
        document.getElementById('mutationType').textContent = 
            mutationType.replace(/_/g, ' ').toUpperCase();
        document.getElementById('mutationScore').textContent = 
            `Mutation Score: ${(mutationScore * 100).toFixed(1)}%`;

        // Display signals - handle both direct array and object format
        const signals = result.signals || {};
        displaySignals('emotionalSignals', signals.emotional || []);
        displaySignals('structuralMarkers', signals.structural || []);
        displaySignals('linguisticPatterns', signals.linguistic || []);

        // Display family info
        const familyInfo = document.getElementById('familyInfo');
        const familyId = result.family_id || 'Unknown';
        familyInfo.innerHTML = `
            This message has been assigned to <strong>Family #${familyId}</strong>.
            <br>
            Classification: <strong>${mutationType.replace(/_/g, ' ')}</strong>
            ${mutationType !== 'original' ? 
                `(${(mutationScore * 100).toFixed(1)}% different from parent)` : 
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
