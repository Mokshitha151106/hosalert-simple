from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>HOSALERT - Coming Soon</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
                padding: 50px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            h1 { font-size: 48px; }
            p { font-size: 20px; }
            .success { background: #4CAF50; padding: 10px; border-radius: 5px; display: inline-block; }
        </style>
    </head>
    <body>
        <h1>🚀 HOSALERT</h1>
        <p>Patient Medication Alert System</p>
        <div class="success">✅ Server is running successfully!</div>
        <p>Full version coming soon with Voice Alerts, Offline Sync, and Real-time Notifications.</p>
        <p><small>Deployed on Render</small></p>
    </body>
    </html>
    '''

@app.route('/test')
def test():
    return 'HOSALERT API is working!'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
