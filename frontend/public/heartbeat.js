// Server heartbeat and connection monitor
(function() {
    // Configuration
    const HEARTBEAT_INTERVAL = 30000; // 30 seconds
    
    // Try to get API URL from window.ENV if it exists (set by Next.js)
    const API_URL = (window.ENV && window.ENV.NEXT_PUBLIC_API_URL) || 'http://localhost:8000/api';
    
    // Send heartbeat to server
    function sendHeartbeat() {
        fetch(`${API_URL}/monitor/heartbeat`, { 
            method: 'GET',
            headers: { 'Cache-Control': 'no-cache' }
        }).catch(err => {
            console.log('Heartbeat error:', err);
        });
    }
    
    // Send shutdown signal to server
    function sendShutdown() {
        fetch(`${API_URL}/monitor/shutdown`, { 
            method: 'GET',
            headers: { 'Cache-Control': 'no-cache' }
        }).catch(err => {
            console.log('Shutdown request error:', err);
        });
    }
    
    // Setup periodic heartbeat
    const heartbeatInterval = setInterval(sendHeartbeat, HEARTBEAT_INTERVAL);
    
    // Initial heartbeat
    sendHeartbeat();
    
    // Setup window close handler
    window.addEventListener('beforeunload', function() {
        clearInterval(heartbeatInterval);
        sendShutdown();
    });
})();
