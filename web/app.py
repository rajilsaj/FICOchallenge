from flask import Flask, render_template, request, session, redirect, url_for, jsonify, send_file
import pandas as pd
import numpy as np
import time
import os
import io

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_synthetic_platform'

# Ensure data directory exists
os.makedirs('data', exist_ok=True)
DATA_FILE = 'data/synthetic_dataset.csv'

def get_generated_df():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return None

def save_generated_df(df):
    df.to_csv(DATA_FILE, index=False)

@app.route('/')
def dashboard():
    df = get_generated_df()
    num_rows = len(df) if df is not None else 0
    return render_template('dashboard.html', active_page='dashboard', num_rows=num_rows)

@app.route('/generation', methods=['GET', 'POST'])
def generation():
    df = get_generated_df()
    preview_data = df.head().to_dict(orient='records') if df is not None else None
    columns = df.columns.tolist() if df is not None else []
    
    return render_template('generation.html', active_page='generation', 
                           preview_data=preview_data, columns=columns)

@app.route('/api/generate', methods=['POST'])
def api_generate():
    data = request.json
    model = data.get('model', 'Llama 3.1 (Unsloth)')
    temperature = float(data.get('temperature', 0.7))
    num_scenarios = int(data.get('num_scenarios', 5))
    num_variants = int(data.get('num_variants', 5))
    
    # Simulate generation delay
    time.sleep(3)
    
    df = pd.DataFrame({
        "intent": ["PAYMENT"] * num_scenarios,
        "scenario": [f"Scenario {i+1} using {model}" for i in range(num_scenarios)],
        "temperature": temperature,
        "variants": num_variants
    })
    
    save_generated_df(df)
    return jsonify({"status": "success"})

@app.route('/api/upload', methods=['POST'])
def api_upload():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"}), 400
    
    if file and file.filename.endswith('.csv'):
        # Simulate upload delay
        time.sleep(1)
        df = pd.read_csv(file)
        save_generated_df(df)
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Invalid file format"}), 400

@app.route('/download')
def download():
    if os.path.exists(DATA_FILE):
        return send_file(DATA_FILE, as_attachment=True, download_name='synthetic_dataset.csv', mimetype='text/csv')
    return "No dataset generated", 404

@app.route('/test-set', methods=['GET', 'POST'])
def test_set():
    return render_template('test_set.html', active_page='test_set')

@app.route('/api/evaluate', methods=['POST'])
def api_evaluate():
    # Simulate evaluate delay
    time.sleep(3)
    return jsonify({"status": "success", "accuracy": "89%", "f1_score": "0.87"})

@app.route('/training', methods=['GET', 'POST'])
def training():
    return render_template('training.html', active_page='training')

@app.route('/api/train', methods=['POST'])
def api_train():
    data = request.json
    epochs = int(data.get('epochs', 3))
    # We will just simulate it in frontend through multiple requests or just wait
    return jsonify({"status": "success", "epochs": epochs})

@app.route('/fine-tuning')
def fine_tuning():
    return render_template('fine_tuning.html', active_page='fine_tuning')

@app.route('/api/finetune', methods=['POST'])
def api_finetune():
    time.sleep(2)
    return jsonify({"status": "success"})

@app.route('/reports')
def reports():
    # Generate random data for reports
    chart_data = pd.DataFrame(
        np.random.randn(20, 3),
        columns=["Precision", "Recall", "F1"]
    )
    data_dict = chart_data.to_dict(orient='list')
    return render_template('reports.html', active_page='reports', chart_data=data_dict)

@app.route('/projects')
def projects():
    return render_template('projects.html', active_page='projects')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
