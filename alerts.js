// Show popup alert
function showAlert(message, isError = true) {
    const indicator = document.getElementById('alertIndicator');
    indicator.textContent = message;
    indicator.className = `alert-indicator ${isError ? 'error' : 'success'}`;
    
    // Auto-hide after 3 seconds
    setTimeout(() => {
        indicator.style.display = 'none';
    }, 3000);
}

// Add log entry (only for errors)
function addLogEntry(message, type = 'error') {
    const logEntries = document.getElementById('logEntries');
    const timestamp = new Date().toLocaleTimeString();
    
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    entry.innerHTML = `<strong>[${timestamp}]</strong> ${message}`;
    
    logEntries.prepend(entry);
    
    // Keep log to a reasonable size
    if (logEntries.children.length > 50) {
        logEntries.removeChild(logEntries.lastChild);
    }
}