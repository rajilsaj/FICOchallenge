from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pipeline import generate_synthetic_data, prepare_data, train_classifier, classify_intent
import os

app = Flask(__name__, static_folder='frontend', static_url_path='')
# Enable CORS for all routes so the frontend can easily communicate with it
CORS(app)

@app.route('/')
def index():
    """Route to serve the frontend's index.html."""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/generate', methods=['POST'])
def api_generate():
    """Endpoint for generating synthetic scenarios."""
    data = request.json or {}
    intent = data.get('intent', 'balance_inquiry')
    seed = data.get('seed', 'default')
    temp = data.get('temperature', 0.7)
    num = data.get('num_scenarios', 5)
    
    scenarios = generate_synthetic_data(intent, seed, temp, num)
    
    return jsonify({
        "status": "success",
        "scenarios": scenarios
    })

@app.route('/api/prepare', methods=['POST'])
def api_prepare():
    """Endpoint for preparing and splitting dataset."""
    data = request.json or {}
    split = data.get('split_ratio', 80)
    
    result = prepare_data(split)
    return jsonify(result)

@app.route('/api/train', methods=['POST'])
def api_train():
    """Endpoint to trigger fine-tuning training."""
    data = request.json or {}
    model_type = data.get('model_type', 'bert')
    epochs = data.get('epochs', 3)
    
    result = train_classifier(model_type, epochs)
    return jsonify(result)

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """Endpoint to pass text to the trained model and get intent."""
    data = request.json or {}
    text = data.get('text', '')
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
        
    result = classify_intent(text)
    return jsonify(result)

if __name__ == '__main__':
    # Run the application in debug mode for development
    app.run(debug=True, port=5000)
