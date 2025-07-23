from flask import Flask, render_template

app = Flask(__name__, static_folder='static', template_folder='templates')

@app.route('/')
def home():
    return render_template('dashboard.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/clips')
def clips():
    return render_template('clips.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/health')
def health():
    return {'status': 'healthy', 'timestamp': '2025-07-23'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
