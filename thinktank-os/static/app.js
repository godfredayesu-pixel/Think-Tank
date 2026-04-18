// Think Tank OS - Frontend Logic

let queue = [];
let isRunning = false;

// Check API health on load
async function checkStatus() {
    try {
        const resp = await fetch('/api/health');
        const data = await resp.json();
        const badge = document.getElementById('statusBadge');
        
        if (data.status === 'online' && data.has_api_key) {
            badge.textContent = `✅ Online (${data.model})`;
            badge.className = 'status-badge status-online';
        } else if (data.status === 'online') {
            badge.textContent = '⚠️ Missing API Key';
            badge.className = 'status-badge status-offline';
        } else {
            badge.textContent = '❌ Offline';
            badge.className = 'status-badge status-offline';
        }
    } catch (err) {
        document.getElementById('statusBadge').textContent = '❌ Cannot connect';
        document.getElementById('statusBadge').className = 'status-badge status-offline';
    }
}

// Tab switching
function switchTab(tab) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    
    if (tab === 'url') {
        document.querySelector('.tab:first-child').classList.add('active');
        document.getElementById('urlTab').classList.add('active');
    } else {
        document.querySelector('.tab:last-child').classList.add('active');
        document.getElementById('uploadTab').classList.add('active');
    }
}

// Add URLs to queue
function addFromURL() {
    const textarea = document.getElementById('urlInput');
    const urls = textarea.value.trim().split('\n').filter(u => u.trim());
    
    if (urls.length === 0) {
        alert('Please enter at least one URL');
        return;
    }
    
    urls.forEach(url => {
        const trimmed = url.trim();
        if (trimmed.startsWith('http')) {
            queue.push({
                type: 'url',
                source: trimmed,
                label: extractLabel(trimmed),
                status: 'waiting',
                result: null,
                error: null
            });
        }
    });
    
    textarea.value = '';
    refreshQueueUI();
}

// Add files to queue
function addFromFiles() {
    const input = document.getElementById('fileInput');
    const files = input.files;
    
    if (files.length === 0) {
        alert('Please select at least one PDF file');
        return;
    }
    
    Array.from(files).forEach(file => {
        queue.push({
            type: 'file',
            source: file,
            label: file.name,
            status: 'waiting',
            result: null,
            error: null
        });
    });
    
    input.value = '';
    refreshQueueUI();
}

// Extract label from URL
function extractLabel(url) {
    try {
        const u = new URL(url);
        const parts = u.pathname.split('/').filter(p => p);
        return parts[parts.length - 1] || u.hostname;
    } catch {
        return url.substring(0, 50);
    }
}

// Refresh queue UI
function refreshQueueUI() {
    const list = document.getElementById('queueList');
    const count = document.getElementById('queueCount');
    
    count.textContent = `${queue.length} item${queue.length !== 1 ? 's' : ''}`;
    
    list.innerHTML = '';
    queue.forEach((item, idx) => {
        const li = document.createElement('li');
        li.className = `queue-item ${item.status}`;
        
        const icon = item.type === 'file' ? '📁' : '🔗';
        const statusText = {
            waiting: '⏳ Waiting',
            running: '🔄 Analyzing',
            done: '✅ Done',
            error: '❌ Error'
        }[item.status];
        
        li.innerHTML = `
            <span>${icon} [${statusText}] ${item.label}</span>
            <button class="queue-item-remove" onclick="removeFromQueue(${idx})">×</button>
        `;
        
        if (item.status === 'done') {
            li.style.cursor = 'pointer';
            li.onclick = () => showResult(item);
        }
        
        list.appendChild(li);
    });
}

// Remove from queue
function removeFromQueue(idx) {
    if (queue[idx].status === 'running') return;
    queue.splice(idx, 1);
    refreshQueueUI();
}

// Clear entire queue
function clearQueue() {
    if (isRunning) {
        alert('Analysis in progress. Please wait.');
        return;
    }
    queue = [];
    refreshQueueUI();
}

// Run all analyses
async function runAll() {
    const waiting = queue.filter(item => item.status === 'waiting');
    
    if (waiting.length === 0) {
        alert('No items to analyze. Add some URLs or files first.');
        return;
    }
    
    if (isRunning) {
        alert('Analysis already in progress.');
        return;
    }
    
    isRunning = true;
    
    for (let i = 0; i < queue.length; i++) {
        if (queue[i].status !== 'waiting') continue;
        
        queue[i].status = 'running';
        refreshQueueUI();
        
        try {
            const result = await analyzeItem(queue[i]);
            queue[i].result = result.insights;
            queue[i].status = 'done';
            showResult(queue[i]);
        } catch (err) {
            queue[i].error = err.message;
            queue[i].status = 'error';
            console.error('Analysis error:', err);
        }
        
        refreshQueueUI();
    }
    
    isRunning = false;
    alert('All analyses complete!');
}

// Analyze single item
async function analyzeItem(item) {
    if (item.type === 'url') {
        const resp = await fetch('/api/analyze', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({url: item.source})
        });
        
        if (!resp.ok) {
            const err = await resp.json();
            throw new Error(err.error || 'Analysis failed');
        }
        
        return await resp.json();
    } else {
        const formData = new FormData();
        formData.append('file', item.source);
        
        const resp = await fetch('/api/analyze', {
            method: 'POST',
            body: formData
        });
        
        if (!resp.ok) {
            const err = await resp.json();
            throw new Error(err.error || 'Analysis failed');
        }
        
        return await resp.json();
    }
}

// Show result
function showResult(item) {
    const content = document.getElementById('resultsContent');
    const title = document.getElementById('resultsTitle');
    const copyBtn = document.getElementById('copyBtn');
    
    title.textContent = `📊 ${item.label}`;
    copyBtn.style.display = 'inline-block';
    
    if (item.result) {
        // Parse opportunities
        const opps = parseOpportunities(item.result);
        let html = '';
        
        opps.forEach((opp, idx) => {
            html += `
                <div class="opportunity">
                    <h4>💡 Opportunity ${idx + 1}</h4>
                    <div>${opp.replace(/\n/g, '<br>')}</div>
                </div>
            `;
        });
        
        content.innerHTML = html || `<pre>${item.result}</pre>`;
    } else if (item.error) {
        content.innerHTML = `<div class="opportunity" style="border-left-color:#e74c3c">
            <h4>❌ Error</h4>
            <p>${item.error}</p>
        </div>`;
    }
}

// Parse opportunities from AI response
function parseOpportunities(text) {
    const parts = text.split(/---OPPORTUNITY\s*\d+---/i);
    const opps = parts.slice(1).map(p => p.replace(/---END---/gi, '').trim());
    return opps.length > 0 ? opps : [text];
}

// Copy results
function copyResults() {
    const content = document.getElementById('resultsContent').innerText;
    navigator.clipboard.writeText(content).then(() => {
        alert('✅ Results copied to clipboard!');
    });
}

// Initialize
checkStatus();
setInterval(checkStatus, 30000); // Check every 30 sec
